import React, { useState, useEffect } from "react";
import MainFrame from "./modules/mainFrame";
import Search from "./modules/search";
import MiniLib from "./modules/miniLib";
import BookList from "./modules/bookList";
import { useSearchParams } from "react-router-dom";
import axios from "axios";

function ResultPage() {
  const [item, setItem] = useState([
    {
      isbn13: "",
      bookname: null,
      authors: "",
      publisher: "",
      class_no: "",
      reg_date: "",
      bookImageURL: "",
      lib_name: "",
    },
  ]);
  const [keyword, setKeyword] = useState([""]);
  const [libInfo, setLibInfo] = useState([""]);
  const searchInfo = { keyword: keyword, library: libInfo };

  const [searchParams] = useSearchParams();

  useEffect(() => {
    const searchedParams = [...searchParams];
    const libValue = searchedParams
      .filter((e) => {
        return e.includes("library");
      })
      .map((e) => {
        return e[1];
      });
    const libName = libValue.map((e) => {
      return e.slice(-e.length, -3);
    });
    const userSearch = searchParams.get("keyword").replace(",", "").split(" ");

    setKeyword(searchParams.get("keyword"));
    setLibInfo(libValue);

    //axios
    axios
      .post("/predict", {
        user_search: userSearch,
        selected_lib: libName,
      })
      .then((res) => {
        setItem(res.data.result);
      });
  }, [searchParams]);

  const noSearchResult = () => {
    return (
      <div className=" d-flex resultBox-dodo px-2 w-100" style={{ color: "var(--background-dodo-color)" }}>
        <div className="d-flex m-auto flex-column ">
          <div className="h3 m-auto my-4 ">검색 결과가 없습니다.</div>
          <div className="m-auto noSearchInfo  mb-3">띄어쓰기 또는 쉼표로 키워드를 분류해주세요.</div>
          <div className="m-auto noSearchInfo ">특수문자 또는 숫자 검색은 불가합니다.</div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex-container flex-column mx-auto fade-in-box-dodo" style={{ width: "80%", position: "relative" }}>
      <div className="d-flex" style={{ flexBasis: "10%" }}>
        <MiniLib libs={libInfo} checkedInputs={libInfo} setCheckedInputs={setLibInfo} />
      </div>
      <div className="d-flex mx-auto" style={{ flexBasis: "10%", width: "100%" }}>
        <Search placeholder={keyword} setCheckedInputs={setKeyword} values={searchInfo} />
      </div>
      <div className="flex-container mx-auto" style={{ flexBasis: "75%" }}>
        {item[0].bookname === null ? noSearchResult() : <BookList item={item} />}
      </div>
    </div>
  );
}

// Main Function
const Result = () => {
  return <MainFrame children={ResultPage()} />;
};

export default Result;
