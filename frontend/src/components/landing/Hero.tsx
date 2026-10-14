'use client';

import React, { useRef, useState } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

import { ShinyText } from '../ui/ShinyText';

export const Hero: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Tracking page scroll for subtle parallax offsets
  const { scrollY } = useScroll();
  const yParallax = useTransform(scrollY, [0, 400], [0, 60]);
  const opacityParallax = useTransform(scrollY, [0, 300], [1, 0]);

  // Track cursor position to trigger interactive radial lighting glow
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    setMousePosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      className="relative min-h-screen w-full flex flex-col items-center justify-center bg-zinc-950 overflow-hidden"
    >
      {/* Background visual layers */}
      <div className="absolute inset-0 animated-grid pointer-events-none opacity-25" />
      
      {/* Cursor Light Effect follower */}
      <div
        className="absolute inset-0 pointer-events-none transition-all duration-300 opacity-40"
        style={{
          background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(99, 102, 241, 0.08), transparent 80%)`,
        }}
      />

      {/* Ambient static glow orb */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[550px] bg-indigo-500/5 rounded-full blur-[130px] pointer-events-none" />

      {/* Center typography stack wrapped in motion */}
      <motion.div
        style={{ y: yParallax, opacity: opacityParallax }}
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 text-center max-w-4xl px-6 flex flex-col items-center justify-center select-none"
      >
        {/* Large Centered Title */}
        <h1 className="text-8xl md:text-9xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white via-slate-200 to-slate-400 select-none leading-normal pb-4 flex items-center justify-center">
          Agent
          <ShinyText 
            text="X" 
            color="#6366f1" 
            shineColor="#ffffff" 
            speed={2.5} 
            className="font-extrabold"
          />
        </h1>

        {/* Elegant Tagline */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 1 }}
          className="mt-6 text-base md:text-xl font-mono tracking-[0.2em] uppercase"
        >
          <ShinyText text="The Future of Multi-Agent Intelligence" speed={3.5} color="#818cf8" shineColor="#ffffff" />
        </motion.div>

        {/* Core Subtitle Description */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.5 }}
          transition={{ delay: 0.6, duration: 1 }}
          className="mt-4 text-xs md:text-sm font-medium text-slate-300 tracking-wider"
        >
          Build • Orchestrate • Automate • Scale Intelligent AI Agents
        </motion.p>
      </motion.div>
    </div>
  );
};
