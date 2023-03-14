from concurrent.futures import ProcessPoolExecutor, as_completed
from utils import save_df_to_parquet, backup_result_to_pkl
from components import scraping, modeling
from typing import List, Tuple, Dict
from itertools import chain
from configs import Deployment
from ast import literal_eval
import pandas as pd
import os
import psutil
import numpy as np
from datetime import date


def concat_lib_book_data_to_df(updated_lib_book_data: List[Tuple[str, map]]) -> pd.DataFrame:
    """정보나루 API에서 받은 데이터를 하나의 df로 통합"""
    result = []
    for lib_code, map_file in updated_lib_book_data:
        data = pd.DataFrame(list(map_file))
        data["lib_code"] = lib_code
        result.append(data)

    return pd.concat(result)


def save_lib_books(concated_lib_book_data: pd.DataFrame, lib_dict) -> None:
    """도서관에서 받은 데이터 중 도서관 별 장서 데이터만 저장"""
    lib_book = concated_lib_book_data[["isbn13", "lib_code"]]
    lib_book["lib_code"] = lib_book["lib_code"].apply(lambda x: lib_dict[x])
    save_df_to_parquet(lib_book, "data/update/lib_books.parquet")


def save_book_info(concated_lib_book_data: pd.DataFrame) -> None:
    """도서관에서 받은 데이터 중 도서 정보만 저장"""
    book_info = concated_lib_book_data.drop(columns=["lib_code"]).drop_duplicates(subset="isbn13")
    save_df_to_parquet(book_info, "data/update/book_info.parquet")


def scrap_book_info_from_kyobo(isbns: List[str]) -> list:
    """멀티프로세스를 사용해 도서 정보 수집(개별 함수는 asyncio로 동작)"""
    executor = ProcessPoolExecutor()

    num_cpus = os.cpu_count()
    chunk = min(max(int(len(isbns) / num_cpus), 1), 10)
    print("chunk", chunk)

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
            print(f"진행상태 : {i}/{len(futures)}")

    return list(map(literal_eval, stringified_result))


def convert_result_to_df(result: List) -> pd.DataFrame:
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


def save_data_for_search(df: pd.DataFrame, dir: str) -> None:
    """키워드 검색용 데이터 저장"""
    isbn_list = df["isbn13"].values
    book_keyword = np.row_stack(list(map(_fill_None, df.keyword.values)))
    backup_result_to_pkl([isbn_list, book_keyword], dir)


def _fill_None(lst: List) -> np.array:
    """추출 키워드가 20개 미만인 경우 pad 생성"""
    pad_length = 20 - len(lst)
    return np.pad(np.array(lst), (0, pad_length), "constant", constant_values=("None"))


from transformers.utils import logging

# transformers warning 제거
logging.set_verbosity(40)
key = modeling.keywordExtractor(dir="data/preprocess/eng_han.csv")


def extract_keywords_using_mutiprocess(docs: pd.DataFrame) -> List[Dict]:
    """멀티프로세싱을 활용해 장서별 키워드 추출"""
    num_cpus = os.cpu_count()
    chunk = min(max(int(len(docs) / num_cpus), 1), 10)

    if int(len(docs) / num_cpus) == 0:
        max_worker = len(docs)
    else:
        max_worker = num_cpus - 3

    executor = ProcessPoolExecutor(max_worker)

    futures = []
    for i in range(0, len(docs), chunk):
        tasks = docs.iloc[i : i + chunk]
        future = executor.submit(_create_job, tasks)
        futures.append(future)

    print("len_docs : ", len(docs))
    print("chunk : ", chunk)
    print("futues : ", len(futures))

    stringified_result = []
    for i, future in enumerate(as_completed(futures)):
        result = future.result()
        stringified_result.append(result)
        if i % 20 == 0 and i != 0:
            print(f"진행상태 : {i}/{len(futures)}")

    return list(map(literal_eval, stringified_result))


def _create_job(df: pd.DataFrame) -> str:
    """멀티프로세싱 잡 생성"""
    return str(key.extract_keyword(df))


def concat_dict_list_to_df(dict_list: List[Dict]) -> pd.DataFrame:
    """장서별 추출 데이터를 하나의 df로 통합"""
    isbn_list = []
    keyword_list = []
    for dct in dict_list:
        isbn_list.extend(dct["isbn13"])
        keyword_list.extend(dct["keywords"])
    return pd.DataFrame(dict(isbn13=isbn_list, keyword=keyword_list))


if __name__ == "__main__":
    dep = Deployment()
    date_now = date.today()

    print("<----update books from libraries---->")
    updated_lib_book_data: list[tuple[str, map]] = scraping.update_lib_book_data(
        dep.lib_codes.keys()
    )
    concated_lib_book_data = concat_lib_book_data_to_df(updated_lib_book_data)

    print("<----save book_info---->")
    save_lib_books(concated_lib_book_data, dep.lib_codes)
    save_book_info(concated_lib_book_data)

    print("<----scrap book_info from kyobo---->")
    isbns = concated_lib_book_data["isbn13"].drop_duplicates().tolist()
    scraping_result = scrap_book_info_from_kyobo(isbns)
    scraping_df = convert_result_to_df(scraping_result)
    save_df_to_parquet(scraping_df, f"data/local_data/{date_now}_scraping_result.parquet")

    print("<----extract keywords using book_info---->")
    dict_list: List[Dict] = extract_keywords_using_mutiprocess(scraping_df)
    result_df = concat_dict_list_to_df(dict_list)
    save_df_to_parquet(result_df, f"data/update/{date_now}_extracted_keywords.parquet")
    save_data_for_search(result_df, f"data/update/{date_now}_data_for_search")

    print("<----update w2v_data---->")
    origin_data = pd.read_parquet("data/local_data/w2v_data.parquet")
    merged_data = pd.concat([origin_data, scraping_df]).drop_duplicates(subset="isbn13")
    save_df_to_parquet(origin_data, f"data/local_data/backup/w2v_data.parquet")
    save_df_to_parquet(merged_data, f"data/local_data/w2v_data.parquet")

    print("<----train W2V Model---->")
    w2v = modeling.W2VTrainer(dir="data/preprocess/eng_han.csv")
    w2v.train_and_save(merged_data, f"data/update/{date_now}_w2v")
