import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const AnimatedCard = ({ card, index }) => {
  const containerVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
        delay: index * 0.2,
        ease: [0.34, 1.56, 0.64, 1],
      },
    },
  };

  const hoverVariants = {
    hover: {
      y: -10,
      boxShadow: '0 20px 60px rgba(0, 212, 255, 0.3)',
      transition: { duration: 0.3 },
    },
  };

  const gradientVariants = {
    hover: {
      backgroundPosition: '200% center',
      transition: { duration: 0.6, repeat: Infinity, repeatType: 'reverse' },
    },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      whileHover="hover"
      viewport={{ once: true, amount: 0.3 }}
      className="h-full"
    >
      <Link to={card.to} className="block h-full">
        <motion.div
          variants={hoverVariants}
          className={`group relative overflow-hidden rounded-2xl border ${card.border} bg-black/40 backdrop-blur-xl p-8 h-full shadow-[0_0_40px_rgba(0,0,0,0.35)] transition-all duration-300 hover:border-cyan-400/80 cursor-pointer`}
          style={{
            background: 'linear-gradient(135deg, rgba(0,20,40,0.4) 0%, rgba(0,50,80,0.2) 100%)',
          }}
        >
          {/* Animated gradient background */}
          <motion.div
            className={`absolute inset-0 bg-gradient-to-br ${card.accent} opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
            style={{ backgroundPosition: 'center' }}
          />

          {/* Radial glow effect */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(0,212,255,0.15),transparent_60%)] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

          {/* Animated border glow */}
          <div className="absolute inset-0 rounded-2xl border border-cyan-400/0 group-hover:border-cyan-400/30 transition-all duration-500 pointer-events-none" />

          <div className="relative z-10 flex h-full flex-col justify-between gap-8">
            {/* Header */}
            <div className="space-y-4">
              <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                transition={{ delay: 0.2 + index * 0.2, duration: 0.6 }}
                className="inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-gradient-to-r from-cyan-500/20 to-blue-500/10 px-4 py-2 text-[10px] font-black tracking-[0.25em] uppercase text-cyan-200/90 group-hover:border-cyan-300/60 transition-all duration-300"
              >
                {card.title === "AI Based Stock Predictor" ? "🤖 Predict" : "📊 Analyse"}
              </motion.div>

              <motion.h3
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                transition={{ delay: 0.3 + index * 0.2, duration: 0.6 }}
                className="text-4xl font-black tracking-tight text-white uppercase group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-cyan-300 group-hover:to-emerald-300 transition-all duration-300"
              >
                {card.title}
              </motion.h3>

              <motion.p
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                transition={{ delay: 0.4 + index * 0.2, duration: 0.6 }}
                className="text-sm text-cyan-100/75 leading-relaxed max-w-md group-hover:text-cyan-50/90 transition-colors duration-300"
              >
                {card.description}
              </motion.p>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between gap-4 pt-4 border-t border-cyan-400/10 group-hover:border-cyan-400/30 transition-colors duration-300">
              <motion.span
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                transition={{ delay: 0.5 + index * 0.2, duration: 0.6 }}
                className="text-[11px] font-black tracking-[0.3em] uppercase text-cyan-100/60 group-hover:text-cyan-100 transition-colors duration-300"
              >
                {card.to.replace("/", "") || "home"}
              </motion.span>

              <motion.div
                whileHover={{ scale: 1.05, x: 5 }}
                className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-gradient-to-r from-cyan-500/20 to-blue-500/10 px-5 py-2 text-[11px] font-black tracking-[0.22em] uppercase text-cyan-100 group-hover:border-cyan-300/60 group-hover:bg-cyan-400/20 transition-all duration-300"
              >
                {card.button}
                <motion.span
                  animate={{ x: [0, 5, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  aria-hidden="true"
                >
                  →
                </motion.span>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </Link>
    </motion.div>
  );
};

export default AnimatedCard;
