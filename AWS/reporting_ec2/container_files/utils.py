import datapane as dp
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import os
import boto3

plt.style.use("seaborn-bright")
# plt.style.available
plt.rcParams["font.family"] = "Noto Sans KR"
mpl.rcParams["axes.unicode_minus"] = False


def create_report(date_time: str = "2023-05-17"):
    if os.path.isdir(f"data/{date_time}") == False:
        os.makedirs(f"data/{date_time}")
    # options
    plt.switch_backend("Agg")
    plt.style.use("seaborn-bright")
    plt.rcParams["font.family"] = "Noto Sans KR"
    mpl.rcParams["axes.unicode_minus"] = False

    # download parquet
    s3 = boto3.client("s3")
    files = [
        "count_keyword",
        "count_book",
        "count_lib",
        "count_unsearchable_keyword",
        "user_requests",
        "user_requests_fail",
        "user_selection_per_recom",
    ]
    # Download the file from S3
    for fname in files:
        bucket_name = "dodomoabucket"
        object_key = f"report/data/{date_time}/{fname}.parquet"
        local_file_path = f"data/{date_time}/{fname}.parquet"
        s3.download_file(bucket_name, object_key, local_file_path)

    # load parquet
    data_dict = dict()
    file_dir = f"data/{date_time}"

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
        _create_dp_group_of(data_dict["count_keyword"], title_dict["count_keyword"]),
        _create_dp_group_of(
            data_dict["count_book"], title_dict["count_book"], column_name=["bookname", "count"]
        ),
        _create_dp_group_of(data_dict["count_lib"], title_dict["count_lib"]),
        _create_dp_group_of(
            data_dict["count_unsearchable_keyword"], title_dict["count_unsearchable_keyword"]
        ),
    ]

    app = dp.App(
        f"# 일일 앱 사용 결과 ({date_time})",
        "### ",
        stats_group,
        dp.Group(dp.Select(blocks=section_group)),
    )

    app.save(path=f"report/{date_time}/report_{date_time}.html")

    # update html file

    return s3.upload_file(
        f"report/{date_time}/report_{date_time}.html",
        "dodomoabucket",
        f"report/{date_time}/report_{date_time}.html",
    )


def _create_stack_barh(
    name_1,
    width_1,
    name_2=None,
    width_2=None,
    width_size: float = 1.05,
    height=0.85,
    color_1="#FFFFFF",
    color_2="#2373B8",
    title_name=None,
):

    fig, ax = plt.subplots(figsize=(4, 3))

    # name set
    if name_2 is None:
        name_2 = name_1
    if width_2 is None:
        width_2 = [max(width_1) * width_size] * len(name_2)

    # create bar
    ax.barh(y=name_2, width=width_2, height=height, color=color_1)
    ax.barh(y=name_1, width=width_1, height=height, color=color_2)

    # add labels
    for i, (x_value, y_value) in enumerate(zip(name_1, width_1)):
        ax.text(
            s=x_value, x=min(width_1) * 0.01, y=i, color="w", verticalalignment="center", size=8
        )
        ax.text(
            s=y_value,
            x=max(width_2) * width_size,
            y=i,
            color="k",
            verticalalignment="center",
            size=10,
        )

    # turn axis off
    plt.axis("off")
    # ax.set_ylabel("")
    # ax.set_yticklabels([])
    # ax.set_xlabel("")
    # ax.set_xticklabels([])

    if title_name is not None:
        plt.title(title_name)
    plt.close()
    return fig


def _create_dp_group_of(
    df,
    label: str,
    column_name: list = None,
):

    plot_data = df.head(10).sort_values("count")
    if column_name is None:
        column_name = df.columns
    name = plot_data[column_name[0]].map(lambda x: x if len(x) < 20 else x[:20] + "...").tolist()
    width = plot_data[column_name[1]].tolist()
    return dp.Group(
        dp.Plot(_create_stack_barh(name_1=name, width_1=width, title_name=label)),
        dp.DataTable(df.reset_index(drop=True).sort_values(by="count", ascending=False)),
        columns=2,
        label=label,
    )
