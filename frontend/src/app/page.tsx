'use client';

import React, { useState, useEffect } from 'react';
import { useAppStore } from '@/store';
import { Sidebar } from '@/components/dashboard/sidebar';
import { HomeView } from '@/components/dashboard/home-view';
import { AIAssistantView } from '@/components/dashboard/ai-assistant-view';
import { MissionsListView } from '@/components/dashboard/missions-list-view';
import { MissionWorkspaceView } from '@/components/dashboard/mission-workspace-view';
import { WorkflowsView } from '@/components/dashboard/workflows-view';
import { 
  MemoryView, 
  KnowledgeView, 
  AgentsView, 
  ToolsView, 
  MarketplaceView, 
  AnalyticsView, 
  MonitoringView, 
  ModelsView, 
  SettingsView, 
  ProfileView, 
  HelpView, 
  DocumentationView, 
  AdminView 
} from '@/components/dashboard/system-views';
import { 
  StudioDashboardView,
  LiveAgentMonitorView,
  PromptStudioView,
  ModelPlaygroundView,
  ApiExplorerView,
  LatencyMetricsView,
  DeveloperSettingsView
} from '@/components/dashboard/studio-views';
import { 
  AdminDashboardView,
  UserManagementView,
  OrganizationManagementView,
  BillingCostsView,
  SecurityAuditsView,
  SystemHealthView
} from '@/components/dashboard/admin-views';
import { GlassCard } from '@/components/ui/glass-card';
import { NeuralBackground } from '@/components/ui/neural-background';
import { AgentXLoader } from '@/components/ui/agentx-loader';
import { authService } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bell, 
  User, 
  Settings as SettingsIcon, 
  LogOut, 
  Lock, 
  UserPlus, 
  Loader2,
  Sparkles,
  Activity,
  Terminal,
  CheckCircle2
} from 'lucide-react';
import { Toaster, toast } from 'sonner';
import { Homepage } from '@/components/landing/Homepage';

export default function Page() {
  const { 
    activeView, 
    isAuthenticated, 
    setIsAuthenticated, 
    setActiveView, 
    consoleMode,
    setConsoleMode,
    user, 
    setUser,
    isInitializing,
    setIsInitializing
  } = useAppStore();

  const [showAuthForm, setShowAuthForm] = useState<'login' | 'signup' | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  // App initialization timer for AGENTX logo reveal
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsInitializing(false);
    }, 1200);
    return () => clearTimeout(timer);
  }, [setIsInitializing]);

  // Check token and load profile on mount or auth status change
  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('agentx_token') : null;
    if (token) {
      if (isAuthenticated !== true) {
        setIsAuthenticated(true);
      }
      authService.getMe()
        .then(u => {
          const userObj = {
            id: u.id,
            email: u.email,
            role: u.role,
            nickname: u.nickname || null
          };
          setUser(userObj);

          // PROBLEM 4 — LOGIN-BASED UI: Set consoleMode & view dynamically from authenticated user role
          const roleLower = (u.role || '').toLowerCase();
          if (roleLower === 'admin') {
            setConsoleMode('admin');
            setActiveView('admin_dashboard');
          } else if (roleLower === 'developer') {
            setConsoleMode('developer');
            setActiveView('studio_dashboard');
          } else {
            setConsoleMode('user');
            setActiveView('ai_assistant');
          }
        })
        .catch(() => {
          // Token is invalid/expired
          authService.logout();
          setIsAuthenticated(false);
          setUser(null);
          setActiveView('home');
        });
    } else {
      if (isAuthenticated !== false) {
        setIsAuthenticated(false);
      }
    }
  }, [isAuthenticated, setIsAuthenticated, setUser, setActiveView, setConsoleMode]);

  // Synchronize Console Mode state based on active route
  useEffect(() => {
    if (!isAuthenticated) return;
    const isStudioView = [
      'studio_dashboard', 'workflows', 'live_agent_monitor', 'prompt_studio',
      'model_playground', 'api_explorer', 'latency_metrics', 'developer_settings', 'developer'
    ].includes(activeView);

    const isAdminView = [
      'admin_dashboard', 'admin_users', 'admin_orgs', 'admin_billing',
      'admin_audit_logs', 'admin_system_health'
    ].includes(activeView);

    if (isAdminView && consoleMode !== 'admin') {
      setConsoleMode('admin');
    } else if (isStudioView && consoleMode !== 'developer') {
      setConsoleMode('developer');
    } else if (!isAdminView && !isStudioView && consoleMode !== 'user') {
      setConsoleMode('user');
    }
  }, [activeView, isAuthenticated, consoleMode, setConsoleMode]);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    setLoading(true);
    try {
      if (showAuthForm === 'login') {
        await authService.login(email, password);
        const u = await authService.getMe();
        const userObj = {
          id: u.id,
          email: u.email,
          role: u.role,
          nickname: u.email.split('@')[0]
        };
        setUser(userObj);
        setIsAuthenticated(true);
        setShowAuthForm(null);

        // Dynamically route by role
        const roleLower = (u.role || '').toLowerCase();
        if (roleLower === 'admin') {
          setConsoleMode('admin');
          setActiveView('admin_dashboard');
        } else if (roleLower === 'developer') {
          setConsoleMode('developer');
          setActiveView('studio_dashboard');
        } else {
          setConsoleMode('user');
          setActiveView('ai_assistant');
        }
        toast.success(`Welcome back to AgentX AI OS.`);
      } else {
        await authService.signup(email, password);
        toast.success('Account registered! Logging in...');
        await authService.login(email, password);
        const u = await authService.getMe();
        const userObj = {
          id: u.id,
          email: u.email,
          role: u.role,
          nickname: u.email.split('@')[0]
        };
        setUser(userObj);
        setIsAuthenticated(true);
        setShowAuthForm(null);

        const roleLower = (u.role || '').toLowerCase();
        if (roleLower === 'admin') {
          setConsoleMode('admin');
          setActiveView('admin_dashboard');
        } else if (roleLower === 'developer') {
          setConsoleMode('developer');
          setActiveView('studio_dashboard');
        } else {
          setConsoleMode('user');
          setActiveView('ai_assistant');
        }
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Authentication error';
      toast.error('Authentication Failed: ' + msg);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setUser(null);
    setActiveView('home');
    setProfileOpen(false);
    toast.info('Signed out of AgentX AI OS.');
  };

  // Full-screen initialization loader reveal
  if (isInitializing) {
    return <AgentXLoader />;
  }

  // Prevent flash before auth check completes
  if (isAuthenticated === null) {
    return <AgentXLoader />;
  }

  // Main Consumer AI OS Dashboard Workspace (Authenticated)
  if (isAuthenticated) {
    return (
      <div className="flex flex-col min-h-screen bg-zinc-950 text-white relative font-sans selection:bg-indigo-500 selection:text-white">
        <Toaster theme="dark" position="top-right" />
        
        {/* Living Ambient Neural Environment Background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/15 via-zinc-950 to-zinc-950 pointer-events-none z-0" />
        <NeuralBackground />

        {/* Sliding Navigation Drawer */}
        <Sidebar isOpen={menuOpen} onClose={() => setMenuOpen(false)} />

        {/* Top Header Bar */}
        <header className="px-6 py-4 border-b border-white/[0.05] flex justify-between items-center bg-zinc-950/60 backdrop-blur-xl sticky top-0 z-30">
          <div className="flex items-center gap-4">
            {/* Premium Hamburger Menu Button */}
            <button 
              onClick={() => setMenuOpen(true)}
              className="p-2.5 rounded-xl hover:bg-white/[0.06] border border-white/[0.08] bg-white/[0.02] transition-all flex flex-col justify-between h-9 w-9 gap-1 cursor-pointer items-center justify-center group"
              title="Open AgentX Menu"
            >
              <span className="w-4 h-[1.5px] bg-white block transition-transform group-hover:translate-y-[1px]"></span>
              <span className="w-4 h-[1.5px] bg-white block transition-transform"></span>
              <span className="w-4 h-[1.5px] bg-white block transition-transform group-hover:-translate-y-[1px]"></span>
            </button>
            
            <div 
              onClick={() => {
                if (consoleMode === 'user') {
                  setActiveView('ai_assistant');
                } else if (consoleMode === 'developer') {
                  setActiveView('studio_dashboard');
                } else {
                  setActiveView('admin_dashboard');
                }
              }}
              className="flex items-center gap-2.5 cursor-pointer group select-none"
            >
              <div className="w-7 h-7 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
                <span className="text-white font-extrabold text-xs">X</span>
              </div>
              <h1 className="text-sm font-bold text-white tracking-wider">
                Agent<span className="text-indigo-400">X</span>
              </h1>
            </div>

            {/* Header Console Selector Pill (Only visible to Admin or Developer) */}
            {(user?.role?.toLowerCase() === 'admin' || user?.role?.toLowerCase() === 'developer') && (
              <div className="hidden sm:flex items-center gap-1 bg-zinc-900/90 p-1 rounded-xl border border-white/[0.08] ml-2">
                <button
                  onClick={() => {
                    setConsoleMode('user');
                    setActiveView('ai_assistant');
                  }}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                    consoleMode === 'user'
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md shadow-indigo-500/20'
                      : 'text-zinc-400 hover:text-white'
                  }`}
                >
                  <Sparkles className="w-3 h-3" />
                  <span>User Console</span>
                </button>
                <button
                  onClick={() => {
                    setConsoleMode('developer');
                    setActiveView('studio_dashboard');
                  }}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                    consoleMode === 'developer'
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md shadow-indigo-500/20'
                      : 'text-zinc-400 hover:text-white'
                  }`}
                >
                  <Terminal className="w-3 h-3" />
                  <span>Developer Studio</span>
                </button>
                {user?.role?.toLowerCase() === 'admin' && (
                  <button
                    onClick={() => {
                      setConsoleMode('admin');
                      setActiveView('admin_dashboard');
                    }}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                      consoleMode === 'admin'
                        ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md shadow-indigo-500/20'
                        : 'text-zinc-400 hover:text-white'
                    }`}
                  >
                    <Activity className="w-3 h-3" />
                    <span>Admin Control</span>
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Right Header Navigation Icons */}
          <div className="flex items-center gap-3 relative">
            {/* Notification Center Icon */}
            <div className="relative">
              <button 
                onClick={() => {
                  setNotificationsOpen(!notificationsOpen);
                  setProfileOpen(false);
                }}
                className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] transition-colors cursor-pointer relative"
                title="Notifications"
              >
                <Bell className="w-4.5 h-4.5" />
                <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-indigo-500 ring-2 ring-zinc-950 animate-pulse" />
              </button>

              {/* Notification Popover Dropdown */}
              <AnimatePresence>
                {notificationsOpen && (
                  <motion.div 
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 8 }}
                    className="absolute right-0 mt-2 w-80 p-4 rounded-2xl bg-zinc-900 border border-white/[0.1] shadow-2xl z-50 space-y-3"
                  >
                    <div className="flex items-center justify-between border-b border-white/[0.06] pb-2">
                      <h4 className="text-xs font-bold text-white">Notification Center</h4>
                      <span className="text-[10px] text-zinc-500 font-mono">1 NEW</span>
                    </div>
                    <div className="space-y-2">
                      <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.04] flex items-start gap-2.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        <div>
                          <p className="text-xs font-semibold text-white">System Kernel Initialized</p>
                          <p className="text-[10px] text-zinc-400">AgentX AI OS is fully operational and synced.</p>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Settings Icon */}
            <button 
              onClick={() => setActiveView('settings')}
              className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] transition-colors cursor-pointer"
              title="Settings"
            >
              <SettingsIcon className="w-4.5 h-4.5" />
            </button>

            {/* Profile Dropdown */}
            <div className="relative">
              <button 
                onClick={() => {
                  setProfileOpen(!profileOpen);
                  setNotificationsOpen(false);
                }}
                className="p-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 hover:bg-indigo-500/20 transition-all cursor-pointer flex items-center gap-2"
                title="Profile"
              >
                <User className="w-4 h-4" />
              </button>

              <AnimatePresence>
                {profileOpen && (
                  <motion.div 
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 8 }}
                    className="absolute right-0 mt-2 w-56 p-3 rounded-2xl bg-zinc-900 border border-white/[0.1] shadow-2xl z-50 space-y-2"
                  >
                    <div className="px-3 py-2 border-b border-white/[0.06]">
                      <p className="text-xs font-bold text-white">{user?.nickname || 'Operator'}</p>
                      <p className="text-[10px] text-zinc-400 truncate font-mono">{user?.email}</p>
                    </div>

                    <button
                      onClick={() => {
                        setActiveView('profile');
                        setProfileOpen(false);
                      }}
                      className="w-full px-3 py-2 rounded-xl text-xs text-zinc-300 hover:text-white hover:bg-white/[0.05] transition-colors flex items-center gap-2 cursor-pointer"
                    >
                      <User className="w-3.5 h-3.5" /> View Profile
                    </button>

                    <button
                      onClick={() => {
                        if (consoleMode === 'user') {
                          const nextMode = user?.role?.toLowerCase() === 'admin' ? 'admin' : 'developer';
                          setConsoleMode(nextMode);
                          setActiveView(nextMode === 'admin' ? 'admin_dashboard' : 'studio_dashboard');
                        } else {
                          setConsoleMode('user');
                          setActiveView('ai_assistant');
                        }
                        setProfileOpen(false);
                      }}
                      className="w-full px-3 py-2 rounded-xl text-xs text-zinc-300 hover:text-white hover:bg-white/[0.05] transition-colors flex items-center gap-2 cursor-pointer"
                    >
                      <Terminal className="w-3.5 h-3.5 text-indigo-400" />
                      {consoleMode === 'user' ? 'Switch to Developer Studio' : 'Switch to User Console'}
                    </button>

                    <div className="border-t border-white/[0.06] pt-1" />

                    <button
                      onClick={handleLogout}
                      className="w-full px-3 py-2 rounded-xl text-xs text-rose-400 hover:bg-rose-500/10 transition-colors flex items-center gap-2 cursor-pointer"
                    >
                      <LogOut className="w-3.5 h-3.5" /> Sign Out
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </header>

        {/* Dynamic Main OS Content Router */}
        <main className="p-6 md:p-8 max-w-7xl mx-auto w-full flex-1 z-10">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeView}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
            >
              {activeView === 'home' && <HomeView />}
              {activeView === 'ai_assistant' && <AIAssistantView />}
              {activeView === 'mission_creator' && <HomeView />}
              {activeView === 'missions' && <MissionsListView />}
              {activeView === 'mission_workspace' && <MissionWorkspaceView />}

              {/* Workspace Apps */}
              {activeView === 'files' && <KnowledgeView />}
              {activeView === 'knowledge' && <KnowledgeView />}
              {activeView === 'templates' && <MarketplaceView />}
              {activeView === 'marketplace' && <MarketplaceView />}
              {activeView === 'settings' && <SettingsView />}
              {activeView === 'profile' && <ProfileView />}

              {/* Studio Views */}
              {activeView === 'studio_dashboard' && <StudioDashboardView />}
              {activeView === 'workflows' && <WorkflowsView />}
              {activeView === 'live_agent_monitor' && <LiveAgentMonitorView />}
              {activeView === 'prompt_studio' && <PromptStudioView />}
              {activeView === 'model_playground' && <ModelPlaygroundView />}
              {activeView === 'api_explorer' && <ApiExplorerView />}
              {activeView === 'latency_metrics' && <LatencyMetricsView />}
              {activeView === 'developer_settings' && <DeveloperSettingsView />}

              {/* Control Center Views */}
              {activeView === 'admin_dashboard' && <AdminDashboardView />}
              {activeView === 'admin_users' && <UserManagementView />}
              {activeView === 'admin_orgs' && <OrganizationManagementView />}
              {activeView === 'admin_billing' && <BillingCostsView />}
              {activeView === 'admin_audit_logs' && <SecurityAuditsView />}
              {activeView === 'admin_system_health' && <SystemHealthView />}

              {/* Legacy/General Developer Mode Technical Views */}
              {activeView === 'developer' && <WorkflowsView />}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    );
  }

  // Auth Gate Panel (Login / Signup)
  if (showAuthForm) {
    return (
      <div className="flex-1 flex items-center justify-center bg-zinc-950 min-h-screen relative overflow-hidden p-6 font-sans">
        <Toaster theme="dark" position="top-right" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-900/20 via-zinc-950 to-zinc-950 pointer-events-none z-0" />
        <NeuralBackground />

        <button
          onClick={() => setShowAuthForm(null)}
          className="absolute top-6 left-6 text-xs text-zinc-400 hover:text-white transition-colors cursor-pointer flex items-center gap-1.5 z-10"
        >
          &larr; Return to Welcome Screen
        </button>

        <GlassCard className="w-full max-w-md p-8 relative z-10 border-white/[0.08]" hoverGlow={true}>
          <div className="flex flex-col items-center text-center space-y-3 mb-6">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <span className="text-white font-extrabold text-base">X</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white tracking-wide">
                Agent<span className="text-indigo-400">X</span>
              </h2>
              <p className="text-xs text-zinc-400 mt-1">
                {showAuthForm === 'login' ? 'Sign in to access your AI Operating System' : 'Create an AgentX Operator Account'}
              </p>
            </div>
          </div>

          <form onSubmit={handleAuth} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs text-zinc-400">Email Address</label>
              <input
                type="email"
                placeholder="operator@agentx.ai"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-white/[0.08] bg-zinc-900/60 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-zinc-400">Password</label>
              <input
                type="password"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-white/[0.08] bg-zinc-900/60 text-sm text-white focus:outline-none focus:border-indigo-500/50 transition-colors"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold text-xs tracking-wider transition-all duration-300 shadow-md shadow-indigo-500/15 flex items-center justify-center gap-2 cursor-pointer"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : showAuthForm === 'login' ? (
                <>
                  <Lock className="w-3.5 h-3.5" /> SIGN IN
                </>
              ) : (
                <>
                  <UserPlus className="w-3.5 h-3.5" /> CREATE ACCOUNT
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => setShowAuthForm(showAuthForm === 'login' ? 'signup' : 'login')}
              className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer"
            >
              {showAuthForm === 'login' ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
            </button>
          </div>
        </GlassCard>
      </div>
    );
  }

  // Public Landing Homepage
  return (
    <Homepage 
      onAuthClick={(mode) => setShowAuthForm(mode)}
      isAuthenticated={isAuthenticated}
      onDashboardClick={() => {
        setActiveView('home');
      }}
    />
  );
}
