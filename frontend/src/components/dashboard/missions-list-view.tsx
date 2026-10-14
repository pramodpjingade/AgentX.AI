'use client';

import React, { useState, useEffect } from 'react';
import { useAppStore } from '@/store';
import { goalService, GoalResponse } from '@/services/api';
import { GlassCard } from '@/components/ui/glass-card';
import { motion } from 'framer-motion';
import { 
  FolderKanban, 
  Search, 
  Plus, 
  CheckCircle2, 
  Play, 
  Clock, 
  ArrowRight, 
  Loader2 
} from 'lucide-react';

export const MissionsListView: React.FC = () => {
  const { setActiveView, setSelectedGoalId } = useAppStore();
  const [goals, setGoals] = useState<GoalResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      setLoading(true);
      const data = await goalService.listGoals();
      setGoals(data);
    } catch (err) {
      console.error('Failed to list goals:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredGoals = goals.filter(g => {
    const matchesSearch = g.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          g.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || g.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-8 max-w-6xl mx-auto py-2">
      {/* Title & New Mission CTA Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <FolderKanban className="w-6 h-6 text-indigo-400" />
            My Missions
          </h1>
          <p className="text-xs text-zinc-400 mt-1">Manage and review your active, paused, and completed AI missions.</p>
        </div>

        <button
          onClick={() => setActiveView('home')}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-xs font-bold tracking-wide transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2 cursor-pointer self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>NEW MISSION</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-zinc-500 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search missions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-zinc-900/60 border border-white/[0.08] rounded-xl text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500/50"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto">
          {['all', 'executing', 'completed', 'paused'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono uppercase tracking-wider transition-all cursor-pointer ${
                statusFilter === status 
                  ? 'bg-indigo-500/20 border border-indigo-500/40 text-indigo-300' 
                  : 'bg-white/[0.03] border border-white/[0.06] text-zinc-400 hover:text-white'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Mission Cards Grid */}
      {loading ? (
        <div className="p-16 text-center">
          <Loader2 className="w-8 h-8 text-indigo-400 animate-spin mx-auto mb-2" />
          <p className="text-xs font-mono text-zinc-400">Loading missions catalog...</p>
        </div>
      ) : filteredGoals.length === 0 ? (
        <GlassCard className="p-12 text-center border-white/[0.06] space-y-3">
          <FolderKanban className="w-10 h-10 text-zinc-600 mx-auto" />
          <h3 className="text-sm font-bold text-white">No Missions Found</h3>
          <p className="text-xs text-zinc-400">Launch a new mission from the Home screen to get started.</p>
        </GlassCard>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredGoals.map((g) => {
            const isDone = g.status === 'completed';
            const isExecuting = g.status === 'executing' || g.status === 'running';

            return (
              <GlassCard key={g.id} className="p-6 border-white/[0.06] flex flex-col justify-between space-y-4">
                <div className="space-y-2.5">
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
                    <span className="text-[10px] font-mono text-zinc-500">
                      {new Date(g.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white">{g.title}</h3>
                  <p className="text-xs text-zinc-400 line-clamp-2">{g.description}</p>
                </div>

                <button
                  onClick={() => {
                    setSelectedGoalId(g.id);
                    setActiveView('mission_workspace');
                  }}
                  className="w-full py-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs font-semibold text-white transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  <span>{isDone ? 'OPEN DELIVERABLES' : 'OPEN WORKSPACE'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </GlassCard>
            );
          })}
        </div>
      )}
    </div>
  );
};
