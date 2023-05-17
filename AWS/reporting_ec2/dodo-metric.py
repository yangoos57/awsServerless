import datapane as dp
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import os
from utils import create_dp_group_of
from datetime import datetime

# options
plt.switch_backend("Agg")
plt.style.use("seaborn-bright")
plt.rcParams["font.family"] = "Noto Sans KR"
mpl.rcParams["axes.unicode_minus"] = False

# download parquet

# load parquet
data_dict = dict()
file_dir = "data/"

for fname in os.listdir(file_dir):
    fname = fname.split(".parquet")[0]
    data_dict[fname] = pd.read_parquet(f"{file_dir}/{fname}.parquet")


# dp_stats variables
requests = data_dict["user_requests"].values[0][0]
requests_fail = data_dict["user_requests_fail"].values[0][0]
fail_ratio = requests_fail / requests
user_select_per_recom = data_dict["user_selection_per_recom"].values[0][0]


# dp_group variables
title_dict = {
    "count_keyword": "유저 검색 키워드",
    "count_book": "도서 검색 순위",
    "count_lib": "도서관 검색 순위",
    "count_unsearchable_keyword": "검색 실패 키워드",
}


def create_report():
    stats_group = dp.Group(
        dp.BigNumber(heading="사용자 요청 건수", value=format(requests, ",") + " 건"),
        dp.BigNumber(heading="도서 검색 실패율", value=format(fail_ratio, ".3f") + "%"),
        dp.BigNumber(
            heading="평균 도서 선택 권수",
            value=format(user_select_per_recom, ".2f") + " 건",
        ),
        columns=3,
    )

    section_group = [
        create_dp_group_of("count_keyword", title_dict["count_keyword"]),
        create_dp_group_of(
            "count_book", title_dict["count_book"], column_name=["bookname", "count"]
        ),
        create_dp_group_of("count_lib", title_dict["count_lib"]),
        create_dp_group_of("count_unsearchable_keyword", title_dict["count_unsearchable_keyword"]),
    ]

    app = dp.App(
        f"# 일일 앱 사용 결과 ({datetime.now().strftime('%Y-%m-%d')})",
        "### ",
        stats_group,
        dp.Group(dp.Select(blocks=section_group)),
    )

    # update html file
    return app.save(path="model_metrics.html")


if __name__ == "__main__":
    create_report()
