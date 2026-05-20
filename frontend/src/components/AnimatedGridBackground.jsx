import React from 'react';

const AnimatedGridBackground = () => {
  return (
    <div className="fixed inset-0 -z-10 bg-[#050a0f]">
      <div className="absolute inset-0 bg-grid pointer-events-none z-0" />
    </div>
  );
};

export default AnimatedGridBackground;
