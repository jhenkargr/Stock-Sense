import React from 'react';
import { motion } from 'framer-motion';

const AnimatedHero = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: 'easeOut' },
    },
  };

  const titleVariants = {
    hidden: { opacity: 0, y: 40, scale: 0.95 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: { duration: 1, ease: [0.34, 1.56, 0.64, 1] },
    },
  };

  const gradientVariants = {
    animate: {
      backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
      transition: {
        duration: 8,
        repeat: Infinity,
        repeatType: 'loop',
      },
    },
  };

  return (
    <motion.section
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="text-center max-w-5xl mx-auto mt-16 md:mt-24"
    >
      {/* Label */}
      <motion.div variants={itemVariants} className="mb-8">
        <motion.p
          className="text-[10px] md:text-xs tracking-[0.5em] uppercase font-black bg-gradient-to-r from-cyan-400 via-blue-400 to-emerald-400 bg-clip-text text-transparent"
          style={{
            backgroundSize: '200% 200%',
          }}
          animate={{
            backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            repeatType: 'loop',
          }}
        >
          REAL-TIME MARKET INTELLIGENCE
        </motion.p>
      </motion.div>

      {/* Main Title */}
      <motion.div variants={titleVariants} className="mb-8 perspective">
        <div className="relative inline-block">
          {/* Glowing background effect */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-cyan-500/30 to-emerald-500/30 blur-3xl rounded-full"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              repeatType: 'loop',
            }}
          />

          <h2 className="text-6xl md:text-8xl lg:text-9xl font-black tracking-tighter leading-none uppercase text-white relative z-10">
            Decode the{' '}
            <motion.span
              className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-emerald-400"
              style={{
                backgroundSize: '200% 200%',
              }}
              variants={gradientVariants}
              animate="animate"
              whileHover={{
                scale: 1.05,
                textShadow: '0 0 30px rgba(0, 212, 255, 0.8)',
              }}
            >
              Market
            </motion.span>
          </h2>
        </div>
      </motion.div>

      {/* Description */}
      <motion.div variants={itemVariants} className="max-w-2xl mx-auto mt-8">
        <motion.p
          className="text-sm md:text-lg text-cyan-100/70 tracking-wide leading-relaxed"
          whileHover={{ color: 'rgba(0, 212, 255, 0.9)' }}
        >
          Harness AI-powered predictions and deep-dive fundamentals analysis. Pick your workflow:
          <motion.span
            className="block mt-2 font-bold text-cyan-300"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            forecast tomorrow's movement or dissect today's opportunities
          </motion.span>
        </motion.p>
      </motion.div>


    </motion.section>
  );
};

export default AnimatedHero;
