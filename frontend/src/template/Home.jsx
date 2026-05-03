import Header from "../Components/Header";
import Footer from "../Components/Footer";
import BackgroundOverlay from "../components/BackgroundOverlay"
import Loadingindicator from "../components/Loadingindicator"
import SearchBar from "../components/SearchBar"
import Hero from "../components/Hero"

import React from "react";

export default function App(){
    return(
        <div className="dr">
            
            <main>
                <Hero/>
                <SearchBar/>
            </main>
            
        </div>
    )
}