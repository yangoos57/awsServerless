### 데이터 정보(local_data 폴더)

##### main.py 실행 결과 중 local에서 사용할 데이터를 저장

- w2v_data.parquet

  - w2v 학습에 활용할 장서 데이터
  - scraping_result를 누적하여 생성
  - isbn13, title, toc, intro, publisher

- scraping_result.parquet

  - 교보문고에서 스크랩한 장서 데이터
  - isbn13, title, toc, intro, publisher
