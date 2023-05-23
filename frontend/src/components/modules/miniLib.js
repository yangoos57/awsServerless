import React from "react";
import { Link } from "react-router-dom";
import miniLogo from "../assets/minilogo.svg";
import PopOver from "./popover";
const MiniLib = ({ libs, checkedInputs, setCheckedInputs }) => {
  // libs = 선택한 도서관 개수 보여주기

  // 선택한 도서관 개수에 따라 제공되는 표현 달라짐
  if (libs.length > 1) {
    var libName = libs[0] + " 외 " + (libs.length - 1);
  } else if (libs.length === 1) {
    libName = libs[0];
  } else {
    libName = "도서관을 선택하세요";
  }

  return (
    <div className="flex-container align-items-end mb-1">
      {/* 로고 클릭 시 메인페이지로 이동 */}
      <Link to="/" style={{ textDecoration: "none", flexBasis: "50%" }}>
        <div className="d-flex">
          <img className="minilogo-dodo" src={miniLogo} alt="" />
        </div>
      </Link>
      <div className="d-flex" style={{ flexBasis: "50%", cursor: "pointer" }}>
        <div className="libBox-mini-dodo">
          {/* 도서관 리스트 띄우기 */}
          <PopOver name={libName} checkedInputs={checkedInputs} setCheckedInputs={setCheckedInputs} />
        </div>
      </div>
    </div>
  );
};

export default MiniLib;
