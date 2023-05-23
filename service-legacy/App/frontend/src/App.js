import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import Init from "./components/init";
import Main from "./components/main";
import Result from "./components/result";

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Init />}></Route>
        <Route path="/main" element={<Main />}></Route>
        <Route path="/searchresult" element={<Result />}></Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
