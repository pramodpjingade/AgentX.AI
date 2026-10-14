'use client';

import React, { useState, useEffect } from 'react';
import { useAppStore } from '@/store';
import { goalService, workflowService, GoalDetailResponse, TaskResponse } from '@/services/api';
import { GlassCard } from '@/components/ui/glass-card';
import { MissionRenderer, MissionResultPayload } from './mission-renderer';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowLeft, 
  Play, 
  Pause, 
  XSquare, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  FileText, 
  MessageSquare, 
  Layers, 
  Download, 
  Copy, 
  Loader2,
  Sparkles,
  ShieldCheck,
  Send
} from 'lucide-react';
import { toast } from 'sonner';

type WorkspaceTab = 'overview' | 'deliverables' | 'tasks' | 'logs' | 'chat' | 'conversation' | 'files' | 'timeline';

export const MissionWorkspaceView: React.FC = () => {
  const { selectedGoalId, setActiveView, user } = useAppStore();
  const [goalDetail, setGoalDetail] = useState<GoalDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('deliverables');
  const [actionLoading, setActionLoading] = useState(false);
  const [chatMessage, setChatMessage] = useState('');

  const isDevOrAdmin = user?.role?.toLowerCase() === 'developer' || user?.role?.toLowerCase() === 'admin';

  const formatAgentName = (agent: string) => {
    if (isDevOrAdmin) {
      return agent.replace(/_/g, ' ');
    }
    const map: Record<string, string> = {
      'research_agent': 'Information & Knowledge Gathering',
      'business_agent': 'Strategic Analysis & Solution Formulation',
      'coding_agent': 'Software & Code Engineering',
      'cybersecurity_agent': 'Security & Compliance Inspection',
      'evaluator_agent': 'Quality Assurance & Validation',
      'fact_verification_agent': 'Fact Verification & Accuracy Check',
      'master_agent': 'Final Deliverable Consolidation'
    };
    return map[agent.toLowerCase()] || 'Milestone Execution Phase';
  };

  useEffect(() => {
    if (selectedGoalId) {
      fetchGoalDetails(selectedGoalId);
      const interval = setInterval(() => {
        fetchGoalDetails(selectedGoalId, true);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [selectedGoalId]);

  const fetchGoalDetails = async (id: string, isPoll = false) => {
    try {
      if (!isPoll) setLoading(true);
      const data = await goalService.getGoal(id);
      setGoalDetail(data);
    } catch (err: any) {
      console.error('Failed to load goal detail:', err);
    } finally {
      if (!isPoll) setLoading(false);
    }
  };

  const handlePause = async () => {
    if (!selectedGoalId) return;
    setActionLoading(true);
    try {
      await workflowService.pauseWorkflow(selectedGoalId);
      toast.info('Mission execution paused.');
      fetchGoalDetails(selectedGoalId);
    } catch (err: any) {
      toast.error('Failed to pause mission: ' + (err.message || 'Unknown error'));
    } finally {
      setActionLoading(false);
    }
  };

  const handleResume = async () => {
    if (!selectedGoalId) return;
    setActionLoading(true);
    try {
      await workflowService.resumeWorkflow(selectedGoalId);
      toast.success('Mission execution resumed.');
      fetchGoalDetails(selectedGoalId);
    } catch (err: any) {
      toast.error('Failed to resume mission: ' + (err.message || 'Unknown error'));
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!selectedGoalId) return;
    setActionLoading(true);
    try {
      await workflowService.cancelWorkflow(selectedGoalId);
      toast.warning('Mission execution cancelled.');
      fetchGoalDetails(selectedGoalId);
    } catch (err: any) {
      toast.error('Failed to cancel mission: ' + (err.message || 'Unknown error'));
    } finally {
      setActionLoading(false);
    }
  };

  const handleCopyText = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Deliverable content copied to clipboard!');
  };

  if (!selectedGoalId) {
    return (
      <div className="p-12 text-center max-w-xl mx-auto space-y-4">
        <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto" />
        <h2 className="text-xl font-bold text-white">No Mission Selected</h2>
        <p className="text-sm text-zinc-400">Select an existing mission from Home or launch a new mission.</p>
        <button
          onClick={() => setActiveView('home')}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold"
        >
          Return to Home
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-16 text-center max-w-md mx-auto space-y-3">
        <Loader2 className="w-8 h-8 text-indigo-400 animate-spin mx-auto" />
        <p className="text-xs font-mono text-zinc-400 uppercase tracking-widest">LOADING MISSION WORKSPACE...</p>
      </div>
    );
  }

  const goal = goalDetail?.goal;
  const tasks = goalDetail?.tasks || [];
  const completedTasks = tasks.filter(t => t.status === 'completed');
  const progressPercent = tasks.length > 0 ? Math.round((completedTasks.length / tasks.length) * 100) : 0;
  const isExecuting = goal?.status === 'executing' || goal?.status === 'running';

  // Extract synthesized result if available
  const synthesizedTask = tasks.find(t => t.assigned_agent === 'master_agent' || (t.input_data && t.input_data.result));
  const deliverablesText = synthesizedTask?.input_data?.result || tasks.map(t => t.expected_output || t.input_data?.query).filter(Boolean).join('\n\n');

  return (
    <div className="space-y-8 max-w-6xl mx-auto py-2">
      {/* Back Button & Mission Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/[0.06] pb-6">
        <div className="space-y-2">
          <button
            onClick={() => setActiveView('home')}
            className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Missions</span>
          </button>

          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-white">{goal?.title}</h1>
            <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase border ${
              goal?.status === 'completed' 
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
                : isExecuting 
                ? 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400 animate-pulse' 
                : 'bg-zinc-800 border-zinc-700 text-zinc-400'
            }`}>
              {goal?.status}
            </span>
          </div>
          <p className="text-xs text-zinc-400 max-w-2xl">{goal?.description}</p>
        </div>

        {/* Runtime Workflow Controls */}
        <div className="flex items-center gap-2">
          {isExecuting && (
            <button
              onClick={handlePause}
              disabled={actionLoading}
              className="px-3.5 py-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 text-amber-300 text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <Pause className="w-3.5 h-3.5" /> Pause
            </button>
          )}

          {goal?.status === 'paused' && (
            <button
              onClick={handleResume}
              disabled={actionLoading}
              className="px-3.5 py-2 rounded-xl bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-300 text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <Play className="w-3.5 h-3.5" /> Resume
            </button>
          )}

          {goal?.status !== 'completed' && goal?.status !== 'cancelled' && (
            <button
              onClick={handleCancel}
              disabled={actionLoading}
              className="px-3.5 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 text-rose-300 text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <XSquare className="w-3.5 h-3.5" /> Cancel
            </button>
          )}
        </div>
      </div>

      {/* Navigation Tabs Header */}
      <div className="flex items-center gap-2 border-b border-white/[0.06] overflow-x-auto pb-1">
        {[
          { id: 'deliverables', label: 'Deliverables', icon: Sparkles },
          { id: 'overview', label: 'Overview', icon: Layers },
          { id: 'conversation', label: 'Conversation', icon: MessageSquare },
          { id: 'files', label: 'Files', icon: FileText },
          { id: 'timeline', label: 'Timeline', icon: Clock },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as WorkspaceTab)}
              className={`px-4 py-2.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 cursor-pointer ${
                isActive 
                  ? 'bg-white/[0.08] text-white border border-white/[0.1]' 
                  : 'text-zinc-400 hover:text-white hover:bg-white/[0.03]'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-zinc-400'}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      <AnimatePresence mode="wait">
        {activeTab === 'deliverables' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-4">
            {goalDetail?.mission_result ? (
              <MissionRenderer mission={goalDetail.mission_result as MissionResultPayload} />
            ) : (
              <GlassCard className="p-6 border-white/[0.06] space-y-4">
                <div className="flex items-center justify-between border-b border-white/[0.06] pb-3">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-indigo-400" />
                    Synthesized Deliverable Report
                  </h3>
                  <button
                    onClick={() => handleCopyText(deliverablesText || '')}
                    className="p-2 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-xs text-zinc-300 flex items-center gap-1.5 cursor-pointer"
                  >
                    <Copy className="w-3.5 h-3.5" /> Copy Text
                  </button>
                </div>
                <div className="bg-zinc-950 p-5 rounded-xl border border-white/[0.05] text-xs font-mono text-zinc-300 leading-relaxed overflow-x-auto whitespace-pre-wrap">
                  {deliverablesText || 'Deliverable synthesis in progress. Please check back shortly.'}
                </div>
              </GlassCard>
            )}
          </motion.div>
        )}

        {activeTab === 'overview' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-6">
            {/* Primary Deliverable View Card */}
            {goalDetail?.mission_result && (
              <div className="space-y-2">
                <h3 className="text-xs font-mono text-indigo-400 uppercase tracking-widest flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5" /> MISSION DELIVERABLE OUTCOME
                </h3>
                <MissionRenderer mission={goalDetail.mission_result as MissionResultPayload} />
              </div>
            )}

            {/* Progress Bar Card */}
            <GlassCard className="p-6 border-white/[0.06] space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-zinc-400">MISSION EXECUTION PROGRESS</span>
                <span className="text-indigo-400 font-bold">{progressPercent}%</span>
              </div>
              <div className="w-full h-2.5 rounded-full bg-zinc-900 overflow-hidden border border-white/[0.05]">
                <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500" style={{ width: `${progressPercent}%` }} />
              </div>
              <div className="flex items-center justify-between text-[11px] text-zinc-400 pt-1">
                <span>Completed Tasks: {completedTasks.length} / {tasks.length}</span>
                <span>Created: {new Date(goal?.created_at || '').toLocaleString()}</span>
              </div>
            </GlassCard>

            {/* Task Breakdown */}
            <div className="space-y-3">
              <h3 className="text-xs font-mono text-zinc-400 uppercase tracking-widest">MISSION MILESTONES & PHASES</h3>
              <div className="space-y-2">
                {tasks.map((t, idx) => (
                  <GlassCard key={t.id || idx} className="p-4 border-white/[0.05] flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                        t.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-zinc-800 text-zinc-400'
                      }`}>
                        {t.status === 'completed' ? <CheckCircle2 className="w-4 h-4" /> : idx + 1}
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-white capitalize">{formatAgentName(t.assigned_agent)}</h4>
                        <p className="text-xs text-zinc-400 line-clamp-1">{t.expected_output || 'Processing milestone specifications...'}</p>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-zinc-800 text-zinc-400">{t.status}</span>
                  </GlassCard>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'conversation' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-4">
            <GlassCard className="p-6 border-white/[0.06] space-y-4 min-h-[300px]">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 text-xs font-bold">AI</div>
                <div className="bg-zinc-900/60 border border-white/[0.06] rounded-2xl p-4 text-xs text-zinc-200 space-y-2 max-w-2xl">
                  <p className="font-semibold text-white">AgentX Operating System</p>
                  <p>I am executing your mission: &ldquo;{goal?.title}&rdquo;. All subtasks are being synthesized into your final deliverables.</p>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {activeTab === 'files' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <GlassCard className="p-8 text-center border-white/[0.06] space-y-2">
              <FileText className="w-8 h-8 text-zinc-500 mx-auto" />
              <h4 className="text-sm font-bold text-white">Attached & Generated Artifacts</h4>
              <p className="text-xs text-zinc-400">All input attachments and final document exports will be displayed here.</p>
            </GlassCard>
          </motion.div>
        )}

        {activeTab === 'timeline' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-3">
            <GlassCard className="p-6 border-white/[0.06] space-y-4">
              <h4 className="text-xs font-mono text-zinc-400 uppercase tracking-widest">MISSION EXECUTION TIMELINE</h4>
              <div className="space-y-4 border-l-2 border-indigo-500/30 pl-4 ml-2">
                <div className="relative">
                  <span className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-indigo-500" />
                  <p className="text-xs font-bold text-white">Mission Created & Decomposed</p>
                  <p className="text-[10px] text-zinc-400">{new Date(goal?.created_at || '').toLocaleString()}</p>
                </div>
                {completedTasks.map((t, i) => (
                  <div key={i} className="relative">
                    <span className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-emerald-400" />
                    <p className="text-xs font-bold text-white">{formatAgentName(t.assigned_agent)} Completed</p>
                    <p className="text-[10px] text-zinc-400">{t.expected_output || 'Milestone output stored successfully'}</p>
                  </div>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
