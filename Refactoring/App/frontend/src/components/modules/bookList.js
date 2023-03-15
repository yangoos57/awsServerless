import React from "react";

function bookInfoBox(imgUrl, bookname, authors, libname, classNo) {
  var a = 0;
  var b = 0;
  var c = 0;
  window.innerWidth > 575 ? (a = 25) : (a = 23);
  window.innerWidth > 575 ? (b = 30) : (b = 8);
  window.innerWidth > 575 ? (c = 30) : (c = 10);
  if (bookname.length > a) {
    bookname = bookname.substring(0, a) + "...";
  }
  if (authors.length > b) {
    authors = authors.substring(0, b) + "...";
  }
  if (libname.length > c) {
    libname = libname.substring(0, c) + "...";
  }
  return (
    <div className="flex-container justify-content-center py-2 bookListBox">
      {/* Beige 색 박스 설정 */}
      <div
        className="flex-container mx-auto p-2"
        style={{
          backgroundColor: "var(--background-dodo-color)",
          width: "100%",
          height: "95%",
          borderRadius: "5px",
        }}>
        {/* Book Info 배치 : 이미지 35% 나머지 65% */}
        <div className="me-2" style={{ flexBasis: "30%" }}>
          <div className="flex-container m-auto">
            {/* <img style={{ width: "100%", border: "0.3px solid #4F4E4E" }} src={imgUrl} alt="" /> */}
          </div>
        </div>
        <div className="flex-container flex-column" style={{ flexBasis: "70%" }}>
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
            color: "#FFF5EA",
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
            {item.map((v) => {
              return bookInfoBox(v.bookImageURL, v.bookname, v.authors, v.lib_name, v.class_no);
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookList;
