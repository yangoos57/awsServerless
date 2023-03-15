from configs import Deployment
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from datetime import datetime
from itertools import chain
from typing import Union
import aiohttp
import aiofiles
import asyncio
import re
from collections import namedtuple


def update_lib_book_data(
    lib_code: Union[str, int],
    chunk: int = 10,
    start_date: datetime.date = None,
    end_date: datetime.date = datetime.now().date(),
) -> list[tuple[str, map]]:
    """도서관 정보를 asyncio를 활용해 불러오는 함수"""

    auth_key = Deployment().api_auth_key

    for i in range(0, len(lib_code), chunk):
        chunk_lib_code = lib_code[i : i + chunk]
        tasks = [_update_lib_book_data(i, auth_key, start_date, end_date) for i in chunk_lib_code]
        result = asyncio.run(asyncio.wait(tasks))

    return list(map(lambda x: x.result(), result[0]))


async def _update_lib_book_data(
    lib_code: Union[str, int],
    auth_key: str,
    start_date: datetime.date = None,
    end_date: datetime.date = datetime.now().date(),
) -> map:
    """정보나루 API에서 매달 추가 되는 도서 정보 확보"""

    if not start_date:
        """당일 기준 한 달 전 데이터 확보"""
        start_date = end_date - relativedelta(months=1)

    libUrl = f"http://data4library.kr/api/itemSrch?libCode={lib_code}&startDt={start_date}&endDt={end_date}&authKey={auth_key}&pageSize=10000&format=json"
    before = datetime.now()

    async with aiohttp.ClientSession() as session:
        async with session.get(libUrl) as resp:
            raw_data = await resp.json()

    after = datetime.now()

    print("실행시간 : ", after - before)

    all_books_info = map(lambda x: x["doc"], raw_data["response"]["docs"])
    cs_data_books_info = filter(_check_cs_data_book, all_books_info)

    return (lib_code, map(_delete_unnecessary_columns, cs_data_books_info))


def _check_cs_data_book(class_num: str) -> bool:
    """
    필요한 도서 데이터 추출
    004 = 전산학,
    005 = 프로그래밍, 프로그램, 데이터
    """
    num = class_num["class_no"][:3]

    # 004 = 전산학, 005 = 프로그래밍, 프로그램, 데이터
    return num == "004" or num == "005"


def _delete_unnecessary_columns(item: dict) -> dict:
    """불필요한 column 제거"""

    keys = [
        "isbn13",
        "bookname",
        "authors",
        "publisher",
        "class_no",
        "reg_date",
        "bookImageURL",
    ]
    selected_item = dict((k, item[k]) for k in keys)

    # if "callNumbers" in item:
    #     if item["callNumbers"] != []:
    #         selected_item["book_code"] = item["callNumbers"][0]["callNumber"]["book_code"]
    #     else:
    #         selected_item["book_code"] = ""
    # else:
    #     selected_item["book_code"] = ""

    return selected_item


async def scrap_book_info(ISBN: Union[str, int]) -> map:
    """book_title, book_toc, book_intro, publisher 등의 도서정보 추출"""

    url = (
        f"http://www.kyobobook.co.kr/product/detailViewKor.laf?ejkGb=KOR&mallGb=KOR&barcode={ISBN}"
    )

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url) as resp:
            html = await resp.read()
            await asyncio.sleep(0.5)

    kyobo_soup = BeautifulSoup(html.decode("utf-8"), "html.parser")

    if kyobo_soup.find(class_="prod_title"):
        await _download_book_cover_img(kyobo_soup, f"data/update/img/{ISBN}.jpg")

        book_title: str = _extract_title(kyobo_soup)
        book_publisher: list[str] = _extract_publisher(kyobo_soup)
        book_intro: list[str] = _extract_intro(kyobo_soup)
        book_toc: list[str] = _extract_toc(kyobo_soup)

        book_info = list(map(_clean_up_book_info, [book_toc, book_intro, book_publisher]))
        return [ISBN, book_title] + book_info
    else:
        return []


def _extract_title(soup: BeautifulSoup) -> str:
    """title 추출"""
    title_soup = soup.find(class_="prod_title")

    if title_soup:
        title = title_soup.string
    else:
        title = "no_title_name"

    return title


def _extract_intro(soup: BeautifulSoup) -> list[str]:
    """intro 추출"""
    book_intro_soup = soup.find_all("div", "info_text")

    if book_intro_soup:
        book_intro_chunk = str(book_intro_soup[-1]).split("<br/>")
        book_intro_chunk_2d = list(
            map(lambda x: re.sub("<.*>", "", x).replace(".", ".##").split("##"), book_intro_chunk)
        )
        book_intro = list(chain(*book_intro_chunk_2d))
    else:
        book_intro = []

    return book_intro


def _extract_toc(soup: BeautifulSoup) -> list[str]:
    """toc 추출"""
    book_toc_soup = soup.find(class_="book_contents_item")

    if book_toc_soup:
        book_toc = str(book_toc_soup).split("<br/>")[1:-1]
    else:
        book_toc = []

    return book_toc


def _extract_publisher(soup: BeautifulSoup) -> list[str]:
    """publisher 추출"""
    publisher_soup: str = soup.find(class_="book_publish_review")

    if publisher_soup:
        publisher = publisher_soup.p.get_text().replace(".", ".##").split("##")
    else:
        publisher = []

    return publisher


async def _download_book_cover_img(soup: BeautifulSoup, dir: str) -> None:
    """도서 이미지 다운로드"""
    async with aiohttp.ClientSession(trust_env=True) as session:
        url = soup.find(name="meta", property="og:image")["content"]
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(f"{dir}", "wb") as f:
                    await f.write(await resp.read())


def _clean_up_book_info(book_info: list[str]) -> list[Union[str, list[str]]]:
    """불필요한 데이터 전처리"""
    # 한글 알파벳 제외하고 모두 제거
    book_info = (re.sub("[^A-Za-z\u3130-\u318F\uAC00-\uD7A3]", " ", i) for i in book_info)

    # 공백 하나로 줄이기 ex) '  ' -> ' '
    book_info = (re.sub(" +", " ", i).strip(" ") for i in book_info)

    # '' 제거
    book_info = filter(None, book_info)

    return list(book_info)


def scrap_book_info_with_multiprocessing(isbns: list[Union[str, int]]) -> str:
    """scrap_book_info 함수를 Processpoolexecutor 기반으로 실행"""
    tasks = [scrap_book_info(isbn) for isbn in isbns]
    result = asyncio.run(asyncio.wait(tasks))
    result = list(map(lambda x: x.result(), result[0]))
    return str(result)
