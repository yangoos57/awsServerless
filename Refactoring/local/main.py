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


def concat_lib_book_data_to_df(updated_lib_book_data: List[Tuple[str, map]]) -> pd.DataFrame:
    result = []
    for lib_code, map_file in updated_lib_book_data:
        data = pd.DataFrame(list(map_file))
        data["lib_code"] = lib_code
        result.append(data)

    return pd.concat(result)


def save_lib_book(concated_lib_book_data: pd.DataFrame) -> None:
    lib_book = concated_lib_book_data[["isbn13", "lib_code"]]
    save_df_to_parquet(lib_book, "data/update/lib_book.parquet")


def save_book_info(concated_lib_book_data: pd.DataFrame) -> None:
    book_info = concated_lib_book_data.drop(columns=["lib_code"]).drop_duplicates(subset="isbn13")
    save_df_to_parquet(book_info, "data/update/book_info.parquet")


def scrap_book_info_from_kyobo(isbns: List[str]) -> list:
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


from transformers.utils import logging

# transformers warning 제거
logging.set_verbosity(40)

key = modeling.keywordExtractor(dir="data/preprocess/eng_han.csv")


def create_job(df: pd.DataFrame) -> str:
    return str(key.extract_keyword(df))


def extract_keywords_using_mutiprocess(docs: pd.DataFrame) -> List[Dict]:
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
        future = executor.submit(create_job, tasks)
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


def covnert_dict_list_to_df(dict_list: List[Dict]) -> pd.DataFrame:
    isbn_list = []
    keyword_list = []
    for dct in dict_list:
        isbn_list.extend(dct["isbn13"])
        keyword_list.extend(dct["keywords"])
    return pd.DataFrame(dict(isbn13=isbn_list, keyword=keyword_list))


if __name__ == "__main__":
    dep = Deployment()

    # print("<----update books from libraries---->")
    # updated_lib_book_data: list[tuple[str, map]] = scraping.update_lib_book_data(dep.lib_codes[:2])
    # concated_lib_book_data = concat_lib_book_data_to_df(updated_lib_book_data)

    # print("<----save book_info---->")
    # save_book_info(concated_lib_book_data)
    # save_lib_book(concated_lib_book_data)

    # print("<----scrap book_info from kyobo---->")
    # isbns = concated_lib_book_data["isbn13"].drop_duplicates().tolist()
    # scraping_result = scrap_book_info_from_kyobo(isbns)
    # scraping_df = convert_result_to_df(scraping_result)
    # save_df_to_parquet(scraping_df, "data/update/scraping_result.parquet")

    scraping_df = pd.read_parquet("data/w2v_data.parquet")

    print("<----extract keywords using book_info---->")
    dict_list: List[Dict] = extract_keywords_using_mutiprocess(scraping_df)
    result_df = covnert_dict_list_to_df(dict_list)
    save_df_to_parquet(result_df, "data/update/extracted_keywords.parquet")

    # print("<----update w2v_data---->")
    # origin_data = pd.read_parquet("data/w2v_data.parquet")
    # merged_data = pd.concat([origin_data, scraping_df]).drop_duplicates(subset="isbn13")
    # save_df_to_parquet(merged_data, "data/w2v_data_check.parquet")

    # print("<----train W2V Model---->")
    # w2v = modeling.W2VTrainer(dir="data/preprocess/eng_han.csv")
    # w2v.train_and_save(merged_data, "data/update/w2v")
