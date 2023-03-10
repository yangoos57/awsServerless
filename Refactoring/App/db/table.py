from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.mysql import VARCHAR, CHAR, INTEGER
from db.database import Base


class BookInfo(Base):
    __tablename__ = "book_info"
    isbn13 = Column(INTEGER(13), primary_key=True)
    bookname = Column(VARCHAR)
    author = Column(VARCHAR)
    publisher = Column(VARCHAR)
    class_no = Column(CHAR(7))
    class_code = Column(CHAR(10))
    reg_date = Column(DateTime)
    img_url = Column(VARCHAR)


class BookKeywords(Base):
    __tablename__ = "book_keywords"
    isbn13 = Column(INTEGER(13), primary_key=True, auto_increment=False)
    keywords = Column(VARCHAR)


class libBooks(Base):
    __tablename__ = "lib_books"
    isbn13 = Column(INTEGER(13), primary_key=True, auto_increment=False)
    lib_name = Column(CHAR(3))
