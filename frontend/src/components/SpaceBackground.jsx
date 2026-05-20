import React, { useEffect, useRef } from 'react';

const SpaceBackground = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;

    // Set canvas size
    canvas.width = window.innerWidth * dpr;
    canvas.height = window.innerHeight * dpr;
    ctx.scale(dpr, dpr);

    // Create gradient background for space effect
    const createSpaceBackground = () => {
      const gradient = ctx.createRadialGradient(
        window.innerWidth / 2,
        window.innerHeight / 2,
        0,
        window.innerWidth / 2,
        window.innerHeight / 2,
        Math.hypot(window.innerWidth, window.innerHeight)
      );
      gradient.addColorStop(0, '#0a1428');
      gradient.addColorStop(0.5, '#050a12');
      gradient.addColorStop(1, '#000000');
      return gradient;
    };

    // Create stars/particles
    const starsCount = 80;
    const stars = [];

    // Star constructor function (not a class)
    const createStar = () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      vx: (Math.random() - 0.5) * 0.8,
      vy: (Math.random() - 0.5) * 0.8,
      size: Math.random() * 1.5 + 0.3,
      opacity: Math.random() * 0.7 + 0.3,
      twinkleSpeed: Math.random() * 0.02 + 0.005,
      twinkle: Math.random(),
    });

    const updateStar = (star) => {
      // Move star
      star.x += star.vx;
      star.y += star.vy;

      // Wrap around edges
      if (star.x < 0) star.x = window.innerWidth;
      if (star.x > window.innerWidth) star.x = 0;
      if (star.y < 0) star.y = window.innerHeight;
      if (star.y > window.innerHeight) star.y = 0;

      // Twinkling effect
      star.twinkle += star.twinkleSpeed;
      if (star.twinkle > 1) star.twinkle = 0;
    };

    const drawStar = (star) => {
      // Calculate twinkling opacity
      const twinkleOpacity = Math.abs(Math.sin(star.twinkle * Math.PI)) * star.opacity;

      // Draw star as small dot with glow
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 255, ${twinkleOpacity})`;
      ctx.fill();

      // Add glow effect
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.size * 2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(100, 150, 255, ${twinkleOpacity * 0.3})`;
      ctx.fill();
    };

    // Initialize stars
    for (let i = 0; i < starsCount; i++) {
      stars.push(createStar());
    }

    let animationFrameId;
    let frameCount = 0;

    // Animation loop
    const animate = () => {
      frameCount++;

      // Draw space background
      const gradient = createSpaceBackground();
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

      // Draw a subtle nebula effect
      const nebula = ctx.createRadialGradient(
        window.innerWidth * 0.3,
        window.innerHeight * 0.3,
        0,
        window.innerWidth * 0.3,
        window.innerHeight * 0.3,
        Math.hypot(window.innerWidth, window.innerHeight) * 0.8
      );
      nebula.addColorStop(0, 'rgba(100, 150, 255, 0.05)');
      nebula.addColorStop(0.5, 'rgba(100, 100, 200, 0.02)');
      nebula.addColorStop(1, 'rgba(50, 50, 100, 0)');
      ctx.fillStyle = nebula;
      ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

      // Update and draw stars
      stars.forEach((star) => {
        updateStar(star);
        drawStar(star);
      });

      // Draw occasional shooting stars (every 3-5 seconds)
      if (frameCount % 150 === 0) {
        drawShootingStar();
      }

      animationFrameId = requestAnimationFrame(animate);
    };

    const drawShootingStar = () => {
      const startX = Math.random() * window.innerWidth;
      const startY = Math.random() * window.innerHeight * 0.5;
      const endX = startX + Math.random() * 200 - 100;
      const endY = startY + Math.random() * 100 + 100;

      ctx.beginPath();
      ctx.moveTo(startX, startY);
      ctx.lineTo(endX, endY);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Fade trail
      ctx.beginPath();
      ctx.moveTo(startX, startY);
      ctx.lineTo(endX, endY);
      ctx.strokeStyle = 'rgba(100, 150, 255, 0.3)';
      ctx.lineWidth = 4;
      ctx.stroke();
    };

    animate();

    // Handle resize
    const handleResize = () => {
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      ctx.scale(dpr, dpr);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed top-0 left-0 w-full h-full -z-10"
      style={{
        background: 'linear-gradient(135deg, #0a1428 0%, #050a12 50%, #000000 100%)',
      }}
    />
  );
};

export default SpaceBackground;
