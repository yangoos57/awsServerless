import pickle
from itertools import chain
import pandas as pd


def save_df_to_parquet(df: pd.DataFrame, dir: str = None) -> pd.DataFrame:
    if dir:
        df.to_parquet(f"{dir}")
        print("saved results to parquet!")
        return None
    else:
        return df


def backup_result_to_pkl(item, dir: str = "back_up_file"):
    # store list in binary file so 'wb' mode
    with open(f"{dir}", "wb") as fp:
        pickle.dump(item, fp)
        print("Done writing list into a binary file")


def read_pkl(dir: str) -> list:
    # for reading also binary mode is important
    with open(dir, "rb") as fp:
        n_list = pickle.load(fp)
        return n_list
