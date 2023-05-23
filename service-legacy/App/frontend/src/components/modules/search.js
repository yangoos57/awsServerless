import React from "react";
import { createSearchParams, useNavigate } from "react-router-dom";

const checkCondition = (values, navigate) => {
  if (values["keyword"].length === 0 && values["library"].length === 0) {
    return window.alert("도서관 선택 및 키워드를 검색해 주세요.");
  } else if (values["keyword"].length === 0) {
    return window.alert("키워드를 검색하세요. ex) 파이썬, matplotlib, pandas");
  } else if (values["library"].length === 0) {
    return window.alert("도서관을 선택해주세요.");
  } else {
    navigate({
      pathname: "/searchresult",
      search: `?${createSearchParams({
        keyword: values["keyword"],
        library: values["library"],
      })}`,
    });
  }
};

// alert 분별
const handleEnter = (event, values, navigate) => {
  if (event.key.toLowerCase() === "enter") {
    checkCondition(values, navigate);
  }
};
const clickSearch = (values, navigate) => {
  checkCondition(values, navigate);
};
const Search = ({ placeholder, setCheckedInputs, values }) => {
  // 도서 검색 시 result 페이지 이동
  const navigate = useNavigate();

  return (
    <div className="flex-container" style={{ position: "relative" }}>
      <input
        onKeyDown={(e) => handleEnter(e, values, navigate)}
        placeholder={placeholder}
        className="search-dodo"
        onChange={(e) => setCheckedInputs(e.target.value)}
      />
      <div onClick={() => clickSearch(values, navigate)} className="d-flex searchIcon">
        <i className="fa fa-search fa-lg m-auto" aria-hidden="true" style={{ color: "#4F4E4E" }} />
      </div>
    </div>
  );
};
export default Search;
