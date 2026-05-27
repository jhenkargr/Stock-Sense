import React from "react";
import { Outlet } from "react-router-dom";
import BackgroundOverlay from "../components/BackgroundOverlay";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function AppLayout() {
  return (
    <>
      <BackgroundOverlay />
      <Header />

      <div className="pt-24 md:pt-28">
        <Outlet />
      </div>

      <Footer />
    </>
  );
}
