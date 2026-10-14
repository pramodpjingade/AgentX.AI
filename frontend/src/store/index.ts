import { create } from 'zustand';

export type DashboardView = 
  | 'home'
  | 'ai_assistant'
  | 'mission_creator'
  | 'missions'
  | 'mission_workspace'
  | 'files' 
  | 'knowledge' 
  | 'templates' 
  | 'marketplace' 
  | 'settings' 
  | 'profile' 
  | 'developer'
  // Developer Studio Views
  | 'studio_dashboard'
  | 'workflows'
  | 'live_agent_monitor'
  | 'prompt_studio'
  | 'model_playground'
  | 'api_explorer'
  | 'latency_metrics'
  | 'developer_settings'
  // Admin Control Center Views
  | 'admin_dashboard'
  | 'admin_users'
  | 'admin_orgs'
  | 'admin_billing'
  | 'admin_audit_logs'
  | 'admin_system_health';

export interface UserProfile {
  id: string;
  email: string;
  role: string;
  nickname?: string | null;
  avatar_url?: string | null;
}

export type ConsoleMode = 'user' | 'developer' | 'admin';

interface AppState {
  activeView: DashboardView;
  setActiveView: (view: DashboardView) => void;
  consoleMode: ConsoleMode;
  setConsoleMode: (mode: ConsoleMode) => void;
  selectedGoalId: string | null;
  setSelectedGoalId: (id: string | null) => void;
  user: UserProfile | null;
  setUser: (user: UserProfile | null) => void;
  isAuthenticated: boolean | null;
  setIsAuthenticated: (auth: boolean | null) => void;
  notificationsOpen: boolean;
  setNotificationsOpen: (open: boolean) => void;
  profileMenuOpen: boolean;
  setProfileMenuOpen: (open: boolean) => void;
  isInitializing: boolean;
  setIsInitializing: (initializing: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeView: 'home',
  setActiveView: (view) => set({ activeView: view }),
  consoleMode: 'user',
  setConsoleMode: (mode) => set({ consoleMode: mode }),
  selectedGoalId: null,
  setSelectedGoalId: (id) => set({ selectedGoalId: id }),
  user: null,
  setUser: (user) => set({ user }),
  isAuthenticated: null,
  setIsAuthenticated: (auth) => set({ isAuthenticated: auth }),
  notificationsOpen: false,
  setNotificationsOpen: (open) => set({ notificationsOpen: open }),
  profileMenuOpen: false,
  setProfileMenuOpen: (open) => set({ profileMenuOpen: open }),
  isInitializing: true,
  setIsInitializing: (isInitializing) => set({ isInitializing }),
}));
