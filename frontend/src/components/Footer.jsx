import React from 'react';

const Footer = () => {
  return (
    <footer className="fixed bottom-0 left-0 right-0 z-50 p-8 pointer-events-none">
      <div className="max-w-6xl mx-auto flex justify-center opacity-30">
        <p className="text-[10px] text-cyan-800 tracking-[0.4em] uppercase font-black text-center whitespace-nowrap">
          STOCKSENSE // FOR EDUCATIONAL PURPOSES ONLY · NOT FINANCIAL ADVICE · DATA IS SIMULATED
        </p>
      </div>
    </footer>
  );
};

export default Footer;
