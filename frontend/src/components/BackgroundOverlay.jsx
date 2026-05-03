import React from 'react';

const BackgroundOverlay = () => {
  return (
    <div className="fixed inset-0 pointer-events-none z-0">
      {/* Grid */}
      <div
        className="absolute inset-0 opacity-[0.15]"
        style={{
          backgroundImage:
            'linear-gradient(#0ea5e9 1px, transparent 1px), linear-gradient(90deg, #0ea5e9 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }}
      />
      {/* Fade to bottom */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#050b0f]/50 to-[#050b0f]" />
      {/* Scanlines */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage:
            'repeating-linear-gradient(0deg, #fff, #fff 1px, transparent 1px, transparent 2px)',
          backgroundSize: '100% 3px',
        }}
      />
    </div>
  );
};

export default BackgroundOverlay;
