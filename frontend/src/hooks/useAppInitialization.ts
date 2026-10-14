import { useState, useEffect } from 'react';
import { initializeApplication, InitializationResult } from '../lib/appInitialization';
import { useAppStore } from '../store';

export function useAppInitialization() {
  const [isInitializing, setIsInitializing] = useState(true);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<InitializationResult | null>(null);

  useEffect(() => {
    let active = true;

    async function runInit() {
      // Delay slightly on start to allow first frame / CSS to render cleanly
      await new Promise((resolve) => setTimeout(resolve, 300));
      
      try {
        const initResult = await initializeApplication((p) => {
          if (active) setProgress(p);
        });

        // Ensure smooth transition: hold visual completion for 2.3s to showcase the logo float and shimmer
        if (active) {
          setProgress(100);
          await new Promise((resolve) => setTimeout(resolve, 2300));
          setResult(initResult);

          // Synchronize with global Zustand store
          const store = useAppStore.getState();
          store.setIsAuthenticated(initResult.isAuthenticated);
          if (initResult.isAuthenticated && initResult.user) {
            store.setUser({
              id: (initResult.user as any).id || '1',
              email: initResult.user.email,
              role: initResult.user.role,
              nickname: initResult.user.email.split('@')[0]
            });
          } else {
            store.setUser(null);
          }

          setIsInitializing(false);
        }
      } catch (err) {
        console.error('Initialization error occurred:', err);
        if (active) {
          const fallbackResult = {
            isAuthenticated: false,
            user: null,
            goals: null,
            plugins: null
          };
          setResult(fallbackResult);
          
          const store = useAppStore.getState();
          store.setIsAuthenticated(false);
          store.setUser(null);
          
          setIsInitializing(false);
        }
      }
    }

    runInit();

    return () => {
      active = false;
    };
  }, []);

  return {
    isInitializing,
    progress,
    result
  };
}
