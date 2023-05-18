### 1. user requests
query = """SELECT count(*) AS requests 
           FROM ps_dynamo_db"""

### 2. user user_requests_fail
query = """SELECT count(*) AS request_fail 
           FROM ps_dynamo_db 
           WHERE SIZE(isbn13_list) = 0"""


### 3. user_selection_per_recom
query = """SELECT avg(*) AS user_select 
           FROM (SELECT count(*) AS request_fail 
                 FROM ps_user_choice 
                 GROUP BY query_id)"""


### 4. count_book
query = """SELECT le.isbn13, re.bookname, le.count 
            FROM (SELECT isbn13, count(*) AS count 
                FROM ps_dynamo_db_isbn13
                GROUP BY isbn13
                ORDER BY count DESC
                LIMIT 100) AS Le
            LEFT JOIN ps_book_info AS re
            ON le.isbn13 = re.isbn13"""


### 5. count_lib
query = """SELECT lib, count(*) AS count 
           FROM ps_dynamo_db_selected_lib 
           GROUP BY lib 
           ORDER BY count DESC"""


### 6. count_keyword
query = """SELECT keyword, count(*) AS count 
           FROM ps_dynamo_db_user_search 
           GROUP BY keyword 
           ORDER BY count DESC
           LIMIT 100"""


### 7.count_query_user
query = """SELECT user_id, COUNT(DISTINCT query_id) AS count
           FROM ps_user_choice 
           GROUP BY user_id
           ORDER BY count DESC
           LIMIT 100"""


### 8.count_unsearchable_keyword
query = """SELECT ri.keyword, count(*) AS count FROM (SELECT * 
           FROM ps_dynamo_db 
           WHERE SIZE(isbn13_list) = 0) AS le
           LEFT JOIN ps_dynamo_db_user_search AS ri
           ON le.query_id = ri.query_id
           GROUP BY keyword"""

query = """SELECT ri.keyword, count(*) AS count FROM (SELECT * 
           FROM ps_dynamo_db 
           WHERE SIZE(isbn13_list) > 0) AS le
           LEFT JOIN ps_dynamo_db_user_search AS ri
           ON le.query_id = ri.query_id
           GROUP BY keyword"""


query = """SELECT le.* FROM query_temp_left le 
            Left JOIN query_temp_right ri
            on le.keyword = ri.keyword
            WHERE ri.keyword is null"""
