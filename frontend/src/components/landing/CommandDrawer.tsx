'use client';

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Search, 
  LayoutDashboard, 
  Compass, 
  ShoppingBag, 
  FileCode, 
  Cpu, 
  Terminal, 
  HelpCircle, 
  Settings, 
  Bell, 
  BookOpen, 
  Users, 
  MapPin, 
  Activity,
  FileText
} from 'lucide-react';

interface CommandDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (view: string) => void;
  onAuthClick: (mode: 'login' | 'signup') => void;
  isAuthenticated: boolean | null;
}

export const CommandDrawer: React.FC<CommandDrawerProps> = ({
  isOpen,
  onClose,
  onNavigate,
  onAuthClick,
  isAuthenticated
}) => {
  // Listen for escape key to close drawer
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  const menuSections = [
    {
      title: "Core Platform",
      items: [
        { name: "Platform Overview", icon: Compass, action: () => onNavigate('overview') },
        { name: "AI Marketplace", icon: ShoppingBag, action: () => onNavigate('plugins') },
        { name: "Workflow Templates", icon: Cpu, action: () => onNavigate('workflows') },
      ]
    },
    {
      title: "Developer Portal",
      items: [
        { name: "API Documentation", icon: Terminal, action: () => {} },
        { name: "System Status", icon: Activity, action: () => {} },
        { name: "Platform Roadmap", icon: MapPin, action: () => {} },
      ]
    },
    {
      title: "Community & Support",
      items: [
        { name: "Developer Forum", icon: Users, action: () => {} },
        { name: "Help & Documentation", icon: HelpCircle, action: () => {} },
        { name: "Contact Operator", icon: FileText, action: () => {} },
      ]
    }
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Frosted Glass Backdrop Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-md"
          />

          {/* Command Drawer Sidebar */}
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 220 }}
            className="fixed top-0 bottom-0 left-0 w-80 max-w-full z-50 bg-slate-950/80 border-r border-white/[0.06] backdrop-blur-2xl p-6 flex flex-col justify-between overflow-y-auto"
            role="dialog"
            aria-label="AI Command Menu"
          >
            <div className="space-y-6">
              {/* Header section with Close button */}
              <div className="flex items-center justify-between pb-4 border-b border-white/[0.05]">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center">
                    <Activity className="w-3.5 h-3.5 text-white" />
                  </div>
                  <span className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
                    Agent<span className="text-indigo-400">X</span> Command
                  </span>
                </div>
                <button 
                  onClick={onClose}
                  className="p-1 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-colors"
                  aria-label="Close menu"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Command Search Input */}
              <div className="relative">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input 
                  type="text" 
                  placeholder="Execute command or search..."
                  className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/[0.02] border border-white/[0.05] text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
                />
              </div>

              {/* Menu Categories */}
              <nav className="space-y-6">
                {isAuthenticated && (
                  <div className="space-y-2">
                    <span className="text-[9px] font-mono font-semibold tracking-widest text-indigo-400 uppercase">Operator Dashboard</span>
                    <button
                      onClick={() => {
                        onNavigate('dashboard');
                        onClose();
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300 font-medium hover:bg-indigo-500/15 transition-all text-left"
                    >
                      <LayoutDashboard className="w-4 h-4" />
                      <span>Launch OS Dashboard</span>
                    </button>
                  </div>
                )}

                {menuSections.map((section, idx) => (
                  <div key={idx} className="space-y-2">
                    <span className="text-[9px] font-mono font-semibold tracking-widest text-slate-500 uppercase">{section.title}</span>
                    <div className="space-y-1">
                      {section.items.map((item, key) => (
                        <button
                          key={key}
                          onClick={() => {
                            item.action();
                            onClose();
                          }}
                          className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs text-slate-400 hover:text-white hover:bg-white/[0.02] transition-all text-left group"
                        >
                          <item.icon className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 transition-colors" />
                          <span>{item.name}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </nav>
            </div>

            {/* Bottom Panel Actions */}
            <div className="mt-8 pt-4 border-t border-white/[0.05] space-y-3">
              {!isAuthenticated ? (
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => {
                      onAuthClick('login');
                      onClose();
                    }}
                    className="py-2 rounded-xl bg-slate-900 border border-white/[0.06] text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-all"
                  >
                    Log In
                  </button>
                  <button
                    onClick={() => {
                      onAuthClick('signup');
                      onClose();
                    }}
                    className="py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-xs font-semibold text-white hover:opacity-95 transition-all"
                  >
                    Register
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-3 p-2 rounded-xl bg-white/[0.01] border border-white/[0.03]">
                  <div className="w-8 h-8 rounded-lg bg-indigo-950 flex items-center justify-center font-mono text-indigo-400 font-bold text-xs uppercase">
                    OP
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[11px] font-medium text-slate-200 truncate">System Operator</p>
                    <p className="text-[9px] font-mono text-slate-500 uppercase tracking-wider">Authorized Console</p>
                  </div>
                </div>
              )}

              <div className="flex justify-between items-center text-[9px] font-mono text-slate-600 px-1">
                <span>OS VERSION: v1.0.4</span>
                <span className="text-emerald-500 animate-pulse">ONLINE</span>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
