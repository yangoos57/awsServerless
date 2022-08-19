import pymysql
import pandas as pd
import numpy as np
from gensim.models import KeyedVectors
import re


def separateKeyword(words: str) -> list:

    """
    - 사용자가 검색한 키워드를 개별 단어로 자른뒤 list로 저장.
    - '파이썬, 자연어' => ['파이썬','자연어']
    """

    if type(words) != str:
        raise ValueError("str only possible")

    k = re.findall(r"\s|,|[^,\s]+|\x08", words)
    k = [i for i in k if i not in [",", " "]]
    return k


def transToHan(words: list) -> list:

    """
    - 영문 키워드를 한글 키워드로 변환한다.
    - 'matplotlib' => '맷플롯립' / 'python' => '파이썬'
    """

    EngToKorDict = pd.read_csv("backend/assets/dodomoa/englist.csv", index_col=0)
    result = []
    for word in words:
        enToko = EngToKorDict[EngToKorDict["0"].isin([word])]
        if enToko.empty is not True:
            result.extend(enToko["1"].tolist())
        else:
            result.append(word)

    return list(set(result))


# 영문 문자 리스트 추출
def findalphabet(text: str) -> str:
    """
    - 영문을 추출한다.
    """
    return re.findall("[a-zA-Z]+", text)


# 한글 문자 리스트 추출
def findHan(text: str) -> str:
    """
    - 한글을 추출한다.
    """
    return re.findall("[\u3130-\u318F\uAC00-\uD7A3]+", text)


#
def searchKeyword(word: list) -> dict:
    """
    - 키워드 검색 시 영문->한글 변환 후 한,영,전체 리스트로 추출한다.
    """
    val = separateKeyword(word)
    keywordItems = transToHan(val)
    engList = list(filter(lambda x: findalphabet(x), keywordItems))
    hanList = list(filter(lambda x: findHan(x), keywordItems))
    return dict(eng=engList, han=hanList, all=keywordItems)


def findOverlapNum(keywordsOfBook: list, keywordsWord2Vec):
    """
    - 키워드가 얼마나 포함됐는지 찾는데 활용된다.
    """
    return np.in1d(keywordsWord2Vec, keywordsOfBook)


def extractKeywords(words: str, num=20) -> list:
    """
    - 사용자가 검색한 키워드와 연관성 높은 키워드 20개를 W2V를 활용해 추출한다.

    """
    # 한,영,전체 리스트 추출
    wordDict: dict = searchKeyword(words)

    # 전체 리스트 확보
    allList = wordDict["all"]

    # 한글 리스트 추출
    hanList = wordDict["han"]

    # 한글로 된 단어가 있으면 w2v에서 키워드 추출 -> 영문인 경우 바로 해당 키워드 검색
    if len(hanList) > 0:
        loaded_model = KeyedVectors.load_word2vec_format("w2v")

        # 키워드 단어 불러오기 20개 추출
        keywordsWord2Vec = loaded_model.most_similar(positive=hanList, topn=num)
        Word2VecKeyword = list(map(lambda x: x[0], keywordsWord2Vec))

        # 사용자가 검색한 단어와 합치기
        allList.extend(Word2VecKeyword)

    # String으로 변환
    keywords = " ".join(allList)
    return keywords


def changeLibName(libName: list):
    """
    frontend에서 받은 도서관명을 db에 저장된 방식으로 변환한다.
    """
    libdict = {
        "강남도서관": "강남",
        "강동도서관": "강동",
        "강서도서관": "강서",
        "개포도서관": "개포",
        "고덕학습관": "고덕",
        "고척도서관": "고척",
        "구로도서관": "구로",
        "남산도서관": "남산",
        "노원학습관": "노원",
        "도봉도서관": "도봉",
        "동대문도서관": "동대문",
        "동작도서관": "동작",
        "마포학습관": "마포",
        "서대문도서관": "서대문",
        "송파도서관": "송파",
        "양천도서관": "양천",
        "영등포도서관": "영등포",
        "용산도서관": "용산",
        "정독도서관": "정독",
        "종로도서관": "종로",
    }
    ist = [libdict[key] for key in libName]
    return ",".join(ist)


def createBookList(libName: list, userKeywords):
    """
    1. frontend에서 도서관 정보(libName)와 키워드(userKeywords)를 받음
    2. 사용자 검색 키워드 외 20개 키워드 추출
    3. 사용자가 선택한 조건 및 키워드로 검색 결과 추출
    4. 도서 검색결과 TOP 50개 선정

    """
    # 1. frontend로부터 도서관 정보와 키워드를 받음
    libName = changeLibName(libName)  # 도서관 이름 변경

    # 2. 사용자 검색 키워드 외 20개 키워드 추출
    keywords = extractKeywords(userKeywords)

    # 3. 사용자가 선택한 조건 및 키워드로 검색 결과 추출

    conn = pymysql.connect(
        host="localhost", port=int(3306), user="root", passwd="", db="dash_test"
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute(
        f"""
        SELECT *
        FROM (
                SELECT keyword2.ISBN, keyword2.keyword, lib.지역모음

                -- 사용자가 선택한 도서관의 도서 정보를 불러온다.
                FROM (SELECT ISBN, GROUP_CONCAT(지역) AS 지역모음
                    FROM backend_dodomoalibinfo
                    where FIND_IN_SET(지역,"{libName}") > 0
                    GROUP BY ISBN ) AS lib

                -- 첫번째 LEFT JOIN
                -- keyword가 포함된 ISBN만 추출
                LEFT JOIN backend_dodomoakeyword2 AS keyword2
                ON keyword2.ISBN = lib.ISBN
                where match(keyword) against("{keywords}")
                ) AS sortedISBN

        -- 두번째 LEFT JOIN
        -- 추출된 도서의 도서정보(제목, 저자, 청구기호 등) 가져오기
        LEFT JOIN backend_dodomoabookinfo AS book
        ON book.ISBN = sortedISBN.ISBN 
        """
    )

    result = cursor.fetchall()
    result = pd.DataFrame(result)

    # 4. TOP 50개 선정

    ## 사용자가 직접 검색한 단어 개수
    wordsLen = len(userKeywords.split(","))

    ## keyword str to list
    keyList = list(map(lambda x: x.split(" "), result["keyword"]))

    ## 추출한 keyword str to list
    allList = keywords.split(" ")

    ## 추출한 키워드와 일치 개수 찾기 & 유저가 검색한 것 3배 가중
    val = np.array(list(map(lambda x: findOverlapNum(x, allList), keyList)))
    df = pd.DataFrame(val)
    for i in range(wordsLen):
        df[i] = df[i] * 3
    result["sum"] = df.T.sum()

    finish = result.sort_values(by="sum", ascending=False)[:50]

    finish = finish[["도서명", "저자", "지역모음", "주제분류번호", "이미지주소"]]
    finish.columns = "title", "author", "lib", "num", "url"
    return finish
