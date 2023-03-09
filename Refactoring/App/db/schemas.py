from pydantic import BaseModel
import datetime


class BookInfoSchemas(BaseModel):
    isbn13: int
    bookname: str
    author: str
    publisher: str
    class_no: str
    class_code: str
    reg_date: datetime.datetime
    img_url: str

    class Config:
        orm_mode = str


class BookKeywordsSchemas(BaseModel):
    isbn13: int
    keywords: str

    class Config:
        orm_mode = str


class LibBookSchemas(BaseModel):
    isbn13: int
    lib_name: str

    class Config:
        orm_mode = str
