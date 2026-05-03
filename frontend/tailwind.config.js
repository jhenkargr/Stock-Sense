/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ['"Share Tech Mono"', 'monospace'],
        display: ['"Orbitron"', 'sans-serif'],
        body: ['"Rajdhani"', 'sans-serif'],
      },
      colors: {
        bg: '#050a0f',
        panel: '#080f18',
        border: '#0d2235',
        'border-glow': '#0a4a7a',
        accent: '#00d4ff',
        accent2: '#00ff9d',
        accent3: '#ff6b35',
        warn: '#ffcc00',
        danger: '#ff3860',
        muted: '#3a5a72',
        'text-base': '#c8e6f5',
      },
      animation: {
        pulse_dot: 'pulse_dot 1.5s ease-in-out infinite',
        spin_slow: 'spin 0.8s linear infinite',
        fadeUp: 'fadeUp 0.5s ease forwards',
        blink: 'blink 1s step-end infinite',
        'bar-grow': 'barGrow 1s cubic-bezier(0.25,1,0.5,1) forwards',
      },
      keyframes: {
        pulse_dot: {
          '0%,100%': { opacity: 1, transform: 'scale(1)' },
          '50%': { opacity: 0.4, transform: 'scale(0.8)' },
        },
        fadeUp: {
          from: { opacity: 0, transform: 'translateY(24px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        blink: {
          '0%,100%': { opacity: 1 },
          '50%': { opacity: 0.3 },
        },
        barGrow: {
          from: { width: '0%' },
          to: { width: 'var(--bar-w)' },
        },
      },
      backgroundImage: {
        'grid-pattern':
          'linear-gradient(rgba(0,212,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.04) 1px, transparent 1px)',
      },
      backgroundSize: {
        'grid-40': '40px 40px',
      },
    },
  },
  plugins: [],
}
