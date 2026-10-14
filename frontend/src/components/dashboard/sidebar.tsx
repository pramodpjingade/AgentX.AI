'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAppStore, DashboardView } from '@/store';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Home,
  PlusCircle,
  FolderKanban,
  Files,
  BookOpen,
  LayoutGrid,
  ShoppingBag,
  Settings,
  User,
  Terminal,
  X,
  Search,
  Users,
  Building,
  CreditCard,
  ShieldCheck,
  Activity,
  Cpu,
  Code,
  Brain,
  Sparkles
} from 'lucide-react';
import { clsx } from 'clsx';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavItem {
  id: DashboardView;
  label: string;
  icon: React.ComponentType<any>;
}

interface NavSection {
  title?: string;
  items: NavItem[];
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { activeView, setActiveView, consoleMode, setConsoleMode, user } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');
  const drawerRef = useRef<HTMLDivElement>(null);

  // Get sections based on active console mode
  const getSections = (): NavSection[] => {
    if (consoleMode === 'admin') {
      return [
        {
          title: "CONTROL CENTER",
          items: [
            { id: 'admin_dashboard', label: 'Dashboard', icon: Home },
            { id: 'admin_users', label: 'Users', icon: Users },
            { id: 'admin_orgs', label: 'Organizations', icon: Building },
          ]
        },
        {
          title: "OPERATIONS",
          items: [
            { id: 'admin_billing', label: 'Billing & Costs', icon: CreditCard },
            { id: 'admin_audit_logs', label: 'Security & Audits', icon: ShieldCheck },
            { id: 'admin_system_health', label: 'System Health', icon: Activity },
          ]
        },
        {
          title: "PREFERENCES",
          items: [
            { id: 'settings', label: 'Platform Settings', icon: Settings },
            { id: 'profile', label: 'Profile', icon: User },
          ]
        }
      ];
    } else if (consoleMode === 'developer') {
      return [
        {
          title: "AGENTX STUDIO",
          items: [
            { id: 'studio_dashboard', label: 'Dashboard', icon: Home },
            { id: 'workflows', label: 'Workflow Visualizer', icon: Terminal },
            { id: 'live_agent_monitor', label: 'Live Agent Monitor', icon: Activity },
          ]
        },
        {
          title: "DEVELOPER TOOLS",
          items: [
            { id: 'prompt_studio', label: 'Prompt Studio', icon: Brain },
            { id: 'model_playground', label: 'Model Playground', icon: Cpu },
            { id: 'api_explorer', label: 'API Explorer', icon: Code },
            { id: 'latency_metrics', label: 'Latency & Metrics', icon: Activity },
          ]
        },
        {
          title: "PREFERENCES",
          items: [
            { id: 'developer_settings', label: 'Developer Settings', icon: Settings },
            { id: 'profile', label: 'Profile', icon: User },
          ]
        }
      ];
    } else {
      // Default: User Console
      return [
        {
          title: "AGENTX AI",
          items: [
            { id: 'ai_assistant', label: 'AI Assistant', icon: Sparkles },
            { id: 'missions', label: 'History', icon: FolderKanban },
          ]
        },
        {
          title: "PREFERENCES",
          items: [
            { id: 'profile', label: 'Profile', icon: User },
            { id: 'settings', label: 'Settings', icon: Settings },
          ]
        }
      ];
    }
  };

  const sections = getSections();

  // Close drawer on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Click outside to close drawer
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (drawerRef.current && !drawerRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    if (isOpen) window.addEventListener('mousedown', handleClickOutside);
    return () => window.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  // Filter items based on search query
  const filteredSections = sections.map(sec => ({
    ...sec,
    items: sec.items.filter(item => 
      item.label.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(sec => sec.items.length > 0);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Glass Overlay Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-md z-45"
          />

          {/* Sliding Navigation Drawer */}
          <motion.div
            ref={drawerRef}
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 260 }}
            className="fixed top-0 left-0 h-screen w-80 bg-zinc-950/95 border-r border-white/[0.08] flex flex-col justify-between z-50 backdrop-blur-2xl shadow-2xl"
          >
            <div>
              {/* Header */}
              <div className="p-6 flex items-center justify-between border-b border-white/[0.05]">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
                    <span className="text-white font-extrabold text-sm tracking-wider">X</span>
                  </div>
                  <div>
                    <h1 className="text-base font-bold text-white tracking-wider">
                      Agent<span className="text-indigo-400">X</span>
                    </h1>
                    <p className="text-[10px] text-zinc-400 font-mono tracking-widest uppercase">AI OPERATING SYSTEM</p>
                  </div>
                </div>
                <button 
                  onClick={onClose}
                  className="p-2 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.08] text-zinc-400 hover:text-white transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Console Mode Selector Card (Only shown for Admin or Developer) */}
              {(user?.role?.toLowerCase() === 'admin' || user?.role?.toLowerCase() === 'developer') && (
                <div className="px-5 py-3 border-b border-white/[0.05]">
                  <p className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider mb-2">CONSOLE MODE</p>
                  <div className="grid grid-cols-3 gap-1 bg-zinc-900/80 p-1 rounded-xl border border-white/[0.08]">
                    <button
                      onClick={() => {
                        setConsoleMode('user');
                        setActiveView('ai_assistant');
                      }}
                      className={clsx(
                        "py-1.5 px-2 rounded-lg text-[10px] font-semibold transition-all cursor-pointer text-center",
                        consoleMode === 'user'
                          ? "bg-indigo-500 text-white shadow-md shadow-indigo-500/20"
                          : "text-zinc-400 hover:text-white"
                      )}
                    >
                      User
                    </button>
                    <button
                      onClick={() => {
                        setConsoleMode('developer');
                        setActiveView('studio_dashboard');
                      }}
                      className={clsx(
                        "py-1.5 px-2 rounded-lg text-[10px] font-semibold transition-all cursor-pointer text-center",
                        consoleMode === 'developer'
                          ? "bg-indigo-500 text-white shadow-md shadow-indigo-500/20"
                          : "text-zinc-400 hover:text-white"
                      )}
                    >
                      Studio
                    </button>
                    {user?.role?.toLowerCase() === 'admin' && (
                      <button
                        onClick={() => {
                          setConsoleMode('admin');
                          setActiveView('admin_dashboard');
                        }}
                        className={clsx(
                          "py-1.5 px-2 rounded-lg text-[10px] font-semibold transition-all cursor-pointer text-center",
                          consoleMode === 'admin'
                            ? "bg-indigo-500 text-white shadow-md shadow-indigo-500/20"
                            : "text-zinc-400 hover:text-white"
                        )}
                      >
                        Admin
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* In-drawer Navigation Search */}
              <div className="px-5 py-3 border-b border-white/[0.05]">
                <div className="relative flex items-center bg-zinc-900/60 border border-white/[0.08] rounded-xl px-3 py-2">
                  <Search className="w-3.5 h-3.5 text-zinc-400 mr-2" />
                  <input
                    type="text"
                    placeholder="Search navigation..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="bg-transparent border-none text-xs text-white focus:outline-none placeholder-zinc-500 w-full"
                  />
                  {searchQuery && (
                    <button onClick={() => setSearchQuery('')} className="text-zinc-500 hover:text-white">
                      <X className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>

              {/* Navigation Items */}
              <nav className="p-4 space-y-6 overflow-y-auto max-h-[calc(100vh-220px)]">
                {filteredSections.map((sec, idx) => (
                  <div key={idx} className="space-y-1">
                    {sec.title && (
                      <h3 className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest px-3.5 mb-2">{sec.title}</h3>
                    )}
                    <div className="space-y-1">
                      {sec.items.map((item) => {
                        const isActive = activeView === item.id;
                        const Icon = item.icon;

                        return (
                          <button
                            key={item.id}
                            onClick={() => {
                              setActiveView(item.id);
                              onClose();
                            }}
                            className={clsx(
                              "w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all duration-200 relative group cursor-pointer",
                              isActive ? "text-white bg-white/[0.08] border border-white/[0.1]" : "text-zinc-400 hover:text-white hover:bg-white/[0.03]"
                            )}
                          >
                            <Icon className={clsx(
                              "w-4 h-4 transition-transform group-hover:scale-110",
                              isActive ? "text-indigo-400" : "text-zinc-400"
                            )} />
                            <span>{item.label}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </nav>
            </div>

            {/* User Profile Mini Footer */}
            <div className="p-4 border-t border-white/[0.05] bg-zinc-900/20">
              <div className="flex items-center gap-3 p-2.5 rounded-xl border border-white/[0.04] bg-white/[0.01]">
                <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-medium text-xs">
                  {user?.email ? user.email.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="overflow-hidden">
                  <h3 className="text-xs font-semibold text-white truncate">{user?.nickname || user?.email || 'User'}</h3>
                  <p className="text-[10px] text-zinc-400 truncate font-mono">{user?.role || 'Standard User'}</p>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
