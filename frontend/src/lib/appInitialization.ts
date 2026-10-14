import { authService, goalService, pluginService } from '@/services/api';

export interface InitializationResult {
  isAuthenticated: boolean;
  user: any | null;
  goals: any[] | null;
  plugins: any[] | null;
}

export async function initializeApplication(onProgress?: (progress: number) => void): Promise<InitializationResult> {
  let progress = 0;
  const updateProgress = (amount: number) => {
    progress = Math.min(progress + amount, 100);
    onProgress?.(progress);
  };

  // 1. Fonts & Layout Mounting Check
  updateProgress(15); // Start at 15%
  
  if (typeof window !== 'undefined') {
    try {
      if (document.fonts) {
        // Wait for fonts to resolve or timeout in 1.2s to prevent freezing
        await Promise.race([
          document.fonts.ready,
          new Promise((resolve) => setTimeout(resolve, 1200))
        ]);
      }
    } catch (e) {
      console.warn('Font loading check failed, proceeding:', e);
    }
  }
  updateProgress(15); // Now at 30%

  // 2. Initialize Theme Settings
  if (typeof window !== 'undefined') {
    // Ensure dark class is applied to root element (Tailwind v4 default/pre-render styling)
    document.documentElement.classList.add('dark');
  }
  updateProgress(10); // Now at 40%

  // 3. Session / Authentication and API Prefetching
  const token = typeof window !== 'undefined' ? localStorage.getItem('agentx_token') : null;
  
  if (!token) {
    // No active session token. Fast track loader to 100% and render authorization login gate.
    updateProgress(60);
    return {
      isAuthenticated: false,
      user: null,
      goals: null,
      plugins: null
    };
  }

  try {
    // Authenticate current session token
    const user = await authService.getMe();
    updateProgress(30); // Now at 70%

    // Pre-fetch workspace data in parallel (goals and plugins) to avoid layout shifts or dashboard spinners
    const [goals, plugins] = await Promise.all([
      goalService.listGoals().catch((err) => {
        console.warn('Prefetch goals failed:', err);
        return [];
      }),
      pluginService.listPlugins().catch((err) => {
        console.warn('Prefetch plugins failed:', err);
        return [];
      })
    ]);

    updateProgress(30); // Now at 100%

    return {
      isAuthenticated: true,
      user,
      goals,
      plugins
    };
  } catch (err) {
    console.error('Session authorization validation failed. Resetting token:', err);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('agentx_token');
    }
    updateProgress(60);
    return {
      isAuthenticated: false,
      user: null,
      goals: null,
      plugins: null
    };
  }
}
