import React from "react";
import "../assets/style.css";

const MainFrame = ({ children }) => {
  return (
    <div className="wrap">
      <div className="header d-flex justify-content-center"></div>
      <div className="content">
        <div className="main">
          <div className="whole-dodo d-flex ">
            <div className="main-dodo m-auto ">
              <div className="flex-column flex-container">{children}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainFrame;
