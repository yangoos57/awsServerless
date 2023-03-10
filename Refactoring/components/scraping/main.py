from scraping import scrap_book_info_with_multiprocessing
from utils import backup_list_to_pkl, save_result_to_df
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd

if __name__ == "__main__":

    # load ISBNs
    df = pd.read_parquet("../../App/db/data/book_info.parquet")
    isbns = df["ISBN"].tolist()

    # create poolexecutor
    executor = ProcessPoolExecutor()

    # create futures
    chunk = 10
    futures = []
    for i in range(0, len(isbns), chunk):
        tasks = isbns[i : i + chunk]
        future = executor.submit(scrap_book_info_with_multiprocessing, tasks)
        futures.append(future)

    # process futures
    results = []
    for i, future in enumerate(as_completed(futures)):
        result = future.result()
        results.append(result)
        if i % 20 == 0 and i != 0:
            print(f"{((i/len(futures))*100)[:3]}")

    # backup results
    result_dir = "../../App/db/data/"
    backup_list_to_pkl(results, result_dir)

    # save results
    save_result_to_df(results, result_dir)
