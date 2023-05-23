from pipeline import BookPipe
from components.modeling import keywordExtractor
import pandas as pd
from typing import Dict

# define keyword extraction workers
worker = keywordExtractor(dir="data/preprocess/eng_han.csv")


def allocate_job_to_worker(job: pd.DataFrame) -> Dict:
    """키워드 추출을 위한 멀티프로세싱 잡 생성"""
    return worker.extract_keyword(job)


if __name__ == "__main__":
    # 파이프라인 선언 - 도서 수집, 전처리, 데이터 정제 수행
    print("start main.py")
    pipeline = BookPipe()

    # 도서정보 확보 및 저장 - 도서관 정보나루 API 활용
    book_df = pipeline.update_books_from_libray()

    # 텍스트 데이터 수집 및 저장 - 이미지, 목차, 저자소개 등
    isbns = book_df["isbn13"].drop_duplicates().tolist()
    scraping_df = pipeline.scrap_book_info_from_kyobo(isbns)

    # 수집 데이터 바탕으로 도서별 핵심 키워드 추출
    pipeline.extract_keywords_using_book_info(scraping_df, allocate_job_to_worker)

    # 키워드 검색 용도로 활용되는 W2V 모델 학습
    w2v_data = pipeline.update_w2v_data(scraping_df)
    pipeline.train_w2v(w2v_data)
