'use client';

import React from 'react';
import { motion, Variants } from 'framer-motion';

interface AgentXLoaderProps {
  onComplete?: () => void;
}

export const AgentXLoader: React.FC<AgentXLoaderProps> = () => {
  const letters = 'AGENTX'.split('');

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.1,
      },
    },
    exit: {
      opacity: 0,
      scale: 1.05,
      filter: 'blur(10px)',
      transition: { duration: 0.6 }
    }
  };

  const letterVariants: Variants = {
    hidden: { opacity: 0, y: 20, filter: 'blur(8px)' },
    visible: {
      opacity: 1,
      y: 0,
      filter: 'blur(0px)',
      transition: { duration: 0.5 }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-zinc-950 text-white select-none overflow-hidden"
    >
      {/* Background ambient radial glow */}
      <div className="absolute w-[500px] h-[500px] rounded-full bg-gradient-to-tr from-indigo-600/20 via-purple-600/10 to-transparent blur-3xl pointer-events-none animate-pulse" />

      {/* Main Centered Logo Reveal */}
      <div className="relative flex items-center justify-center">
        <div className="flex items-center text-5xl md:text-7xl font-extrabold tracking-[0.25em] text-white">
          {letters.map((char, index) => (
            <motion.span
              key={index}
              variants={letterVariants}
              className={char === 'X' ? 'text-indigo-400 font-black drop-shadow-[0_0_25px_rgba(99,102,241,0.6)]' : 'text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.15)]'}
            >
              {char}
            </motion.span>
          ))}
        </div>
      </div>

      {/* Subtitle / System Initialization Indicator */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.5 }}
        className="mt-6 flex items-center gap-3 text-xs tracking-widest text-zinc-400 font-mono uppercase"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-ping" />
        <span>INITIALIZING AGENTX AI OS</span>
      </motion.div>
    </motion.div>
  );
};
