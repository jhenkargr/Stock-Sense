import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./template/Home";
import AppLayout from "./template/AppLayout";
import AnalysePage from "./template/AnalysePage";
import PredictPage from "./template/PredictPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/analyse" element={<AnalysePage />} />
          <Route path="/predict" element={<PredictPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
