from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from konlpy.tag import Hannanum
from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import pandas as pd
import time
from tqdm.notebook import tqdm
from keybert import KeyBERT
from queue import Queue
from threading import Thread


# Extract Function 시작
def loadLibBook(libCode: int, startDate: str) -> pd.DataFrame:
    """
    ex) startData : "2022-07-11"
    """
    from datetime import timedelta, datetime

    day = datetime.strptime(startDate, "%Y-%m-%d").date()

    # 해당 달의 첫째날 구하기
    first_day = day.replace(day=1)

    # 전달의 마지막 날 구하기
    dayLast = first_day - timedelta(days=1)

    # 전달의 첫째 날 구하기
    dayStart = dayLast.replace(day=1)
    # print(dayStart, " - ", dayLast)

    libUrl = f"http://data4library.kr/api/itemSrch?libCode={libCode}&startDt={dayStart}&endDt={dayLast}&authKey=7123eacb2744a02faca2508a82304c3bf154bf0b285da35c2faa2b8498b09872&pageSize=10000"
    libHtml = requests.get(libUrl)
    libSoup = BeautifulSoup(libHtml.content, features="xml")

    libBookname = list(map(lambda x: x.string, libSoup.find_all("bookname")))
    libAuthor = list(map(lambda x: x.string, libSoup.find_all("authors")))
    libPublisher = list(map(lambda x: x.string, libSoup.find_all("publisher")))
    libISBN = list(map(lambda x: x.string, libSoup.find_all("isbn13")))
    libClassNum = list(map(lambda x: x.string, libSoup.find_all("class_no")))
    libRegDate = list(map(lambda x: x.string, libSoup.find_all("reg_date")))
    libBookImageURL = list(map(lambda x: x.string, libSoup.find_all("bookImageURL")))

    data = pd.DataFrame(
        [
            libBookname,
            libAuthor,
            libPublisher,
            libISBN,
            libClassNum,
            libRegDate,
            libBookImageURL,
        ]
    ).T
    data.columns = ["도서명", "저자", "출판사", "ISBN", "주제분류번호", "등록일자", "이미지주소"]
    sortedData: pd.DataFrame = data[~data["주제분류번호"].isna()]
    return sortedData


##최신버전
def extractAllLibBooksMultiThread(date: str, thread_num: int = 11) -> pd.DataFrame:
    startDate = date
    q = Queue()
    dataframes = []
    seoulLibCode = [
        111003,
        111004,
        111005,
        111006,
        111007,
        111008,
        111009,
        111010,
        111022,
        111011,
        111012,
        111013,
        111014,
        111031,
        111016,
        111017,
        111030,
        111015,
        111018,
        111019,
        111020,
        111021,
    ]

    for code in seoulLibCode:
        q.put(code)

    def process():
        while True:
            code = q.get()
            item = loadLibBook(code, startDate)
            dataframes.append(item)
            q.task_done()
            print(f"{code} 완료")

    for _ in range(thread_num):
        worker = Thread(target=process)
        worker.daemon = True
        worker.start()

    q.join()

    result = pd.concat(dataframes).drop_duplicates(subset="ISBN")
    val = result["주제분류번호"].astype(str)
    BM = val.str.contains("004") | val.str.contains("005")
    result: pd.DataFrame = result[BM].reset_index(drop=True)
    return result


# 과거버전(안정성 확보되면 삭제)
def extractAllLibBooks(startDate: str) -> pd.DataFrame:
    seoulLibCode = [
        111003,
        111004,
        111005,
        111006,
        111007,
        111008,
        111009,
        111010,
        111022,
        111011,
        111012,
        111013,
        111014,
        111031,
        111016,
        111017,
        111030,
        111015,
        111018,
        111019,
        111020,
        111021,
    ]
    dataframes = []
    for code in tqdm(seoulLibCode):
        libBook: pd.DataFrame = loadLibBook(code, startDate)
        dataframes.append(libBook)

    result = pd.concat(dataframes).drop_duplicates(subset="ISBN")
    val = result["주제분류번호"].astype(str)
    BM = val.str.contains("004") | val.str.contains("005")
    result: pd.DataFrame = result[BM].reset_index(drop=True)
    return result


def extractKyobo(ISBN: int) -> list:
    kyoboUrl = f"http://www.kyobobook.co.kr/product/detailViewKor.laf?ejkGb=KOR&mallGb=KOR&barcode={ISBN}"
    kyoboHtml = requests.get(kyoboUrl)
    kyoboSoup = BeautifulSoup(kyoboHtml.content, "html.parser")

    try:
        bookTitle: str = kyoboSoup.h1.strong.string.strip()

        contents = kyoboSoup.find_all(class_="box_detail_article")
        sortedItems = []
        for item in contents:
            if item.find(class_="content"):
                # 숨겨진 항목을 불러오는 조건식
                item = item.find_all(class_="content")[-1]

            result = re.sub("<.*?>|\W|[_*]", " ", str(item))
            sortedItems.append(result)

        itemList = [bookTitle, ISBN]
        itemList.extend(sortedItems)

    except:
        itemList = ["skip", ISBN]
        print("Skip :", ISBN)

    return itemList


# 최신버전
def kyoboSaveMultiThread(ISBNs: list, thread_num: int = 10) -> list:
    result: list = []

    q = Queue()
    for ISBN in ISBNs:
        q.put(ISBN)

    def process():
        for num in range(9999):
            ISBN = q.get()
            item = extractKyobo(ISBN)
            result.append(item)
            q.task_done()
            if (num + 1) % 5 == 0:
                time.sleep(0.5)

    for _ in range(thread_num):
        worker = Thread(target=process)
        worker.daemon = True
        worker.start()

    q.join()
    print("kyoboBooks 추출완료")

    return result


# 과거버전(안정성 확보되면 삭제)
def kyoboSave(ISBNs: list) -> list:
    # return [kyoboExtract(ISBN) for ISBN in ISBNs]
    result: list = []
    for num, ISBN in tqdm(enumerate(ISBNs)):
        val = extractKyobo(ISBN)
        result.append(val)
        if (num + 1) % 10 == 0:
            time.sleep(0.5)

    return result


def extract(startDate: str) -> tuple:
    df = extractAllLibBooksMultiThread(startDate)
    dfISBN = df["ISBN"]
    ### mysql에 저장된 ISBN과 비교해서 없는 것만 불러오는 function 추가하기
    docs: list = kyoboSaveMultiThread(dfISBN)
    print(f"총 : {len(docs)}개 추출")
    return df, docs


# Transform Functions


def findEng(text: str) -> str:
    # han = re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', text)
    eng = re.findall("[a-zA-Z]+", text)
    return eng


def removeStopwords(text: list, stopwords: list) -> str:
    # text = list(filter(None, doc.split(" ")))
    word = [word for word in text if word not in stopwords]
    result = " ".join(word)
    return result


### 최신버전
def extractKeywords(doc: str, stopwords: list, keyBertModel) -> list:
    """
    반복적으로 모델을 불러와야하는 문제를 개선하기 위해 변수에 model을 넣었음.
    모델을 미리 불러와야 한다.
    리턴 값으로 keyword를 반환함.
    """
    doc: str = (
        re.sub("\d[.]|\d|\W|[_]", " ", doc)
        .replace("머신 러닝", "머신러닝")
        .replace("인공 지능", "인공지능")
    )
    text = list(filter(None, doc.split(" ")))
    removedoc: str = removeStopwords(text, stopwords)

    # 문서 정보 추출
    hannanum = Hannanum()
    hanNouns: list = hannanum.nouns(removedoc)
    words: str = " ".join(hanNouns)

    docResult: list = keyBertModel.extract_keywords(
        words, top_n=10, keyphrase_ngram_range=(3, 3), use_mmr=True, diversity=0.1
    )
    result = list(map(lambda x: x[0], docResult))

    items = []
    for item in result:
        items.extend(item.split(" "))

    # Stopwords remove
    items: str = removeStopwords(items, stopwords)
    hanNouns: str = removeStopwords(hanNouns, stopwords)

    bertInfo = pd.DataFrame(items.split(" "))
    keyWordInfo = pd.DataFrame(hanNouns.split(" "))

    keyWords = (
        pd.concat([bertInfo, keyWordInfo], axis=0)
        .groupby(by=0)
        .size()
        .sort_values(ascending=False)
        .index.tolist()
    )

    keyWords = list(filter(lambda a: a if len(a) > 1 else None, keyWords))

    engList = (
        pd.DataFrame(findEng(removedoc))
        .value_counts()
        .sort_values(ascending=False)[:20]
        .index.tolist()
    )

    engList = list(map(lambda x: x[0], engList))

    result: list = keyWords[:20]
    result.extend(engList)
    return result


def transform(extract: tuple) -> pd.DataFrame:
    df: pd.DataFrame = extract[0]
    docs: list = extract[1]

    stopwords = pd.read_csv("./data/stopwords.csv").T.values.tolist()[0]
    keyBertModel = KeyBERT("paraphrase-multilingual-MiniLM-L12-v2")

    keywords = []
    for doc in tqdm(docs):
        doc = " ".join(doc)
        val: list = extractKeywords(doc, stopwords=stopwords, keyBertModel=keyBertModel)
        keywords.append(val)

    df["keywords"] = keywords

    return df


# TransformerFunctions 끝

## 예전버전(삭제용)
def bookInfoExtraction(doc: str, stopwords: list, model) -> list:
    """
    반복적으로 모델을 불러와야하는 문제를 개선하기 위해 변수에 model을 넣었음.
    모델을 미리 불러와야 한다.
    리턴 값으로 keyword를 반환함.
    """
    start_in = time.time()
    doc: str = (
        # re.sub("[_-]|\d[.]|\d|[▶★●]", "", doc)
        re.sub("\d[.]|\d|\W|[_]", " ", doc)
        .replace("머신 러닝", "머신러닝")
        .replace("인공 지능", "인공지능")
    )
    text = list(filter(None, doc.split(" ")))
    removedoc = removeStopwords(text, stopwords)

    # 문서 정보 추출
    hannanum = Hannanum()
    hanNouns = hannanum.nouns(removedoc)
    vect = CountVectorizer(ngram_range=(2, 2))
    words = " ".join(hanNouns)
    count = vect.fit([words])
    candidate = count.get_feature_names_out()

    doc_embedding = model.encode([removedoc])
    candidate_embeddings = model.encode(candidate)
    result: list = mmr(
        doc_embedding, candidate_embeddings, candidate, top_n=20, diversity=0.2
    )

    items = []
    for item in result:
        items.extend(item.split(" "))

    # Stopwords remove
    items = removeStopwords(items, stopwords)
    hanNouns = removeStopwords(hanNouns, stopwords)

    bertInfo = pd.DataFrame(items.split(" "))
    keyWordInfo = pd.DataFrame(hanNouns.split(" "))

    keyWords = (
        pd.concat([bertInfo, keyWordInfo], axis=0)
        .groupby(by=0)
        .size()
        .sort_values(ascending=False)
        .index.tolist()
    )

    keyWords = list(filter(lambda a: a if len(a) > 1 else None, keyWords))
    # engList = pd.DataFrame(findEng(doc)).value_counts().sort_values(ascending=False)[:5]
    return keyWords[:20]


def mmr(doc_embedding, candidate_embeddings, words, top_n, diversity):
    start_in = time.time()
    # 문서와 각 키워드들 간의 유사도가 적혀있는 리스트
    word_doc_similarity = cosine_similarity(candidate_embeddings, doc_embedding)
    # 각 키워드들 간의 유사도
    word_similarity = cosine_similarity(candidate_embeddings)

    # 문서와 가장 높은 유사도를 가진 키워드의 인덱스를 추출.
    # 만약, 2번 문서가 가장 유사도가 높았다면
    # keywords_idx = [2]
    keywords_idx = [np.argmax(word_doc_similarity)]

    # 가장 높은 유사도를 가진 키워드의 인덱스를 제외한 문서의 인덱스들
    # 만약, 2번 문서가 가장 유사도가 높았다면
    # ==> candidates_idx = [0, 1, 3, 4, 5, 6, 7, 8, 9, 10 ... 중략 ...]
    candidates_idx = list(range(0, len(words)))
    candidates_idx.remove(keywords_idx[0])

    # 최고의 키워드는 이미 추출했으므로 top_n-1번만큼 아래를 반복.
    # ex) top_n = 5라면, 아래의 loop는 4번 반복됨.
    for _ in range(top_n - 1):
        candidate_similarities = word_doc_similarity[candidates_idx, :]
        target_similarities = np.max(
            word_similarity[candidates_idx][:, keywords_idx], axis=1
        )

        # MMR을 계산
        mmr = (
            1 - diversity
        ) * candidate_similarities - diversity * target_similarities.reshape(-1, 1)
        mmr_idx = candidates_idx[np.argmax(mmr)]

        # keywords & candidates를 업데이트
        keywords_idx.append(mmr_idx)
        candidates_idx.remove(mmr_idx)

    return [words[idx] for idx in keywords_idx]


if __name__ == "__main__":

    bookInfo = pd.read_parquet("./data/bookInfo.parquet")
    stopwords = pd.read_csv("./data/stopwords.csv").T.values.tolist()[0]
    keyBertModel = KeyBERT("paraphrase-multilingual-MiniLM-L12-v2")
    text = bookInfo.iloc[0].dropna().astype(str).tolist()

    text = " ".join(text)

    result = extractKeywords(text, stopwords, keyBertModel)

    print(result)
