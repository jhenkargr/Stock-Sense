import React, { useEffect, useRef } from 'react';

const SpaceBackgroundOverlay = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const starsCount = 140;
    const stars = [];
    let animationFrameId;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = `${window.innerWidth}px`;
      canvas.style.height = `${window.innerHeight}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const createStar = () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      size: Math.random() * 1.2 + 0.4,
      opacity: Math.random() * 0.55 + 0.25,
      twinkleSpeed: Math.random() * 0.02 + 0.005,
      twinkle: Math.random(),
    });

    const updateStar = (star) => {
      star.x += star.vx;
      star.y += star.vy;

      if (star.x < 0) star.x = window.innerWidth;
      if (star.x > window.innerWidth) star.x = 0;
      if (star.y < 0) star.y = window.innerHeight;
      if (star.y > window.innerHeight) star.y = 0;

      star.twinkle += star.twinkleSpeed;
      if (star.twinkle > 1) star.twinkle = 0;
    };

    const drawStar = (star) => {
      const twinkleOpacity = Math.abs(Math.sin(star.twinkle * Math.PI)) * star.opacity;

      ctx.beginPath();
      ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 255, ${twinkleOpacity})`;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(star.x, star.y, star.size * 2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 255, ${twinkleOpacity * 0.18})`;
      ctx.fill();
    };

    const drawNebula = () => {
      const nebula = ctx.createRadialGradient(
        window.innerWidth * 0.25,
        window.innerHeight * 0.2,
        0,
        window.innerWidth * 0.25,
        window.innerHeight * 0.2,
        Math.hypot(window.innerWidth, window.innerHeight) * 0.9
      );
      nebula.addColorStop(0, 'rgba(14, 165, 233, 0.10)');
      nebula.addColorStop(0.5, 'rgba(14, 165, 233, 0.04)');
      nebula.addColorStop(1, 'rgba(5, 10, 15, 0)');
      ctx.fillStyle = nebula;
      ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);
    };

    for (let index = 0; index < starsCount; index += 1) {
      stars.push(createStar());
    }

    const animate = () => {
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

      const background = ctx.createLinearGradient(0, 0, window.innerWidth, window.innerHeight);
      background.addColorStop(0, '#050a0f');
      background.addColorStop(1, '#02060a');
      ctx.fillStyle = background;
      ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

      drawNebula();

      stars.forEach((star) => {
        updateStar(star);
        drawStar(star);
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    resizeCanvas();
    animate();

    const handleResize = () => {
      resizeCanvas();
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-0">
      <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" />

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

export default SpaceBackgroundOverlay;