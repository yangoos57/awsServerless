## 도서관 장서 검색 서비스

### 개요

개인 프로젝트로 진행한 [Sbert를 활용한 도서 키워드 추출 모델](https://github.com/yangoos57/Sentence_bert_from_scratch/blob/main/keyword_extraction_using_sbert/main.ipynb)을 활용해 도서관 장서 검색 서비스를 구현하였습니다.

### 프로젝트 진행 배경

평소 컴퓨터, 데이터 분야의 책을 빌릴때면 원하는 도서를 찾는데 어려움이 있었습니다. 도서 검색으로는 찾고자 하는 분야를 찾는데 한계가 있었으며 도서 분류 기준이 명확하지 않아 같은 분야임에도 여러 책장에 분산되어 직접 찾는 방법에도 어려움이 있었습니다. 이러한 불편함을 해결하기 위해 NLP 기반 도서 검색 프로젝트를 기획했습니다.

### 프로젝트 구현 결과

> [링크](http://yangoos.me/)를 클릭하시면 서비스를 이동 하실 수 있습니다.

https://user-images.githubusercontent.com/98074313/226160516-234422e5-ebfb-4daa-9105-52ee225d6f83.mov

### 프로젝트 구조

<br/>
<img width=600px src='images/dodomoa_architecture.png'>
<br/>

### 프로젝트 구현 사항

#### 데이터 수집 자동화 및 학습 파이프라인 구축

- 서울시 도서관이 보유중인 5895권의 컴퓨터/데이터 장서 정보를 기반으로 목차, 도서 소개, 출판사 리뷰를 크롤링하여 도서 데이터 수집

- 매월 도서 정보가 업데이트 되는 시점에 맞춰 데이터 수집 및 모델 학습을 자동화하는 파이프라인을 로컬 환경에 구축

- [Sbert 기반 키워드 추출 모델](https://github.com/yangoos57/Sentence_bert_from_scratch/blob/main/keyword_extraction_using_sbert/main.ipynb)을 활용해 도서를 대표하는 핵심 키워드를 추출하고 DB에 저장

#### 웹 서버 개발

- 도서별로 추출한 핵심 키워드와 사용자 검색 키워드를 비교하여 연관 도서 정보를 제공하는 서비스 구현

- 도서 이미지, 웹페이지와 같은 정적 파일 처리를 담당하는 NGINX를 구축하여 검색 서버 부하 최소화

- PC, 모바일에서 간편하게 사용 할 수 있는 반응형 웹 구현
