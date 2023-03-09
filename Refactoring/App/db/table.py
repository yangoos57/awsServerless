from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, CHAR, INTEGER
from sqlalchemy.orm import relationship
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
    id = Column(INTEGER, primary_key=True)
    isbn13 = Column(INTEGER(13), ForeignKey("book_info.isbn13"))
    keywords = Column(VARCHAR)


class libBooks(Base):
    __tablename__ = "lib_books"
    id = Column(INTEGER, primary_key=True)
    isbn13 = Column(INTEGER(13), ForeignKey("book_info.isbn13"))
    lib_name = Column(CHAR(3))
