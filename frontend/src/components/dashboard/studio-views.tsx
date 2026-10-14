'use client';

import React, { useState } from 'react';
import { GlassCard } from '../ui/glass-card';
import { 
  Cpu, 
  Terminal, 
  Activity, 
  Brain, 
  Code, 
  Play, 
  Sparkles, 
  Search, 
  CheckCircle2, 
  Clock, 
  Coins, 
  Settings, 
  HelpCircle,
  AlertCircle,
  Sliders,
  Flag,
  Wrench,
  Gauge
} from 'lucide-react';
import { toast } from 'sonner';

// ==========================================
// 1. STUDIO DASHBOARD VIEW
// ==========================================
export const StudioDashboardView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            AgentX Developer Studio
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Build, evaluate, trace, and optimize autonomous multi-agent graph pipelines.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <GlassCard className="p-5 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Gauge className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] font-mono text-zinc-400 uppercase">Avg Graph Latency</p>
            <h3 className="text-lg font-bold text-white mt-0.5">8.42s</h3>
          </div>
        </GlassCard>

        <GlassCard className="p-5 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Coins className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] font-mono text-zinc-400 uppercase">Tokens / Sec</p>
            <h3 className="text-lg font-bold text-white mt-0.5">1,248 t/s</h3>
          </div>
        </GlassCard>

        <GlassCard className="p-5 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] font-mono text-zinc-400 uppercase">Avg Evaluator Score</p>
            <h3 className="text-lg font-bold text-emerald-400 mt-0.5">98.4%</h3>
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard className="p-6 space-y-4">
          <h3 className="text-sm font-semibold text-white">Active Core Agents</h3>
          <div className="space-y-3">
            {[
              { name: 'master_agent', type: 'Supervisor', latency: '240ms' },
              { name: 'research_agent', type: 'Web Intelligence', latency: '1.2s' },
              { name: 'coding_agent', type: 'Sandbox Exec', latency: '980ms' },
              { name: 'evaluator_agent', type: 'Safety Auditor', latency: '410ms' },
            ].map((a) => (
              <div key={a.name} className="flex justify-between items-center p-3 rounded-xl border border-white/[0.04] bg-white/[0.01]">
                <span className="text-xs font-mono font-semibold text-white">{a.name}</span>
                <span className="text-[10px] font-mono text-zinc-400">{a.type} • {a.latency}</span>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="p-6 space-y-4">
          <h3 className="text-sm font-semibold text-white">Execution Metrics</h3>
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-zinc-400">Memory Cache Hit Rate</span>
                <span className="text-white font-mono font-bold">94.2%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-zinc-950 overflow-hidden">
                <div className="h-full bg-indigo-500" style={{ width: '94.2%' }} />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-zinc-400">HITL Approvals Queue</span>
                <span className="text-white font-mono font-bold">0 Pending</span>
              </div>
              <div className="w-full h-2 rounded-full bg-zinc-950 overflow-hidden">
                <div className="h-full bg-emerald-500" style={{ width: '0%' }} />
              </div>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

// ==========================================
// 2. LIVE AGENT MONITOR VIEW
// ==========================================
export const LiveAgentMonitorView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400" />
            Live Agent Monitor & Tracing
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Observe real-time digital operator traces, token expenditures, and memory reads.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { name: 'master_agent', desc: 'Central coordinator. Runs supervisor router nodes.', status: 'IDLE' },
          { name: 'research_agent', desc: 'Scrapes web documentation and fetches online search parameters.', status: 'IDLE' },
          { name: 'coding_agent', desc: 'Compiles, refactors, and runs unit tests in sandboxed shell.', status: 'IDLE' },
          { name: 'evaluator_agent', desc: 'Audits output factuality, correctness, and checks hallucination indices.', status: 'IDLE' },
        ].map((a) => (
          <GlassCard key={a.name} className="p-5 flex flex-col justify-between h-40">
            <div>
              <div className="flex justify-between items-center">
                <span className="text-xs font-mono font-bold text-white uppercase">{a.name.replace('_', ' ')}</span>
                <span className="text-[8px] font-mono font-bold bg-white/[0.04] text-zinc-400 px-2 py-0.5 rounded-full border border-white/[0.05]">
                  {a.status}
                </span>
              </div>
              <p className="text-[11px] text-zinc-400 mt-2 leading-relaxed">{a.desc}</p>
            </div>
            <div className="border-t border-white/[0.03] pt-3 flex justify-between text-[10px] font-mono text-zinc-500">
              <span>TRACES: 14</span>
              <button 
                onClick={() => toast.info(`Opened simulation trace logs for ${a.name}`)}
                className="text-indigo-400 hover:text-indigo-300 transition-colors uppercase"
              >
                Trace operator
              </button>
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};

// ==========================================
// 3. PROMPT STUDIO VIEW
// ==========================================
export const PromptStudioView: React.FC = () => {
  const [prompt, setPrompt] = useState('Write an optimized Python binary search tree helper class.');
  const [model, setModel] = useState('gpt-4o');
  const [evalResult, setEvalResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleEvaluate = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setEvalResult(`Model: ${model}\nEvaluator Grounding: 0.99\nPII Violation Check: Clear\nHallucination Index: 0.01\nOutput size: 450 chars`);
      toast.success('Prompt evaluation completed successfully.');
    }, 1200);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Brain className="w-5 h-5 text-indigo-400" />
            Prompt Engineering Studio
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Tune system instructions, test prompts against evaluation suites, and calculate hallucination metrics.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="lg:col-span-2 p-6 space-y-4">
          <div className="space-y-2">
            <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-widest block">System Instructions / Prompt</label>
            <textarea
              rows={6}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full bg-zinc-900/60 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500/50 leading-relaxed"
            />
          </div>

          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-400">Target Model:</span>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="bg-zinc-900 border border-white/[0.08] text-zinc-300 text-xs rounded-lg px-2 py-1 focus:outline-none"
              >
                <option value="gpt-4o">GPT-4o</option>
                <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                <option value="gemini-1-5-pro">Gemini 1.5 Pro</option>
              </select>
            </div>

            <button
              onClick={handleEvaluate}
              disabled={loading}
              className="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 disabled:bg-indigo-500/50 text-white text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              {loading ? (
                <>
                  <Clock className="w-3.5 h-3.5 animate-spin" /> Evaluating...
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5" /> Run Evaluation
                </>
              )}
            </button>
          </div>
        </GlassCard>

        <GlassCard className="p-6 space-y-4 h-fit">
          <h3 className="text-sm font-semibold text-white">Evaluation Scorecard</h3>
          {evalResult ? (
            <pre className="text-[10px] font-mono text-zinc-300 leading-relaxed bg-zinc-950 p-4 rounded-xl border border-white/[0.05] whitespace-pre-wrap">
              {evalResult}
            </pre>
          ) : (
            <p className="text-xs text-zinc-500 italic">No runs executed yet.</p>
          )}
        </GlassCard>
      </div>
    </div>
  );
};

// ==========================================
// 4. MODEL ROUTER PLAYGROUND
// ==========================================
export const ModelPlaygroundView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            Model Router Playground
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Test model aliasing, verify provider configurations, and calculate routing thresholds.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <GlassCard className="p-6 space-y-4">
          <h3 className="text-sm font-semibold text-white">Available Model Aliases</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { alias: 'REASONING_MODEL', resolved: 'gpt-4o', latency: '120ms' },
              { alias: 'EXTRACTION_MODEL', resolved: 'gpt-4o-mini', latency: '40ms' },
              { alias: 'FAST_ROUTER_MODEL', resolved: 'gpt-4o-mini', latency: '35ms' },
            ].map((m) => (
              <div key={m.alias} className="p-4 rounded-xl border border-white/[0.04] bg-white/[0.01]">
                <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider block">{m.alias}</span>
                <span className="text-xs font-semibold text-white mt-1 block">{m.resolved}</span>
                <span className="text-[10px] text-zinc-400 mt-1.5 block">Ping Latency: {m.latency}</span>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

// ==========================================
// 5. API EXPLORER VIEW
// ==========================================
export const ApiExplorerView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Code className="w-5 h-5 text-indigo-400" />
            FastAPI Kernel API Explorer
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Directly invoke kernel routes, inspect schemas, and query DB models.
          </p>
        </div>
      </div>

      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm font-semibold text-white">Kernel Routes</h3>
        <div className="space-y-3">
          {[
            { method: 'GET', path: '/goals/', desc: 'List active or historic goals.' },
            { method: 'POST', path: '/goals/', desc: 'Create and decompose a new goal.' },
            { method: 'POST', path: '/workflows/pause/{goal_id}', desc: 'Pause active goal runtime loop.' },
            { method: 'GET', path: '/approvals/', desc: 'List pending tool verification approvals.' },
            { method: 'GET', path: '/admin/system/metrics', desc: 'Retrieve admin statistics.' },
          ].map((r) => (
            <div key={r.path} className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 rounded-xl border border-white/[0.04] bg-white/[0.01] gap-2">
              <div className="flex items-center gap-3">
                <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded ${
                  r.method === 'GET' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-indigo-500/10 text-indigo-400'
                }`}>
                  {r.method}
                </span>
                <span className="text-xs font-mono text-zinc-200">{r.path}</span>
              </div>
              <span className="text-xs text-zinc-400">{r.desc}</span>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
};

// ==========================================
// 6. LATENCY & PERFORMANCE METRICS
// ==========================================
export const LatencyMetricsView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400" />
            Performance & Latency Profiler
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Trace step latencies, calculate token consumption, and audit performance flags.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard className="p-5 flex flex-col justify-between h-32">
          <p className="text-[10px] font-mono text-zinc-400 uppercase">Supervisor Latency</p>
          <h3 className="text-2xl font-bold text-white mt-1">210ms</h3>
          <span className="text-[9px] font-mono text-emerald-400">Normal operating bounds</span>
        </GlassCard>

        <GlassCard className="p-5 flex flex-col justify-between h-32">
          <p className="text-[10px] font-mono text-zinc-400 uppercase">Model Call Failures</p>
          <h3 className="text-2xl font-bold text-white mt-1">0.00%</h3>
          <span className="text-[9px] font-mono text-emerald-400">Zero timeouts recorded</span>
        </GlassCard>

        <GlassCard className="p-5 flex flex-col justify-between h-32">
          <p className="text-[10px] font-mono text-zinc-400 uppercase">API Route Jitter</p>
          <h3 className="text-2xl font-bold text-white mt-1">4.2ms</h3>
          <span className="text-[9px] font-mono text-emerald-400">Extremely low latency skew</span>
        </GlassCard>
      </div>
    </div>
  );
};

// ==========================================
// 7. DEVELOPER SETTINGS & FEATURE FLAGS
// ==========================================
export const DeveloperSettingsView: React.FC = () => {
  const [flags, setFlags] = useState({
    mockLlm: false,
    digitalTwinSync: true,
    hnswVector: true,
    eventBusAsync: true,
  });

  const toggleFlag = (key: keyof typeof flags) => {
    const updated = { ...flags, [key]: !flags[key] };
    setFlags(updated);
    toast.success('Feature flags updated successfully.');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Settings className="w-5 h-5 text-indigo-400" />
            Developer Parameters & Feature Flags
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Toggle offline simulation flags, optimize memory configurations, and customize developer workspaces.
          </p>
        </div>
      </div>

      <GlassCard className="p-6 space-y-6 max-w-2xl">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Flag className="w-4 h-4 text-indigo-400" />
          Platform Feature Flags
        </h3>

        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 rounded-xl border border-white/[0.04] bg-white/[0.01]">
            <div>
              <h4 className="text-xs font-bold text-white uppercase">Mock LLM Responses</h4>
              <p className="text-[10px] text-zinc-400 mt-0.5">Use offline mock templates instead of making OpenAI/Anthropic network calls.</p>
            </div>
            <button
              onClick={() => toggleFlag('mockLlm')}
              className={`w-12 h-6 rounded-full p-1 transition-all ${
                flags.mockLlm ? 'bg-indigo-500 flex justify-end' : 'bg-zinc-800 flex justify-start'
              }`}
            >
              <div className="w-4 h-4 bg-white rounded-full" />
            </button>
          </div>

          <div className="flex justify-between items-center p-4 rounded-xl border border-white/[0.04] bg-white/[0.01]">
            <div>
              <h4 className="text-xs font-bold text-white uppercase">Synchronous Digital Twin Profile Sync</h4>
              <p className="text-[10px] text-zinc-400 mt-0.5">Save preference fact updates instantly to database Vector tables during runs.</p>
            </div>
            <button
              onClick={() => toggleFlag('digitalTwinSync')}
              className={`w-12 h-6 rounded-full p-1 transition-all ${
                flags.digitalTwinSync ? 'bg-indigo-500 flex justify-end' : 'bg-zinc-800 flex justify-start'
              }`}
            >
              <div className="w-4 h-4 bg-white rounded-full" />
            </button>
          </div>

          <div className="flex justify-between items-center p-4 rounded-xl border border-white/[0.04] bg-white/[0.01]">
            <div>
              <h4 className="text-xs font-bold text-white uppercase">HNSW Graph Vector Indexing</h4>
              <p className="text-[10px] text-zinc-400 mt-0.5">Optimizes context retrieval speeds for large document vectors.</p>
            </div>
            <button
              onClick={() => toggleFlag('hnswVector')}
              className={`w-12 h-6 rounded-full p-1 transition-all ${
                flags.hnswVector ? 'bg-indigo-500 flex justify-end' : 'bg-zinc-800 flex justify-start'
              }`}
            >
              <div className="w-4 h-4 bg-white rounded-full" />
            </button>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
