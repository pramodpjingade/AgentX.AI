'use client';

import React from 'react';
import { motion, useReducedMotion, Variants } from 'framer-motion';
import { Activity } from 'lucide-react';
import { NeuralBackground } from './ui/neural-background';

interface SplashScreenProps {}

export const SplashScreen: React.FC<SplashScreenProps> = () => {
  const shouldReduceMotion = useReducedMotion();

  // Typography characters for staggered animations
  const brandName = "Agent".split("");
  const brandSuffix = "X";

  // Stagger container animation
  const containerVariants: Variants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.1,
      },
    },
  };

  // Letter animations
  const letterVariants: Variants = {
    hidden: { 
      opacity: 0, 
      y: shouldReduceMotion ? 0 : 15,
      filter: shouldReduceMotion ? "none" : "blur(4px)"
    },
    visible: {
      opacity: 1,
      y: 0,
      filter: "none",
      transition: {
        type: "spring",
        damping: 15,
        stiffness: 100,
      },
    },
  };

  return (
    <motion.div
      initial={{ opacity: 1 }}
      exit={{ 
        opacity: 0,
        scale: shouldReduceMotion ? 1 : 0.98,
        filter: shouldReduceMotion ? "none" : "blur(10px)",
        transition: { duration: 0.5, ease: [0.32, 0.94, 0.6, 1] }
      }}
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-zinc-950 text-white overflow-hidden select-none"
    >
      {/* Background visual styles identical to dashboard */}
      <div className="absolute inset-0 animated-grid pointer-events-none opacity-20" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/5 rounded-full blur-[140px] pointer-events-none" />
      <NeuralBackground />

      {/* Center Layout Container */}
      <div className="relative z-10 flex flex-col items-center max-w-sm w-full text-center px-6">
        
        {/* Animated Brand Logo Icon */}
        <motion.div
          initial={{ opacity: 0, scale: shouldReduceMotion ? 1 : 0.8, filter: shouldReduceMotion ? "none" : "blur(8px)" }}
          animate={{ 
            opacity: 1, 
            scale: 1, 
            filter: "none",
            y: shouldReduceMotion ? 0 : [0, -6, 0]
          }}
          transition={{
            opacity: { duration: 0.6 },
            scale: { duration: 0.6 },
            filter: { duration: 0.6 },
            y: {
              repeat: Infinity,
              duration: 4,
              ease: "easeInOut"
            }
          }}
          className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-indigo-500/35 border border-white/10 mb-6"
        >
          <motion.div
            animate={{ rotate: shouldReduceMotion ? 0 : 360 }}
            transition={{
              repeat: Infinity,
              duration: 12,
              ease: "linear"
            }}
          >
            <Activity className="w-8 h-8 text-white" />
          </motion.div>
        </motion.div>

        {/* Brand Name Header with Staggered Letters */}
        <motion.h2 
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="text-4xl font-bold tracking-wide flex items-center justify-center agentx-brand text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-indigo-400"
        >
          {brandName.map((char, index) => (
            <motion.span 
              key={index} 
              variants={letterVariants}
              className="inline-block"
            >
              {char}
            </motion.span>
          ))}
          <motion.span 
            variants={letterVariants}
            className="text-indigo-500 inline-block font-black ml-0.5"
          >
            {brandSuffix}
          </motion.span>
        </motion.h2>

      </div>
    </motion.div>
  );
};
