from concurrent.futures import ProcessPoolExecutor, as_completed
from components import scraping, modeling
from typing import List, Tuple, Dict
from logs.utils import make_logger
from ast import literal_eval
from itertools import chain
from datetime import date
import transformers.utils
import pandas as pd
import numpy as np
import configs
import pickle
import os


class BookPipe:
    """
    데이터 수집, 정제, 모델 학습을 수행하는 파이프라인 입니다.
    """

    def __init__(self) -> None:
        transformers.utils.logging.set_verbosity(40)
        self.key = modeling.keywordExtractor(dir="data/preprocess/eng_han.csv")
        self.w2v = modeling.W2VTrainer(dir="data/preprocess/eng_han.csv")
        self.dep = configs.Deployment()
        self.date_now = date.today()
        self.logging = make_logger("logs/pipeline.log", "pipeline")
        self.logging.info("Complete Loading BookPipe")

    def update_books_from_libray(self) -> pd.DataFrame:
        """정보나루 API에서 매월 업데이트 되는 도서 정보 확보"""
        self.logging.info("<----update books from libraries---->")
        updated_lib_book_data: list[tuple[str, map]] = scraping.update_lib_book_data(
            self.dep.lib_codes.keys()
        )

        self.logging.info("<----save book_info---->")
        concated_lib_book_df = self._concat_lib_book_data_to_df(updated_lib_book_data)
        self._save_lib_books(concated_lib_book_df, self.dep.lib_codes)
        self._save_book_info(concated_lib_book_df)
        return concated_lib_book_df

    def _concat_lib_book_data_to_df(
        self, updated_lib_book_data: List[Tuple[str, map]]
    ) -> pd.DataFrame:
        """정보나루 API에서 받은 데이터를 하나의 df로 통합"""

        result = []
        for lib_code, map_file in updated_lib_book_data:
            data = pd.DataFrame(list(map_file))
            data["lib_code"] = lib_code
            result.append(data)

        return pd.concat(result)

    def _save_lib_books(self, concated_lib_book_data: pd.DataFrame, lib_dict) -> None:
        """정보나루 API에서 받은 데이터 중 도서관 별 장서 데이터만 저장"""
        lib_book = concated_lib_book_data[["isbn13", "lib_code"]]
        # libe_code to lib_name 111003: "강남"
        lib_book["lib_code"] = lib_book["lib_code"].apply(lambda x: lib_dict[x])
        lib_book.columns = ["isbn13", "lib_name"]
        return self._save_df_to_parquet(lib_book, "data/update/lib_books.parquet")

    def _save_book_info(self, concated_lib_book_data: pd.DataFrame) -> None:
        """정보나루 API에서 받은 데이터 중 도서 정보만 저장"""
        book_info = concated_lib_book_data.drop(columns=["lib_code"]).drop_duplicates(
            subset="isbn13"
        )
        return self._save_df_to_parquet(book_info, "data/update/book_info.parquet")

    def _save_df_to_parquet(self, df: pd.DataFrame, dir: str = None) -> pd.DataFrame:
        if dir:
            df.to_parquet(f"{dir}")
            self.logging.info("saved results to parquet!")
            return None
        else:
            return df

    def scrap_book_info_from_kyobo(self, isbns: List) -> pd.DataFrame:
        """업데이트 된 도서 정보에 대해 데이터(도서 이미지, 목차, 저자소개, 출판사 설명) 수집"""
        self.logging.info("<----scrap book_info from kyobo---->")

        scraping_result = self._scrap_book_info_using_multiprocess(isbns)
        scraping_df = self._convert_result_to_df(scraping_result)
        self._save_df_to_parquet(
            scraping_df, f"data/local_data/{self.date_now}_scraping_result.parquet"
        )
        return scraping_df

    def _scrap_book_info_using_multiprocess(self, isbns: List[str]) -> List:
        """멀티프로세스를 사용해 도서 정보 수집(개별 함수는 asyncio로 동작)"""
        executor = ProcessPoolExecutor()

        num_cpus = os.cpu_count()
        chunk = min(max(int(len(isbns) / num_cpus), 1), 10)
        self.logging.info(f"scraping_chunk_size : {chunk}")

        futures = []
        for i in range(0, len(isbns), chunk):
            tasks = isbns[i : i + chunk]
            future = executor.submit(scraping.scrap_book_info_with_multiprocessing, tasks)
            futures.append(future)

        stringified_result = []
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            stringified_result.append(result)
            if i % 50 == 0 and i != 0:
                self.logging.info(f"진행상태 : {i}/{len(futures)}")

        return list(map(literal_eval, stringified_result))

    def _convert_result_to_df(self, result: List) -> pd.DataFrame:
        """result를 양식에 맞는 df로 변경"""
        scraping_list = list(chain(*result))

        df = pd.DataFrame(scraping_list).dropna(subset=[1]).reset_index(drop=True)
        df.columns = [
            "isbn13",
            "title",
            "toc",
            "intro",
            "publisher",
        ]
        return df

    def extract_keywords_using_book_info(self, scraping_df: pd.DataFrame) -> None:
        """수집한 데이터를 바탕으로 electra model을 활용해 도서 핵심 키워드 추출"""
        self.logging.info("<----extract keywords using book_info---->")

        dict_list: List[Dict] = self._extract_keywords_using_mutiprocess(scraping_df)
        result_df = self._concat_dict_list_to_df(dict_list)

        self.logging.info("<----save keywords extraction result---->")
        self._save_df_to_parquet(
            result_df, f"data/update/{self.date_now}_extracted_keywords.parquet"
        )
        self._save_data_for_search(result_df, f"data/update/{self.date_now}_data_for_search")
        return None

    def _extract_keywords_using_mutiprocess(self, docs: pd.DataFrame) -> List[Dict]:
        """멀티프로세싱을 활용해 장서별 키워드 추출"""

        num_cpus = os.cpu_count()
        chunk = 1
        if int(len(docs) / num_cpus) == 0:
            max_worker = len(docs)
        else:
            max_worker = num_cpus - 3

        executor = ProcessPoolExecutor(max_worker)

        futures = []
        for i in range(0, len(docs), chunk):
            tasks = docs.iloc[i : i + chunk]
            future = executor.submit(self._create_job, tasks)
            futures.append(future)

        self.logging.info(f"extracting_keyword_chunk_size : {chunk}")
        self.logging.info(
            f"num_of_docs : {len(docs)}",
        )
        self.logging.info(
            f"num_of_futures : {len(futures)}",
        )

        stringified_result = []
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            stringified_result.append(result)
            if i % 20 == 0 and i != 0:
                self.logging.info(f"진행상태 : {i}/{len(futures)}")

        return list(map(literal_eval, stringified_result))

    def _create_job(self, df: pd.DataFrame) -> str:
        """키워드 추출을 위한 멀티프로세싱 잡 생성"""
        return str(self.key.extract_keyword(df))

    def _concat_dict_list_to_df(self, dict_list: List[Dict]) -> pd.DataFrame:
        """장서별 추출 데이터를 하나의 df로 통합"""
        isbn_list = []
        keyword_list = []
        for dct in dict_list:
            isbn_list.extend(dct["isbn13"])
            keyword_list.extend(dct["keywords"])
        return pd.DataFrame(dict(isbn13=isbn_list, keyword=keyword_list))

    def _save_data_for_search(self, df: pd.DataFrame, dir: str) -> None:
        """키워드 검색용 데이터 저장"""
        isbn_list = df["isbn13"].values
        book_keyword = np.row_stack(list(map(self._fill_None, df.keyword.values)))
        self.backup_result_to_pkl([isbn_list, book_keyword], dir)

    def backup_result_to_pkl(self, item, dir: str = "back_up_file"):
        # store list in binary file so 'wb' mode
        with open(f"{dir}", "wb") as fp:
            pickle.dump(item, fp)
            print("Done writing list into a binary file")

    def _fill_None(self, lst: List) -> np.array:
        """추출 키워드가 20개 미만인 경우 pad 생성"""
        pad_length = 20 - len(lst)
        return np.pad(np.array(lst), (0, pad_length), "constant", constant_values=("None"))

    def update_w2v_data(self, scraping_df: pd.DataFrame):
        """학습에 활용될 데이터 생성 및 word2vec 학습"""
        self.logging.info("<----update w2v_data---->")
        origin_data = pd.read_parquet("data/local_data/w2v_data.parquet")
        merged_data = pd.concat([origin_data, scraping_df]).drop_duplicates(subset="isbn13")

        self.logging.info("<----save w2v_data---->")
        self._save_df_to_parquet(origin_data, f"data/local_data/backup/w2v_data.parquet")
        self._save_df_to_parquet(merged_data, f"data/local_data/w2v_data.parquet")
        return merged_data

    def train_w2v(self, w2v_data: pd.DataFrame):
        self.logging.info("<----train W2V Model---->")
        return self.w2v.train_and_save(w2v_data, f"data/update/{self.date_now}_w2v")
