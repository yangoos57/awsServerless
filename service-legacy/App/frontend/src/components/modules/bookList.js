import React from "react";
import defaultImg from "../assets/default.png";

function bookInfoBox(isbn13, bookname, authors, libname, classNo, key) {
  var titleLength = 0;
  var libLength = 0;
  var authorLength = 0;
  window.innerWidth > 575 ? (titleLength = 23) : (titleLength = 23);
  window.innerWidth > 575 ? (libLength = 10) : (libLength = 8);
  window.innerWidth > 575 ? (authorLength = 20) : (authorLength = 10);
  if (bookname.length > titleLength) {
    bookname = bookname.substring(0, titleLength) + "...";
  }
  if (libname.length > libLength) {
    libname = libname.substring(0, libLength) + "...";
  }
  if (authors.length > authorLength) {
    authors = authors.substring(0, authorLength) + "...";
  }

  var imgUrl = "images/" + isbn13 + ".jpg";
  return (
    <div className="flex-container px-3 py-2 bookListBox" key={key}>
      <div className="flex-container mx-auto p-1 libBox-card">
        {/* Book Info 배치 : 이미지 35% 나머지 65% */}
        <div className="me-2 libBox-card-img">
          <div className="flex-container m-auto">
            <img
              style={{ width: "80px", height: "100px", border: "0.1px solid #4F4E4E" }}
              src={imgUrl}
              alt=""
              onError={(e) => {
                e.target.src = defaultImg;
              }}
            />
          </div>
        </div>
        <div className="flex-container flex-column libBox-card-text">
          {" "}
          <div className="mb-1 bookTitleInfo">{bookname}</div>
          <div className="bookInfo">저자 : {authors}</div>
          <div className="bookInfo">도서관 : {libname}</div>
          <div className="bookInfo">청구기호 : {classNo}</div>
        </div>
      </div>
    </div>
  );
}

// Main Function
const BookList = ({ item }) => {
  return (
    <div className="flex-container resultBox-dodo ">
      <div
        className="flex-container flex-column mx-auto px-2"
        style={{ display: item[0].bookname.length === 0 ? "none" : "" }}>
        {/* 검색건수 */}
        <div
          className="d-flex mt-3 ms-auto"
          style={{
            paddingRight: "5%",
            flexBasis: "5%",
            fontWeight: "bolder",
          }}>
          총 {item.length}건 검색
        </div>
        <div
          className="flex-container"
          style={{ overflow: "hidden", flexBasis: "90%", position: "relative", height: "auto" }}>
          <div
            className="d-flex flex-column"
            style={{ position: "absolute", overflow: "scroll", height: "100%", width: "100%" }}>
            {item.map((v, k) => {
              return bookInfoBox(v.isbn13, v.bookname, v.authors, v.lib_name, v.class_no, k);
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookList;
