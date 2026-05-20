import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const ThreeDBackground = () => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x000000, 0);
    containerRef.current.appendChild(renderer.domElement);
    camera.position.z = 5;

    // Create floating particles (stock market inspired)
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCnt = 150;
    const posArray = new Float32Array(particlesCnt * 3);

    for (let i = 0; i < particlesCnt * 3; i += 3) {
      posArray[i] = (Math.random() - 0.5) * 2000;
      posArray[i + 1] = (Math.random() - 0.5) * 2000;
      posArray[i + 2] = (Math.random() - 0.5) * 2000;
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

    const particlesMaterial = new THREE.PointsMaterial({
      size: 5,
      color: 0x00d4ff,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.6,
    });

    const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particlesMesh);

    // Create candlestick-like structures
    const candlesticks = [];
    for (let i = 0; i < 8; i++) {
      const group = new THREE.Group();
      
      // Candlestick body
      const bodyGeometry = new THREE.BoxGeometry(40, Math.random() * 200 + 100, 40);
      const isUp = Math.random() > 0.5;
      const bodyMaterial = new THREE.MeshPhongMaterial({
        color: isUp ? 0x00ff88 : 0xff4444,
        wireframe: false,
        transparent: true,
        opacity: 0.3,
        emissive: isUp ? 0x00ff88 : 0xff4444,
        emissiveIntensity: 0.3,
      });
      
      const candle = new THREE.Mesh(bodyGeometry, bodyMaterial);
      group.add(candle);
      
      // Wick line
      const wickGeometry = new THREE.BufferGeometry();
      const wickPositions = new Float32Array([
        0, -60, 0,
        0, 80, 0,
      ]);
      wickGeometry.setAttribute('position', new THREE.BufferAttribute(wickPositions, 3));
      const wickMaterial = new THREE.LineBasicMaterial({
        color: isUp ? 0x00ff88 : 0xff4444,
        transparent: true,
        opacity: 0.5,
      });
      const wick = new THREE.Line(wickGeometry, wickMaterial);
      group.add(wick);
      
      group.position.x = (i - 4) * 200;
      group.position.y = Math.sin(i) * 150;
      group.position.z = -500;
      
      candlesticks.push({
        group,
        isUp,
        originalY: candle.position.y,
        candle,
      });
      
      scene.add(group);
    }

    // Create animated chart lines
    const lines = [];
    for (let i = 0; i < 3; i++) {
      const points = [];
      for (let j = 0; j < 30; j++) {
        points.push(
          new THREE.Vector3(
            (j - 15) * 50,
            Math.sin(j * 0.3 + i) * 100,
            -300 + i * 100
          )
        );
      }
      
      const curve = new THREE.CatmullRomCurve3(points);
      const geometry = new THREE.BufferGeometry().setFromPoints(
        curve.getPoints(100)
      );
      
      const colors = [
        0x00d4ff,
        0x00ff88,
        0xff6b00,
      ];
      
      const material = new THREE.LineBasicMaterial({
        color: colors[i],
        transparent: true,
        opacity: 0.4,
        linewidth: 2,
      });
      
      const line = new THREE.Line(geometry, material);
      lines.push({ line, points, color: colors[i], offset: i });
      scene.add(line);
    }

    // Create dollar sign symbols
    const dollarSigns = [];
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#00d4ff';
    ctx.font = 'bold 40px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('$', 32, 32);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true, opacity: 0.5 });
    
    for (let i = 0; i < 6; i++) {
      const sprite = new THREE.Sprite(spriteMaterial.clone());
      sprite.scale.set(100, 100, 1);
      sprite.position.set(
        (Math.random() - 0.5) * 1200,
        (Math.random() - 0.5) * 800,
        Math.random() * -400 - 200
      );
      dollarSigns.push(sprite);
      scene.add(sprite);
    }

    // Add lighting
    const light = new THREE.PointLight(0x00d4ff, 1, 2000);
    light.position.set(500, 500, 500);
    scene.add(light);

    const light2 = new THREE.PointLight(0x00ff88, 0.8, 2000);
    light2.position.set(-500, -500, 500);
    scene.add(light2);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
    scene.add(ambientLight);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);

      const time = Date.now() * 0.0005;

      // Rotate particles
      particlesMesh.rotation.x += 0.00005;
      particlesMesh.rotation.y += 0.00008;

      // Animate candlesticks
      candlesticks.forEach((stick, index) => {
        stick.group.rotation.y += 0.001;
        stick.group.position.y += Math.sin(time + index * 0.5) * 0.05;
        
        // Pulse effect
        const scale = 1 + Math.sin(time * 2 + index) * 0.1;
        stick.group.scale.set(scale, scale, scale);
      });

      // Animate chart lines
      lines.forEach((lineData, idx) => {
        lineData.line.rotation.z += 0.0003;
        lineData.line.position.y += Math.sin(time + idx) * 0.02;
      });

      // Animate dollar signs
      dollarSigns.forEach((dollar, index) => {
        dollar.position.y += Math.sin(time + index * 0.7) * 0.3;
        dollar.rotation.z += 0.005;
        dollar.scale.set(
          100 + Math.cos(time + index) * 20,
          100 + Math.cos(time + index) * 20,
          1
        );
      });

      renderer.render(scene, camera);
    };

    animate();

    // Handle window resize
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="fixed top-0 left-0 w-full h-full -z-10"
      style={{
        background: 'radial-gradient(ellipse at center, rgba(0,20,40,0.9) 0%, rgba(0,0,0,1) 100%)',
      }}
    />
  );
};

export default ThreeDBackground;
