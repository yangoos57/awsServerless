from pipeline import BookPipe
import pandas as pd

if __name__ == "__main__":
    # 도서 수집, 전처리, 데이터 정제를 수행하는 파이프라인 선언
    pipeline = BookPipe()

    # 도서관 정보나루 API를 활용해 매월 업데이트되는 도서정보 확보 및 저장
    update_book_df = pipeline.update_books_from_libray()

    # 업데이트 된 도서정보에 대한 도서 이미지, 목차, 저자소개 등 텍스트 데이터 수집 및 저장
    isbns = update_book_df["isbn13"].drop_duplicates().tolist()
    scraping_df = pipeline.scrap_book_info_from_kyobo(isbns)

    # 목차, 저자소개 등 텍스트 데이터를 바탕으로 도서를 대표하는 핵심 키워드 추출
    pipeline.extract_keywords_using_book_info(scraping_df)

    # 키워드 검색 용도로 활용되는 W2V 모델 학습
    w2v_data = pipeline.update_w2v_data(scraping_df)
    pipeline.train_w2v(w2v_data)
