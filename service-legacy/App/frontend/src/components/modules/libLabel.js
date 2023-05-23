import React, { useEffect } from "react";

const libNames = [
  "도서관전체",
  "강남도서관",
  "강동도서관",
  "강서도서관",
  "개포도서관",
  "고덕학습관",
  "고척도서관",
  "구로도서관",
  "남산도서관",
  "노원학습관",
  "도봉도서관",
  "동대문도서관",
  "동작도서관",
  "마포학습관",
  "서대문도서관",
  "송파도서관",
  "양천도서관",
  "영등포도서관",
  "용산도서관",
  "정독도서관",
  "종로도서관",
];

//checkBox 생성 함수
function CustomInput(libName, idx, setCheckedInputs, checkedInputs) {
  //check관리 함수
  const changeHandler = (checked, id) => {
    if (checked) {
      id === "도서관전체" ? setCheckedInputs([...libNames.slice(1)]) : setCheckedInputs([...checkedInputs, id]);
    } else {
      // 체크 해제
      id === "도서관전체" ? initializeAll() : initializeItem(id);
    }
  };

  // 전부 체크 해제
  const initializeAll = () => {
    document.querySelectorAll('input[type="checkbox"]').forEach((el) => (el.checked = false));
    setCheckedInputs([]);
  };

  // 특정 id만 체크 해제
  const initializeItem = (id) => {
    if (checkedInputs.length < 21) {
      // 21개 미만인 경우 "도서관 전체" 제거
      document.querySelector('input[type="checkbox"]').checked = false;
    }
    setCheckedInputs(checkedInputs.filter((el) => el !== id));
  };
  return (
    <div className="ms-sm-3 libNameCover" key={idx}>
      <input
        type="checkbox"
        className="css-checkbox "
        id={libName}
        onChange={(e) => {
          changeHandler(e.target.checked, e.target.id);
        }}
      />
      <label for={libName} className="css-label lite-gray-check libName" name="checkbox1_lbl">
        {libName}
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
            {libNames.map((val, i) => {
              return CustomInput(val, i, setCheckedInputs, checkedInputs);
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LibLabel;
