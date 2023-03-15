import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import mainLogo from "./assets/mainlogo.svg";
import MainFrame from "./modules/mainFrame";
function Init() {
  const navigate = useNavigate();
  useEffect(() => {
    setTimeout(() => navigate("main"), 1000);
  }, [navigate]);

  return (
    <>
      <div className="flex-column flex-container">
        <div className="m-auto">
          <div className="d-flex btTitle">
            <img className="titleLogo fade-out-box-dodo" src={mainLogo} alt="" />
          </div>
        </div>
      </div>
    </>
  );
}
// Main Function
const Main = () => {
  return <MainFrame children={Init()} />;
};

export default Main;
