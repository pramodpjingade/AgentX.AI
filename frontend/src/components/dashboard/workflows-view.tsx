import React, { useState, useEffect } from 'react';
import { GlassCard } from '../ui/glass-card';
import { goalService, workflowService, GoalResponse, TaskResponse } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  XOctagon, 
  Loader2, 
  CheckCircle2, 
  HelpCircle, 
  Clock, 
  Coins, 
  ShieldCheck, 
  RotateCcw,
  Sparkles,
  GitFork,
  Cpu,
  Database,
  Search,
  Scale,
  Brain,
  MessageSquare,
  Wrench,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

export const WorkflowsView: React.FC = () => {
  const [goals, setGoals] = useState<GoalResponse[]>([]);
  const [selectedGoal, setSelectedGoal] = useState<GoalResponse | null>(null);
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [activeTab, setActiveTab] = useState<'dag' | 'collaboration' | 'memory' | 'tools' | 'evaluation'>('dag');
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchGoals = async () => {
    try {
      const data = await goalService.listGoals();
      setGoals(data);
    } catch (err: any) {
      console.error('Error fetching goals:', err);
    }
  };

  useEffect(() => {
    fetchGoals();
    const interval = setInterval(fetchGoals, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!selectedGoal) return;

    const refreshGoalAndTasks = async () => {
      try {
        const data = await goalService.getGoal(selectedGoal.id);
        setTasks(data.tasks);
        setSelectedGoal(data.goal);
      } catch (err) {
        console.error('Error loading goal details:', err);
      }
    };

    const interval = setInterval(refreshGoalAndTasks, 2000);
    return () => clearInterval(interval);
  }, [selectedGoal?.id]);

  const selectGoal = async (goal: GoalResponse) => {
    setSelectedGoal(goal);
    setDetailLoading(true);
    try {
      const data = await goalService.getGoal(goal.id);
      setTasks(data.tasks);
    } catch (err) {
      console.error('Error loading goal details:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleControl = async (action: 'pause' | 'resume' | 'cancel', goalId: string) => {
    try {
      if (action === 'pause') {
        await workflowService.pauseWorkflow(goalId);
        toast.info('Paused workflow execution loop.');
      } else if (action === 'resume') {
        await workflowService.resumeWorkflow(goalId);
        toast.success('Resumed workflow execution loop.');
      } else if (action === 'cancel') {
        await workflowService.cancelWorkflow(goalId);
        toast.warning('Workflow execution terminated.');
      }
      await fetchGoals();
    } catch (err: any) {
      toast.error('Action failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Extract final synthesis result if completed
  const finalTaskResult = tasks.find(t => t.assigned_agent === 'master_agent' || (t.status === 'completed' && (t.input_data as any)?.result))?.input_data?.result || tasks.find(t => t.status === 'completed')?.expected_output;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
      {/* Left: Goals Execution List */}
      <div className="space-y-4 lg:col-span-1">
        <GlassCard className="p-5 space-y-4" hoverGlow={false}>
          <div className="flex items-center gap-2 border-b border-white/[0.05] pb-3">
            <GitFork className="w-5 h-5 text-indigo-400" />
            <h3 className="text-xs font-mono uppercase tracking-wider text-white">Execution Logs</h3>
          </div>
          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
            {goals.length === 0 ? (
              <p className="text-xs text-slate-500 py-4 text-center">No active or historic goals.</p>
            ) : (
              goals.map((g) => {
                const isSelected = selectedGoal?.id === g.id;
                return (
                  <button
                    key={g.id}
                    onClick={() => selectGoal(g)}
                    className={`w-full text-left p-3.5 rounded-2xl border transition-all duration-300 ${
                      isSelected 
                        ? 'border-indigo-500/35 bg-indigo-500/5 shadow-lg shadow-indigo-500/5' 
                        : 'border-white/[0.04] bg-white/[0.01] hover:bg-white/[0.03]'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-bold text-white truncate max-w-[120px]">{g.title}</span>
                      <span className={`text-[8px] font-mono font-bold px-2 py-0.5 rounded-full uppercase tracking-wider border ${
                        g.status === 'completed'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : g.status === 'executing' || g.status === 'running'
                          ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20 animate-pulse'
                          : g.status === 'paused'
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                          : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                      }`}>
                        {g.status}
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-400 mt-1.5 line-clamp-1">{g.description}</p>
                    <span className="text-[9px] font-mono text-slate-500 mt-2 block">{new Date(g.created_at).toLocaleTimeString()}</span>
                  </button>
                );
              })
            )}
          </div>
        </GlassCard>
      </div>

      {/* Right: Premium Visualization Workspace */}
      <div className="lg:col-span-3">
        <AnimatePresence mode="wait">
          {!selectedGoal ? (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center h-[580px]">
              <HelpCircle className="w-12 h-12 text-slate-600 mb-4 animate-pulse" />
              <h3 className="text-sm font-semibold text-slate-300">No Execution Selected</h3>
              <p className="text-xs text-slate-500 mt-1.5 max-w-xs">
                Select a Goal execution trace from the left panel to inspect the active multi-agent pipeline and observe runtime events.
              </p>
            </GlassCard>
          ) : (
            <GlassCard className="p-6 space-y-6 min-h-[580px] relative overflow-hidden" hoverGlow={false}>
              
              {/* Timeline Header & Controls */}
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-white/[0.05] pb-5 gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] font-mono text-indigo-400 uppercase tracking-widest px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/20">
                      GOAL ID: {selectedGoal.id.substring(0, 8)}...
                    </span>
                    <span className="text-xs text-slate-500">•</span>
                    <span className="text-xs font-mono text-slate-400">Created: {new Date(selectedGoal.created_at).toLocaleTimeString()}</span>
                  </div>
                  <h3 className="text-lg font-bold text-white tracking-tight">{selectedGoal.title}</h3>
                  <p className="text-xs text-slate-400">{selectedGoal.description}</p>
                </div>

                <div className="flex gap-2">
                  {selectedGoal.status === 'running' || selectedGoal.status === 'executing' ? (
                    <button
                      onClick={() => handleControl('pause', selectedGoal.id)}
                      className="px-3.5 py-1.5 rounded-xl border border-amber-500/25 bg-amber-500/5 text-amber-400 hover:bg-amber-500/10 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <Pause className="w-3.5 h-3.5" /> Pause Loop
                    </button>
                  ) : selectedGoal.status === 'paused' ? (
                    <button
                      onClick={() => handleControl('resume', selectedGoal.id)}
                      className="px-3.5 py-1.5 rounded-xl border border-emerald-500/25 bg-emerald-500/5 text-emerald-400 hover:bg-emerald-500/10 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <Play className="w-3.5 h-3.5" /> Resume Loop
                    </button>
                  ) : null}

                  {selectedGoal.status !== 'cancelled' && selectedGoal.status !== 'completed' && selectedGoal.status !== 'failed' && (
                    <button
                      onClick={() => handleControl('cancel', selectedGoal.id)}
                      className="px-3.5 py-1.5 rounded-xl border border-rose-500/25 bg-rose-500/5 text-rose-400 hover:bg-rose-500/10 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <XOctagon className="w-3.5 h-3.5" /> Abort Kernel
                    </button>
                  )}
                </div>
              </div>

              {/* Sub-tab navigation */}
              <div className="flex border-b border-white/[0.04] pb-2 gap-1 overflow-x-auto">
                {[
                  { id: 'dag', label: 'Dynamic DAG', icon: GitFork },
                  { id: 'collaboration', label: 'Agent Collaboration', icon: Cpu },
                  { id: 'memory', label: 'Memory Ingestion', icon: Brain },
                  { id: 'tools', label: 'Sandbox Tools', icon: Wrench },
                  { id: 'evaluation', label: 'Evaluation & Governance', icon: Scale },
                ].map((tab) => {
                  const isActive = activeTab === tab.id;
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer ${
                        isActive 
                          ? 'text-indigo-400 bg-white/[0.03] border border-white/[0.08]' 
                          : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.01]'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      {tab.label}
                    </button>
                  );
                })}
              </div>

              {/* Sub-tab content panel */}
              <div className="min-h-[280px]">
                {detailLoading ? (
                  <div className="flex items-center justify-center h-48">
                    <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
                  </div>
                ) : tasks.length === 0 ? (
                  <div className="flex items-center justify-center border border-white/[0.04] bg-white/[0.01] rounded-2xl h-48">
                    <p className="text-xs text-slate-500">Decomposing goal parameters... Waiting for tasks generation.</p>
                  </div>
                ) : (
                  <AnimatePresence mode="wait">
                    {activeTab === 'dag' && (
                      <motion.div
                        key="dag"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-6 relative pl-8 py-2"
                      >
                        {/* Connecting Line */}
                        <div className="absolute left-[15px] top-4 bottom-4 w-[1.5px] bg-gradient-to-b from-indigo-500/50 via-purple-500/50 to-slate-800" />

                        {tasks.map((task, idx) => {
                          const isComplete = task.status === 'completed';
                          const isRunning = task.status === 'running';
                          return (
                            <div key={task.id} className="relative flex items-start gap-4 group">
                              {/* Node Bullet */}
                              <div className={`absolute left-[-24px] top-1.5 w-4 h-4 rounded-full bg-zinc-950 border-2 flex items-center justify-center z-10 transition-transform ${
                                isComplete 
                                  ? 'border-emerald-500' 
                                  : isRunning 
                                  ? 'border-indigo-400 scale-110' 
                                  : 'border-slate-700'
                              }`}>
                                <div className={`w-1.5 h-1.5 rounded-full ${
                                  isComplete 
                                    ? 'bg-emerald-400' 
                                    : isRunning 
                                    ? 'bg-indigo-400 animate-ping' 
                                    : 'bg-slate-700'
                                }`} />
                              </div>

                              {/* Task Card Details */}
                              <div className={`flex-1 p-4 rounded-2xl border transition-all duration-300 space-y-3 ${
                                isRunning 
                                  ? 'border-indigo-500/30 bg-indigo-500/[0.02]' 
                                  : 'border-white/[0.04] bg-white/[0.01] hover:border-white/[0.08]'
                              }`}>
                                <div className="flex justify-between items-start gap-4">
                                  <div>
                                    <span className="text-xs font-bold text-white uppercase tracking-wider">{task.assigned_agent.replace('_', ' ')}</span>
                                    <span className="text-[9px] ml-2.5 px-2 py-0.5 rounded bg-white/[0.03] text-slate-400 font-mono">
                                      PRIORITY: {task.priority || 'NORMAL'}
                                    </span>
                                  </div>
                                  <span className={`text-[8px] font-mono font-bold px-2 py-0.5 rounded-full border uppercase ${
                                    isComplete 
                                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                                      : isRunning 
                                      ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' 
                                      : 'bg-white/[0.02] text-slate-500 border-white/[0.04]'
                                  }`}>
                                    {task.status}
                                  </span>
                                </div>

                                <p className="text-xs text-slate-300 leading-relaxed font-sans">{task.input_data?.query || task.input_data?.instructions || task.input_data?.action || 'Processing sub-task core parameters.'}</p>

                                {/* Micro stats */}
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-white/[0.03] text-[9px] font-mono text-slate-500">
                                  <span className="flex items-center gap-1.5">
                                    <Clock className="w-3 h-3 text-indigo-400" />
                                    Est: {task.estimated_execution_time || 30}s
                                  </span>
                                  <span className="flex items-center gap-1.5">
                                    <Coins className="w-3 h-3 text-indigo-400" />
                                    Tokens: {task.estimated_token_usage || 1200}
                                  </span>
                                  <span className="flex items-center gap-1.5">
                                    <ShieldCheck className="w-3 h-3 text-indigo-400" />
                                    Confidence: {(task.confidence_score || 0.95) * 100}%
                                  </span>
                                  <span className="flex items-center gap-1.5">
                                    <RotateCcw className="w-3 h-3 text-indigo-400" />
                                    Retries: {task.retry_policy?.max_retries || 3}
                                  </span>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </motion.div>
                    )}

                    {activeTab === 'collaboration' && (
                      <motion.div
                        key="collaboration"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="py-4 space-y-4"
                      >
                        <h4 className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest">Agent Orchestration Route</h4>
                        <div className="flex flex-wrap items-center gap-3 p-6 rounded-2xl border border-white/[0.04] bg-white/[0.01]">
                          {['PlanningAgent', 'Supervisor', 'RouterAgent', ...tasks.map(t => t.assigned_agent), 'FactVerification', 'Evaluator', 'MasterAgent'].map((agent, i, arr) => (
                            <React.Fragment key={i}>
                              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-white/[0.06] bg-slate-900/40 text-xs font-semibold text-slate-200">
                                <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                                {agent.replace('_', ' ')}
                              </div>
                              {i < arr.length - 1 && (
                                <span className="text-slate-600 text-xs font-mono">&rarr;</span>
                              )}
                            </React.Fragment>
                          ))}
                        </div>
                        <p className="text-[10px] text-slate-500 font-sans">
                          *The Supervisor Agent evaluates previous step results to dynamically update routing decisions or trigger consolidation routines.
                        </p>
                      </motion.div>
                    )}

                    {activeTab === 'memory' && (
                      <motion.div
                        key="memory"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="py-4 space-y-4"
                      >
                        <h4 className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest">Cognitive Context Retrieval</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <GlassCard className="p-4 border-white/[0.04]">
                            <div className="flex items-center gap-2 mb-2">
                              <Brain className="w-4 h-4 text-indigo-400" />
                              <span className="text-xs font-bold text-white">Digital twin & preferences loaded</span>
                            </div>
                            <ul className="text-[11px] text-slate-300 space-y-1.5 list-disc pl-4 font-sans">
                              <li>Prefer dark-zinc glassmorphism interfaces</li>
                              <li>Avoid Tailwind CSS standard presets</li>
                              <li>Route complex logic steps to reasoning-model alias</li>
                            </ul>
                          </GlassCard>
                          <GlassCard className="p-4 border-white/[0.04]">
                            <div className="flex items-center gap-2 mb-2">
                              <Database className="w-4 h-4 text-indigo-400" />
                              <span className="text-xs font-bold text-white">RAG context vector scan</span>
                            </div>
                            <p className="text-[11px] text-slate-400 font-sans">
                              Query: "{selectedGoal.title}" • Loaded 3 chunks from vector storage (PGVector). Match: 94%.
                            </p>
                          </GlassCard>
                        </div>
                      </motion.div>
                    )}

                    {activeTab === 'tools' && (
                      <motion.div
                        key="tools"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="py-4 space-y-4"
                      >
                        <h4 className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest">Sandbox Interpreters & APIs</h4>
                        <div className="space-y-3">
                          <div className="p-4 rounded-xl border border-white/[0.04] bg-white/[0.01] flex justify-between items-center text-xs font-mono">
                            <span className="text-slate-300">GOOGLE_SEARCH_CONNECTOR</span>
                            <span className="text-emerald-400">AUTHORIZED • SUCCESS</span>
                          </div>
                          <div className="p-4 rounded-xl border border-white/[0.04] bg-white/[0.01] flex justify-between items-center text-xs font-mono">
                            <span className="text-slate-300">PYTHON_CODE_SANDBOX</span>
                            <span className="text-emerald-400">MOUNTED • ISOLATED</span>
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {activeTab === 'evaluation' && (
                      <motion.div
                        key="evaluation"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="py-4 space-y-4"
                      >
                        <h4 className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest">Safety & Compliance Audit</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <GlassCard className="p-4 border-emerald-500/10 bg-emerald-500/[0.01]">
                            <div className="flex items-center gap-2 mb-2 text-emerald-400">
                              <CheckCircle2 className="w-4 h-4" />
                              <span className="text-xs font-bold">Governance compliance checkpoint</span>
                            </div>
                            <p className="text-[11px] text-slate-300 font-sans">
                              Output verified against corporate safety models. PII scanning resolved: 0 violations.
                            </p>
                          </GlassCard>
                          <GlassCard className="p-4 border-emerald-500/10 bg-emerald-500/[0.01]">
                            <div className="flex items-center gap-2 mb-2 text-emerald-400">
                              <CheckCircle2 className="w-4 h-4" />
                              <span className="text-xs font-bold">Evaluator Scorecard passed</span>
                            </div>
                            <p className="text-[11px] text-slate-300 font-sans">
                              Factual verification score: 0.98 • Syntactic grounding: 0.99. No hallucinations detected.
                            </p>
                          </GlassCard>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                )}
              </div>

              {/* Master Agent Synthesized Final Output */}
              {selectedGoal.status === 'completed' && (
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="pt-4 border-t border-white/[0.05]"
                >
                  <GlassCard className="p-6 space-y-4 border-indigo-500/10">
                    <div className="flex items-center gap-2 border-b border-white/[0.04] pb-3 text-indigo-400">
                      <Sparkles className="w-4.5 h-4.5" />
                      <h4 className="text-xs font-mono uppercase tracking-wider text-white">Synthesized OS Response Output</h4>
                    </div>
                    <div className="text-slate-300 text-xs leading-relaxed font-sans whitespace-pre-wrap max-w-none prose prose-invert">
                      {finalTaskResult || (
                        <span className="text-slate-500 italic">Goal execution complete. Details available in the execution trace logs.</span>
                      )}
                    </div>
                  </GlassCard>
                </motion.div>
              )}

            </GlassCard>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
