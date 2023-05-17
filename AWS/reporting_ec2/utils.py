import datapane as dp
import matplotlib.pyplot as plt
import matplotlib as mpl

plt.style.use("seaborn-bright")
# plt.style.available
plt.rcParams["font.family"] = "Noto Sans KR"
mpl.rcParams["axes.unicode_minus"] = False


def create_stack_barh(
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


def create_dp_group_of(
    df: str,
    label: str,
    column_name: list = None,
):

    plot_data = df.head(10).sort_values("count")
    if column_name is None:
        column_name = df.columns
    name = plot_data[column_name[0]].map(lambda x: x if len(x) < 20 else x[:20] + "...").tolist()
    width = plot_data[column_name[1]].tolist()
    return dp.Group(
        dp.Plot(create_stack_barh(name_1=name, width_1=width, title_name=label)),
        dp.DataTable(df.reset_index(drop=True).sort_values(by="count", ascending=False)),
        columns=2,
        label=label,
    )
