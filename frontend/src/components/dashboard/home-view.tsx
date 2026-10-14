'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAppStore } from '@/store';
import { goalService, GoalResponse } from '@/services/api';
import { GlassCard } from '@/components/ui/glass-card';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Mic, 
  Paperclip, 
  Globe, 
  ArrowRight, 
  Compass, 
  Code, 
  BookOpen, 
  Trophy, 
  Loader2, 
  Play, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  FileText
} from 'lucide-react';
import { toast } from 'sonner';

export const HomeView: React.FC = () => {
  const { user, setActiveView, setSelectedGoalId } = useAppStore();
  const [prompt, setPrompt] = useState('');
  const [isWebSearch, setIsWebSearch] = useState(true);
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [recentGoals, setRecentGoals] = useState<GoalResponse[]>([]);
  const [loadingGoals, setLoadingGoals] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Time-adaptive greeting message
  const [greeting, setGreeting] = useState('');
  const [motivationMessage, setMotivationMessage] = useState('');

  useEffect(() => {
    const hour = new Date().getHours();
    let timeOfDay = 'day';
    if (hour >= 5 && hour < 12) {
      timeOfDay = 'morning';
      setGreeting('Good morning');
    } else if (hour >= 12 && hour < 18) {
      timeOfDay = 'afternoon';
      setGreeting('Good afternoon');
    } else {
      timeOfDay = 'evening';
      setGreeting('Good evening');
    }

    const messages = {
      morning: [
        "What ambitious mission shall we accomplish together today?",
        "Empower your morning workflow with autonomous AI intelligence.",
        "Your AI Operating System is primed for execution."
      ],
      afternoon: [
        "Ready to accelerate your afternoon projects?",
        "Transform your complex goals into completed deliverables.",
        "Delegate your heavy technical workflows to AgentX."
      ],
      evening: [
        "Let's wrap up your key missions before the day ends.",
        "Consolidate your daily research and code deliverables.",
        "Review active workflows and plan your next objectives."
      ]
    };

    const array = messages[timeOfDay as keyof typeof messages];
    const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 1000 / 60 / 60 / 24);
    setMotivationMessage(array[dayOfYear % array.length]);

    fetchRecentGoals();
  }, []);

  const fetchRecentGoals = async () => {
    try {
      setLoadingGoals(true);
      const goals = await goalService.listGoals();
      setRecentGoals(goals);
    } catch (err: any) {
      console.error('Failed to load recent goals:', err);
    } finally {
      setLoadingGoals(false);
    }
  };

  const handleLaunchMission = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!prompt.trim()) {
      toast.error('Please enter a goal or mission prompt.');
      return;
    }

    setSubmitting(true);
    try {
      const title = prompt.length > 50 ? prompt.substring(0, 47) + '...' : prompt;
      const description = attachedFiles.length > 0 
        ? `${prompt}\n\nAttached Files: ${attachedFiles.map(f => f.name).join(', ')}`
        : prompt;

      const createdGoal = await goalService.createGoal(title, description);
      toast.success('Mission launched successfully! Initializing AI agents...');
      
      setSelectedGoalId(createdGoal.id);
      setActiveView('mission_workspace');
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to dispatch mission';
      toast.error('Mission Dispatch Failed: ' + msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleQuickAction = (quickPrompt: string) => {
    setPrompt(quickPrompt);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArray = Array.from(e.target.files);
      setAttachedFiles(prev => [...prev, ...filesArray]);
      toast.info(`Attached ${filesArray.length} file(s)`);
    }
  };

  const handleToggleVoice = () => {
    setIsVoiceActive(!isVoiceActive);
    if (!isVoiceActive) {
      toast.info('Voice input simulation listening...');
      setTimeout(() => {
        setPrompt('Plan a 5-day luxury trip to Kerala with houseboats and beach resorts.');
        setIsVoiceActive(false);
        toast.success('Voice input transcribed!');
      }, 2500);
    }
  };

  const nickname = user?.nickname || (user?.email ? user.email.split('@')[0] : 'Operator');

  return (
    <div className="space-y-12 max-w-5xl mx-auto py-4">
      {/* Hero Header Section */}
      <div className="space-y-3 text-center md:text-left">
        <motion.h1 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl md:text-4xl font-extrabold text-white tracking-tight"
        >
          Welcome back, <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-300 to-white">{nickname}</span> 👋
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-sm md:text-base text-zinc-400 font-normal"
        >
          {motivationMessage}
        </motion.p>
      </div>

      {/* Main AI Mission Creator Input Card */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
      >
        <GlassCard className="p-6 md:p-8 relative border-white/[0.08] bg-zinc-900/40 backdrop-blur-xl shadow-2xl rounded-2xl" hoverGlow={true}>
          <form onSubmit={handleLaunchMission} className="space-y-4">
            <div className="relative">
              <div className="absolute top-3 left-4 text-indigo-400 flex items-center gap-2">
                <Sparkles className="w-5 h-5 animate-pulse" />
              </div>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="What would you like to accomplish today?"
                rows={4}
                className="w-full pl-12 pr-4 pt-3 pb-3 bg-zinc-950/60 border border-white/[0.06] rounded-xl text-base text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500/50 transition-all resize-none"
              />
            </div>

            {/* Attached Files Pill List */}
            {attachedFiles.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-1">
                {attachedFiles.map((file, idx) => (
                  <span key={idx} className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300 font-mono">
                    <FileText className="w-3.5 h-3.5" />
                    {file.name}
                    <button type="button" onClick={() => setAttachedFiles(prev => prev.filter((_, i) => i !== idx))} className="ml-1 text-zinc-400 hover:text-white">&times;</button>
                  </span>
                ))}
              </div>
            )}

            {/* Input Actions Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
              <div className="flex items-center gap-2">
                {/* Voice Input Button */}
                <button
                  type="button"
                  onClick={handleToggleVoice}
                  className={`p-2.5 rounded-xl border transition-all flex items-center gap-1.5 text-xs font-medium cursor-pointer ${
                    isVoiceActive 
                      ? 'bg-rose-500/20 border-rose-500/40 text-rose-300 animate-pulse' 
                      : 'bg-white/[0.03] border-white/[0.06] text-zinc-400 hover:text-white hover:bg-white/[0.06]'
                  }`}
                  title="Voice Input"
                >
                  <Mic className="w-4 h-4" />
                  <span className="hidden sm:inline">{isVoiceActive ? 'Listening...' : 'Voice'}</span>
                </button>

                {/* File Upload Button */}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06] text-zinc-400 hover:text-white hover:bg-white/[0.06] transition-all flex items-center gap-1.5 text-xs font-medium cursor-pointer"
                  title="Attach File"
                >
                  <Paperclip className="w-4 h-4" />
                  <span className="hidden sm:inline">Attach</span>
                </button>
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileUpload} 
                  multiple 
                  className="hidden" 
                />

                {/* Web Search Toggle */}
                <button
                  type="button"
                  onClick={() => setIsWebSearch(!isWebSearch)}
                  className={`p-2.5 rounded-xl border transition-all flex items-center gap-1.5 text-xs font-medium cursor-pointer ${
                    isWebSearch 
                      ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300' 
                      : 'bg-white/[0.03] border-white/[0.06] text-zinc-400 hover:text-white hover:bg-white/[0.06]'
                  }`}
                  title="Deep Web Search"
                >
                  <Globe className="w-4 h-4" />
                  <span className="hidden sm:inline">Web Search</span>
                </button>
              </div>

              {/* Launch Mission Button */}
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-xs font-bold tracking-wide transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2 cursor-pointer disabled:opacity-50"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>LAUNCHING...</span>
                  </>
                ) : (
                  <>
                    <span>LAUNCH MISSION</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </form>
        </GlassCard>
      </motion.div>

      {/* Quick Action Cards */}
      <div className="space-y-4">
        <h2 className="text-xs font-mono text-zinc-400 uppercase tracking-widest">QUICK START TEMPLATES</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <GlassCard 
            onClick={() => handleQuickAction("Plan a 5-day luxury holiday trip to Kerala with houseboats, backwaters, and beach resorts.")}
            className="p-5 cursor-pointer border-white/[0.06] hover:border-indigo-500/30 transition-all group"
          >
            <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-3 group-hover:scale-110 transition-transform">
              <Compass className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">Travel Planner</h3>
            <p className="text-xs text-zinc-400 mt-1 line-clamp-2">Plan itineraries, hotels, and travel advisories for any destination.</p>
          </GlassCard>

          <GlassCard 
            onClick={() => handleQuickAction("Build a Python script to parse CSV and JSON sales data files with error handling and summaries.")}
            className="p-5 cursor-pointer border-white/[0.06] hover:border-indigo-500/30 transition-all group"
          >
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-3 group-hover:scale-110 transition-transform">
              <Code className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">Code & Engineering</h3>
            <p className="text-xs text-zinc-400 mt-1 line-clamp-2">Generate REST APIs, data pipelines, scripts, and software architecture.</p>
          </GlassCard>

          <GlassCard 
            onClick={() => handleQuickAction("Synthesize a comprehensive research report on Quantum Computing algorithms and cryptography.")}
            className="p-5 cursor-pointer border-white/[0.06] hover:border-indigo-500/30 transition-all group"
          >
            <div className="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-3 group-hover:scale-110 transition-transform">
              <BookOpen className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white group-hover:text-purple-300 transition-colors">Deep Learning</h3>
            <p className="text-xs text-zinc-400 mt-1 line-clamp-2">Research technical concepts, summarize literature, and extract facts.</p>
          </GlassCard>

          <GlassCard 
            onClick={() => handleQuickAction("Design a 6-week progressive athletic strength and vertical jump training program.")}
            className="p-5 cursor-pointer border-white/[0.06] hover:border-indigo-500/30 transition-all group"
          >
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-3 group-hover:scale-110 transition-transform">
              <Trophy className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors">Sports & Fitness</h3>
            <p className="text-xs text-zinc-400 mt-1 line-clamp-2">Formulate customized workout plans, athletic drills, and biomechanics.</p>
          </GlassCard>
        </div>
      </div>

      {/* Continue Your Missions Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-mono text-zinc-400 uppercase tracking-widest">CONTINUE YOUR MISSIONS</h2>
          <button 
            onClick={() => setActiveView('missions')}
            className="text-xs font-mono text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer"
          >
            VIEW ALL &rarr;
          </button>
        </div>

        {loadingGoals ? (
          <div className="p-8 text-center border border-white/[0.05] rounded-2xl bg-zinc-900/20">
            <Loader2 className="w-6 h-6 text-indigo-400 animate-spin mx-auto mb-2" />
            <p className="text-xs text-zinc-400 font-mono">Loading mission history...</p>
          </div>
        ) : recentGoals.length === 0 ? (
          <GlassCard className="p-8 text-center border-white/[0.05]">
            <p className="text-sm text-zinc-400">No active missions yet. Launch your first mission above!</p>
          </GlassCard>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recentGoals.slice(0, 4).map((g) => {
              const isDone = g.status === 'completed';
              const isExecuting = g.status === 'executing' || g.status === 'running';

              return (
                <GlassCard key={g.id} className="p-6 border-white/[0.06] flex flex-col justify-between space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono tracking-wider uppercase border ${
                        isDone 
                          ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
                          : isExecuting 
                          ? 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400 animate-pulse' 
                          : 'bg-zinc-800/50 border-zinc-700/50 text-zinc-400'
                      }`}>
                        {isDone ? <CheckCircle2 className="w-3 h-3" /> : isExecuting ? <Play className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                        {g.status}
                      </span>
                      <span className="text-[10px] font-mono text-zinc-400">
                        {new Date(g.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-white line-clamp-1">{g.title}</h3>
                    <p className="text-xs text-zinc-400 line-clamp-2">{g.description}</p>
                  </div>

                  <button
                    onClick={() => {
                      setSelectedGoalId(g.id);
                      setActiveView('mission_workspace');
                    }}
                    className="w-full py-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs font-semibold text-white transition-all flex items-center justify-center gap-2 cursor-pointer"
                  >
                    <span>{isDone ? 'VIEW DELIVERABLES' : 'CONTINUE MISSION'}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </GlassCard>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
