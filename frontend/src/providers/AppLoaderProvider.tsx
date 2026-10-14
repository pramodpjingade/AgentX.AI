'use client';

import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { useAppInitialization } from '../hooks/useAppInitialization';
import { SplashScreen } from '../components/SplashScreen';

export const AppLoaderProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isInitializing, progress } = useAppInitialization();

  React.useEffect(() => {
    if (!isInitializing) {
      window.scrollTo(0, 0);
    }
  }, [isInitializing]);

  return (
    <>
      <AnimatePresence mode="wait">
        {isInitializing && (
          <SplashScreen key="splash-screen" />
        )}
      </AnimatePresence>
      
      {/* 
        Render children only when initialization is complete.
        This guarantees that components reading the Zustand store (like auth roles or goals lists)
        mount with pre-populated data, avoiding spinners and layout shifts.
      */}
      {!isInitializing && children}
    </>
  );
};
