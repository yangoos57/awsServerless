import pickle
from ast import literal_eval
from itertools import chain
import pandas as pd


def save_result_to_df(scraping_result: list, dir: str = None) -> pd.DataFrame:
    scraping_str_map = map(literal_eval, scraping_result)
    scraping_list = list(chain(*scraping_str_map))

    df = pd.DataFrame(scraping_list).dropna(subset=[1]).reset_index(drop=True)
    df.columns = [
        "isbn13",
        "title",
        "toc",
        "intro",
        "publisher",
    ]

    if dir:
        df.to_parquet(f"{dir}/book_scraping.parquet")
        print("saved results to parquet!")
        return None
    else:
        return df


def backup_list_to_pkl(names: str, dir: str = None):
    # store list in binary file so 'wb' mode
    with open(f"{dir}scraping_backup_file", "wb") as fp:
        pickle.dump(names, fp)
        print("Done writing list into a binary file")


def read_pkl(dir: str) -> list:
    # for reading also binary mode is important
    with open(dir, "rb") as fp:
        n_list = pickle.load(fp)
        return n_list
