'use client';

import React, { useState, useEffect } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

interface NavbarProps {
  onMenuToggle: () => void;
  isMenuOpen: boolean;
  onAuthClick: (mode: 'login' | 'signup') => void;
  isAuthenticated: boolean | null;
  onDashboardClick: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onMenuToggle,
  isMenuOpen,
  onAuthClick,
  isAuthenticated,
  onDashboardClick
}) => {
  const { scrollY } = useScroll();
  const [hasScrolled, setHasScrolled] = useState(false);

  // Transition navbar styles on scroll
  useEffect(() => {
    return scrollY.onChange((latest) => {
      setHasScrolled(latest > 50);
    });
  }, [scrollY]);

  // Framer motion variants for the morphing Hamburger lines
  const line1Variants = {
    closed: { rotate: 0, y: 0 },
    opened: { rotate: 45, y: 5 },
  };

  const line2Variants = {
    closed: { opacity: 1, scale: 1 },
    opened: { opacity: 0, scale: 0 },
  };

  const line3Variants = {
    closed: { rotate: 0, y: 0 },
    opened: { rotate: -45, y: -5 },
  };

  return (
    <motion.header
      initial={{ y: -30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-6 left-0 right-0 z-40 px-4 md:px-8 max-w-[96vw] mx-auto pointer-events-none"
    >
      <div
        className={`w-full flex items-center justify-between py-3 px-6 rounded-full border transition-all duration-500 pointer-events-auto ${
          hasScrolled
            ? 'bg-slate-950/45 backdrop-blur-xl border-white/[0.06] shadow-[0_10px_30px_-15px_rgba(0,0,0,0.7)]'
            : 'bg-transparent border-transparent'
        }`}
      >
        {/* LEFT: Premium Morphing Menu Toggle & Nav Links */}
        <div className="flex items-center gap-6">
          <button
            onClick={onMenuToggle}
            className="flex items-center justify-center p-2.5 rounded-full bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.05] hover:border-white/[0.1] text-slate-300 hover:text-white transition-all group relative cursor-pointer"
            aria-label="Toggle command drawer"
          >
            <svg width="18" height="12" viewBox="0 0 18 12" fill="none" className="stroke-current stroke-[1.8] stroke-round">
              <motion.path
                d="M 2 2 L 16 2"
                variants={line1Variants}
                animate={isMenuOpen ? 'opened' : 'closed'}
                transition={{ duration: 0.25 }}
              />
              <motion.path
                d="M 2 6 L 16 6"
                variants={line2Variants}
                animate={isMenuOpen ? 'opened' : 'closed'}
                transition={{ duration: 0.25 }}
              />
              <motion.path
                d="M 2 10 L 16 10"
                variants={line3Variants}
                animate={isMenuOpen ? 'opened' : 'closed'}
                transition={{ duration: 0.25 }}
              />
            </svg>
          </button>

          <nav className="hidden lg:flex items-center gap-6">
            <button className="text-xs font-mono text-slate-400 hover:text-white hover:-translate-y-0.5 transition-all cursor-pointer relative py-1 group">
              Platform
              <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-indigo-500 group-hover:w-full transition-all duration-300" />
            </button>
            <button className="text-xs font-mono text-slate-400 hover:text-white hover:-translate-y-0.5 transition-all cursor-pointer relative py-1 group">
              AI Agents
              <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-indigo-500 group-hover:w-full transition-all duration-300" />
            </button>
            <button className="text-xs font-mono text-slate-400 hover:text-white hover:-translate-y-0.5 transition-all cursor-pointer relative py-1 group">
              Workflows
              <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-indigo-500 group-hover:w-full transition-all duration-300" />
            </button>
            <button className="text-xs font-mono text-slate-400 hover:text-white hover:-translate-y-0.5 transition-all cursor-pointer relative py-1 group">
              Pricing
              <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-indigo-500 group-hover:w-full transition-all duration-300" />
            </button>
          </nav>
        </div>

        {/* CENTER: Intentionally Empty for Visual focus */}
        <div className="hidden md:block flex-1" />

        {/* RIGHT: User Navigation Actions */}
        <div className="flex items-center gap-4">
          {!isAuthenticated ? (
            <>
              <button
                onClick={() => onAuthClick('login')}
                className="text-xs font-mono font-medium text-slate-400 hover:text-white transition-colors py-2 px-4 cursor-pointer"
              >
                Log In
              </button>
              
              <button
                onClick={() => onAuthClick('signup')}
                className="relative py-2 px-5 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-semibold text-xs tracking-wider transition-all duration-300 shadow-md shadow-indigo-500/20 flex items-center justify-center gap-1 group overflow-hidden cursor-pointer"
              >
                <span className="relative z-10">Try for Free</span>
                <span className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
            </>
          ) : (
            <button
              onClick={onDashboardClick}
              className="relative py-2 px-5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 hover:text-white hover:bg-indigo-500/20 font-semibold text-xs tracking-wider transition-all duration-300 flex items-center justify-center gap-1 cursor-pointer"
            >
              Open Workspace
            </button>
          )}
        </div>
      </div>
    </motion.header>
  );
};
