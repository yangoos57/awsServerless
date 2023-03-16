import React, { useEffect } from "react";

const libName1 = ["전체도서관", "강남도서관", "강동도서관", "강서도서관", "개포도서관", "고덕학습관", "고척도서관"];

const libName2 = ["구로도서관", "남산도서관", "노원학습관", "도봉도서관", "동대문도서관", "동작도서관", "마포학습관"];

const libName3 = ["서대문도서관", "송파도서관", "양천도서관", "영등포도서관", "용산도서관", "정독도서관", "종로도서관"];

//checkBox 생성 함수
function CustomInput(v, i, setCheckedInputs, checkedInputs) {
  //check관리 함수
  const changeHandler = (checked, id) => {
    if (checked) {
      setCheckedInputs([...checkedInputs, id]);
    } else {
      // 체크 해제
      setCheckedInputs(checkedInputs.filter((el) => el !== id));
    }
  };
  return (
    <div className="ms-sm-3 libNameCover" key={i}>
      <input
        type="checkbox"
        className="css-checkbox "
        id={v}
        onChange={(e) => {
          changeHandler(e.target.checked, e.target.id);
        }}
      />
      <label for={v} className="css-label lite-gray-check libName" name="checkbox1_lbl">
        {v}
      </label>
    </div>
  );
}

const LibLabel = ({ checkedInputs, setCheckedInputs }) => {
  // 값 유지시키기
  useEffect(() => {
    checkedInputs.map((e) => {
      return (document.getElementById(e).checked = true);
    });
  });
  return (
    <div className="mx-auto libBox-dodo flex-column ">
      <div className="libBox-title-dodo" style={{ flexBasis: "18%" }}>
        <div className="m-auto libTitle">도서관을 선택하세요</div>
      </div>
      <div className="libBox-names-dodo">
        <div className="flex-container justify-content-evenly">
          <div className="d-flex flex-column libBox-names-column">
            {libName1.map((val, i) => {
              return CustomInput(val, i, setCheckedInputs, checkedInputs);
            })}
          </div>
          <div className="d-flex flex-column libBox-names-column">
            {libName2.map((val, i) => {
              return CustomInput(val, i + 100, setCheckedInputs, checkedInputs);
            })}
          </div>
          <div className="d-flex flex-column libBox-names-column">
            {libName3.map((val, i) => {
              return CustomInput(val, i + 100, setCheckedInputs, checkedInputs);
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LibLabel;
