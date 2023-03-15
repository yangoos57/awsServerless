import mainLogo from "./assets/mainlogo.svg";
import MainFrame from "./modules/mainFrame";
import LibLabel from "./modules/libLabel";
import Search from "./modules/search";
import "./assets/style.css";
import { useState } from "react";

function Logo() {
  // 검색한 키워드 정보
  const [keyword, setKeyword] = useState([]);
  // 선택한 도서관 정보
  const [libInfo, setLibInfo] = useState([]);

  // 정보종합
  const values = { keyword: keyword, library: libInfo };

  return (
    <div className="flex-container flex-column mx-auto fade-in-box-dodo" style={{ width: "80%" }}>
      <div className="d-flex mx-auto align-items-end" style={{ flexBasis: "35%" }}>
        <img className="titleLogo" src={mainLogo} alt="" />
      </div>
      <div className="flex-container mx-auto mb-2" style={{ flexBasis: "10%" }}>
        <Search
          placeholder="찾고자 하는 도서 키워드를 검색하세요. ex) 파이썬, SQL"
          setCheckedInputs={setKeyword}
          values={values}
        />
      </div>
      <div className="flex-container mx-auto " style={{ flexBasis: "55%" }}>
        <LibLabel checkedInputs={libInfo} setCheckedInputs={setLibInfo} />
      </div>
    </div>
  );
}

// Main Function
const Main = () => {
  return <MainFrame children={Logo()} />;
};

export default Main;
