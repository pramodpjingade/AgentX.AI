import React, { useState, useEffect } from 'react';
import { GlassCard } from '../ui/glass-card';
import { 
  Database, 
  Brain, 
  BookOpen, 
  Bot, 
  Wrench, 
  ShoppingBag, 
  LineChart, 
  Activity, 
  Layers, 
  Settings, 
  User, 
  HelpCircle, 
  FileText, 
  ShieldAlert, 
  Plus, 
  Search, 
  Check, 
  Cpu, 
  Power,
  Play,
  RotateCcw,
  Sparkles,
  GitBranch,
  RefreshCw,
  Terminal,
  Lock,
  Wifi,
  Clock,
  Layers3,
  Server
} from 'lucide-react';
import { toast } from 'sonner';
import { api } from '@/services/api';

// ==========================================
// 1. MEMORY BANK VIEW
// ==========================================
export const MemoryView: React.FC = () => {
  const [memories, setMemories] = useState([
    { id: '1', type: 'semantic', content: 'User prefers dark zinc-950 layouts and fluid framer-motion transitions.', date: '10 mins ago' },
    { id: '2', type: 'preference', content: 'Preferred default reasoning model configured as GPT-4o.', date: '1 hour ago' },
    { id: '3', type: 'episodic', content: 'Successfully resolved task: Generate FastAPI REST Server Template.', date: 'Yesterday' },
    { id: '4', type: 'preference', content: 'Avoids using Tailwind CSS unless explicitly requested.', date: '2 days ago' },
  ]);
  const [newMemory, setNewMemory] = useState('');
  const [memoryType, setMemoryType] = useState('semantic');

  const handleAdd = () => {
    if (!newMemory.trim()) return;
    setMemories([
      { id: Date.now().toString(), type: memoryType, content: newMemory, date: 'Just now' },
      ...memories
    ]);
    setNewMemory('');
    toast.success('Fact successfully stored into core cognitive memory bank.');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Brain className="w-5 h-5 text-indigo-400" />
            Memory Bank & Digital Twin Profile
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Personalized episodic, semantic, and preference memory modules synced dynamically.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Memory Input */}
        <GlassCard className="p-6 space-y-4 h-fit">
          <h3 className="text-sm font-semibold text-white">Record Fact or Preference</h3>
          <div className="space-y-3">
            <div>
              <label className="text-[10px] font-mono text-slate-400 uppercase tracking-widest block mb-1">Memory Category</label>
              <select 
                value={memoryType} 
                onChange={(e) => setMemoryType(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-white/[0.08] bg-zinc-900 text-xs text-white focus:outline-none"
              >
                <option value="semantic">Semantic Fact</option>
                <option value="preference">User Preference</option>
                <option value="episodic">Episodic Trace</option>
              </select>
            </div>
            <div>
              <label className="text-[10px] font-mono text-slate-400 uppercase tracking-widest block mb-1">Memory Content</label>
              <textarea 
                rows={3}
                placeholder="Type a key learning, preference, or fact to store..."
                value={newMemory}
                onChange={(e) => setNewMemory(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-white/[0.08] bg-zinc-900 text-xs text-white focus:outline-none placeholder-slate-600"
              />
            </div>
            <button 
              onClick={handleAdd}
              className="w-full py-2 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
            >
              <Plus className="w-4 h-4" /> Save Memory
            </button>
          </div>
        </GlassCard>

        {/* Memories List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex gap-2">
            {['all', 'semantic', 'preference', 'episodic'].map((cat) => (
              <button 
                key={cat}
                className="px-3 py-1 rounded-lg border border-white/[0.04] bg-white/[0.01] hover:bg-white/[0.03] text-[10px] font-mono uppercase tracking-wider text-slate-300 transition-colors"
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {memories.map((m) => (
              <GlassCard key={m.id} className="p-5 border-white/[0.04] flex flex-col justify-between space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-mono font-semibold uppercase tracking-wider border ${
                      m.type === 'preference' 
                        ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' 
                        : m.type === 'episodic' 
                        ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' 
                        : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                    }`}>
                      {m.type}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">{m.date}</span>
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed font-sans">{m.content}</p>
                </div>
                <div className="border-t border-white/[0.03] pt-3 flex justify-between items-center text-[10px] font-mono text-slate-500">
                  <span>VECTOR_SIZE: 1536</span>
                  <button className="text-rose-400/80 hover:text-rose-400 transition-colors">FORGET</button>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 2. KNOWLEDGE BASE VIEW
// ==========================================
export const KnowledgeView: React.FC = () => {
  const [documents, setDocuments] = useState([
    { id: '1', title: 'AgentX Architectural Guide.pdf', chunks: 14, size: '2.4 MB', date: 'Just now' },
    { id: '2', title: 'Financial Q4 Report.xlsx', chunks: 45, size: '12.1 MB', date: '2 hours ago' },
    { id: '3', title: 'Developer Guidelines & Security Policy.md', chunks: 8, size: '344 KB', date: '2 days ago' },
  ]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-indigo-400" />
            Knowledge Base (RAG Store)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Ingest static assets, PDFs, or files into vector tables to support semantic context search.
          </p>
        </div>
        <button className="px-4 py-2 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer">
          <Plus className="w-4 h-4" /> Upload Document
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="p-6 space-y-4 lg:col-span-2">
          <h3 className="text-sm font-semibold text-white">Ingested Libraries</h3>
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="flex justify-between items-center p-4 rounded-2xl border border-white/[0.04] bg-white/[0.01] hover:bg-white/[0.02] transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-white">{doc.title}</h4>
                    <p className="text-[10px] text-slate-400 mt-0.5">{doc.size} • {doc.chunks} Semantic Chunks</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-mono text-slate-500 block">{doc.date}</span>
                  <span className="text-[9px] font-mono text-emerald-400 uppercase tracking-widest">INDEXED</span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="p-6 space-y-4 h-fit">
          <h3 className="text-sm font-semibold text-white">Vector Ingestion Metrics</h3>
          <div className="space-y-4">
            <div className="p-4 rounded-xl border border-white/[0.04] bg-white/[0.01]">
              <span className="text-[10px] font-mono text-slate-400 block uppercase">Total Vectors Indexed</span>
              <span className="text-2xl font-bold text-white mt-1 block">4,289</span>
            </div>
            <div className="p-4 rounded-xl border border-white/[0.04] bg-white/[0.01]">
              <span className="text-[10px] font-mono text-slate-400 block uppercase">Vector Storage Database</span>
              <span className="text-xs font-semibold text-emerald-400 mt-1 block">PGVector (PostgreSQL)</span>
            </div>
            <div className="p-4 rounded-xl border border-white/[0.04] bg-white/[0.01]">
              <span className="text-[10px] font-mono text-slate-400 block uppercase">Index Engine Status</span>
              <span className="text-xs font-semibold text-indigo-400 mt-1 block">HNSW Indexing Enabled</span>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

// ==========================================
// 3. AGENTS REGISTRY VIEW
// ==========================================
export const AgentsView: React.FC = () => {
  const agents = [
    { name: 'master_agent', role: 'Ecosystem CEO', status: 'idle', desc: 'Central coordinator. Decomposes goals, routes tasks, and synthesizes output.' },
    { name: 'research_agent', role: 'Web Search & Intelligence', status: 'idle', desc: 'Scrapes web articles, fetches documentation, and gathers online facts.' },
    { name: 'coding_agent', role: 'Software Engineer', status: 'idle', desc: 'Writes, reviews, refactors, and validates source code across languages.' },
    { name: 'travel_agent', role: 'Travel Planner', status: 'idle', desc: 'Builds customized trip itineraries, explores lodging categories, and checks routes.' },
    { name: 'education_agent', role: 'Academic Instructor', status: 'idle', desc: 'Prepares teaching syllabus, sets course structures, and plans training schedules.' },
    { name: 'fitness_agent', role: 'Athletic Trainer', status: 'idle', desc: 'Formulates workout plans, nutritional guidelines, and gym splits.' },
    { name: 'evaluator_agent', role: 'QA & Safety Auditor', status: 'idle', desc: 'Evaluates correctness, fact-checking, and audits safety limits on execution.' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bot className="w-5 h-5 text-indigo-400" />
            Agent Registry & Discoverability
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Registered agents capable of autonomous participation in task pipelines.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <GlassCard key={agent.name} className="p-5 border-white/[0.04] flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xs font-mono font-bold text-white uppercase">{agent.name.replace('_', ' ')}</h3>
                  <p className="text-[10px] text-indigo-400 font-medium mt-0.5">{agent.role}</p>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-slate-900 border border-white/[0.05] text-[9px] font-mono text-slate-400">
                  {agent.status}
                </span>
              </div>
              <p className="text-[11px] text-slate-300 leading-relaxed font-sans">{agent.desc}</p>
            </div>
            <div className="border-t border-white/[0.03] pt-3 flex justify-between items-center text-[10px] font-mono text-slate-500">
              <span>CAPABILITIES: 4</span>
              <span className="text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer uppercase">PROPERTIES</span>
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};

// ==========================================
// 4. TOOLS VIEW
// ==========================================
export const ToolsView: React.FC = () => {
  const [tools, setTools] = useState([
    { id: '1', name: 'Google Search API', type: 'search', active: true, usage: '280 calls today' },
    { id: '2', name: 'Local Shell Exec', type: 'sandbox', active: false, usage: '0 calls today' },
    { id: '3', name: 'RAG Retriever', type: 'database', active: true, usage: '1,450 calls today' },
    { id: '4', name: 'Web Scraper Chrome', type: 'scraping', active: true, usage: '122 calls today' },
  ]);

  const toggleTool = (id: string) => {
    setTools(tools.map(t => t.id === id ? { ...t, active: !t.active } : t));
    toast.success('Tool security permission updated.');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Wrench className="w-5 h-5 text-indigo-400" />
            Secure Tools & Connectors
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Toggle API access or shell interpreter integrations with secure sandboxing policies.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {tools.map((t) => (
          <GlassCard key={t.id} className="p-5 border-white/[0.04] flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-2xl bg-white/[0.02] border border-white/[0.06] flex items-center justify-center text-slate-400">
                <Wrench className="w-4 h-4 text-indigo-400" />
              </div>
              <div>
                <h3 className="text-xs font-bold text-white uppercase">{t.name}</h3>
                <p className="text-[10px] text-slate-400 mt-0.5">{t.usage}</p>
              </div>
            </div>
            <button 
              onClick={() => toggleTool(t.id)}
              className={`p-2 rounded-xl flex items-center justify-center transition-all ${
                t.active 
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/25' 
                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/25'
              }`}
            >
              <Power className="w-4 h-4" />
            </button>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};

// ==========================================
// 5. MARKETPLACE VIEW
// ==========================================
export const MarketplaceView: React.FC = () => {
  const plugins = [
    { name: 'Cybersecurity Guard', provider: 'AgentX Labs', desc: 'Adds high-fidelity penetration testing and vulnerability checks to coding tasks.', price: 'Free' },
    { name: 'Advanced SQL Synthesizer', provider: 'DataCorp', desc: 'Enables complex analytical DB querying and visual chart report generation.', price: '$12/mo' },
    { name: 'GitHub Integration Link', provider: 'Core Devs', desc: 'Allows agents to commit, pull, and review pull requests on user repositories directly.', price: 'Free' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-indigo-400" />
            Capability Marketplace
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Install community plugins, specialized agents, or third-party tool adapters.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {plugins.map((p) => (
          <GlassCard key={p.name} className="p-5 border-white/[0.04] flex flex-col justify-between h-56">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-bold text-white uppercase">{p.name}</h3>
                <span className="text-[10px] font-mono text-emerald-400 font-bold">{p.price}</span>
              </div>
              <p className="text-[10px] text-slate-400">By {p.provider}</p>
              <p className="text-[11px] text-slate-300 leading-relaxed font-sans">{p.desc}</p>
            </div>
            <button 
              onClick={() => toast.success(`Initiated sandbox download for: ${p.name}`)}
              className="w-full py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] hover:bg-indigo-500 hover:text-white text-xs font-semibold transition-all cursor-pointer"
            >
              Install Plug-in
            </button>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};

// ==========================================
// 6. ANALYTICS & MONITORING VIEWS
// ==========================================
export const AnalyticsView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <LineChart className="w-5 h-5 text-indigo-400" />
            Ecosystem Metrics & Analytics
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Detailed resource usage, cost trends, and active agent execution parameters.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <GlassCard className="p-5 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] font-mono text-slate-400 uppercase">Avg CPU Usage</p>
            <h3 className="text-lg font-bold text-white mt-0.5">14.8%</h3>
          </div>
        </GlassCard>
        <GlassCard className="p-5 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] font-mono text-slate-400 uppercase">Latency Average</p>
            <h3 className="text-lg font-bold text-white mt-0.5">420ms</h3>
          </div>
        </GlassCard>
        <GlassCard className="p-5 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Server className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] font-mono text-slate-400 uppercase">DB Connection</p>
            <h3 className="text-lg font-bold text-emerald-400 mt-0.5">ACTIVE</h3>
          </div>
        </GlassCard>
      </div>

      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm font-semibold text-white">System Performance Summary</h3>
        <p className="text-xs text-slate-400">
          AgentX Operating System scheduler resolved 120 goals with a task execution completion rate of 99.4%.
        </p>
      </GlassCard>
    </div>
  );
};

export const MonitoringView: React.FC = () => {
  const [logs, setLogs] = useState([
    { timestamp: '17:34:02', level: 'INFO', message: 'Orchestrator Node [PlanningAgent]: Persisting goal plan success.' },
    { timestamp: '17:34:04', level: 'INFO', message: 'Orchestrator Node [SafetyAgent]: Auditing task parameters.' },
    { timestamp: '17:34:08', level: 'INFO', message: 'Orchestrator Node [Specialized Agent]: Invoking travel_agent reasoning.' },
    { timestamp: '17:34:10', level: 'INFO', message: 'MemoryConsolidator: Saved semantic facts to user twin profile.' },
  ]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400" />
            Observability Logs & Monitoring
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time kernel debug log stream and health signals.
          </p>
        </div>
      </div>

      <GlassCard className="p-6 h-[400px] flex flex-col justify-between">
        <div className="flex items-center gap-2 border-b border-white/[0.05] pb-3 mb-3">
          <Terminal className="w-4 h-4 text-indigo-400 animate-pulse" />
          <span className="text-xs font-mono text-slate-300">syslog://agentx-kernel-stream</span>
        </div>
        <div className="flex-1 overflow-y-auto font-mono text-xs text-slate-400 space-y-2 pr-2">
          {logs.map((l, i) => (
            <div key={i} className="leading-relaxed">
              <span className="text-slate-600">[{l.timestamp}]</span>{' '}
              <span className="text-indigo-400 font-bold">[{l.level}]</span>{' '}
              <span>{l.message}</span>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
};

// ==========================================
// 7. MODELS VIEW
// ==========================================
export const ModelsView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-400" />
            Model Router & Aliasing
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Route reasoning, extraction, and planning workloads to dynamic LLM backends.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <GlassCard className="p-6 space-y-4">
          <h3 className="text-sm font-semibold text-white">Model Provider Connections</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl border border-white/[0.04] bg-white/[0.01] flex justify-between items-center">
              <div>
                <span className="text-xs font-bold text-white">OpenAI</span>
                <span className="text-[10px] text-slate-400 block mt-0.5">GPT-4o, GPT-4o-mini</span>
              </div>
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            </div>
            <div className="p-4 rounded-xl border border-white/[0.04] bg-white/[0.01] flex justify-between items-center">
              <div>
                <span className="text-xs font-bold text-white">Anthropic</span>
                <span className="text-[10px] text-slate-400 block mt-0.5">Claude 3.5 Sonnet</span>
              </div>
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            </div>
            <div className="p-4 rounded-xl border border-white/[0.04] bg-white/[0.01] flex justify-between items-center">
              <div>
                <span className="text-xs font-bold text-white">Google</span>
                <span className="text-[10px] text-slate-400 block mt-0.5">Gemini 1.5 Pro</span>
              </div>
              <span className="w-2.5 h-2.5 rounded-full bg-slate-600" />
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

// ==========================================
// 8. SETTINGS VIEW
// ==========================================
export const SettingsView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Settings className="w-5 h-5 text-indigo-400" />
            System Configuration
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Configure default API routes, database integrations, and cognitive properties.
          </p>
        </div>
      </div>

      <GlassCard className="p-6 space-y-4 max-w-xl">
        <h3 className="text-sm font-semibold text-white">General Parameters</h3>
        <div className="space-y-3">
          <div>
            <label className="text-[10px] font-mono text-slate-400 uppercase tracking-widest block mb-1">Ecosystem Provider Mode</label>
            <select className="w-full px-3 py-2 rounded-xl border border-white/[0.08] bg-zinc-900 text-xs text-white focus:outline-none">
              <option>Hybrid Local / Cloud Gateway (Default)</option>
              <option>Full Offline Local Mode (Ollama)</option>
              <option>Full Cloud Orchestration (OpenAI/Anthropic)</option>
            </select>
          </div>
          <div>
            <label className="text-[10px] font-mono text-slate-400 uppercase tracking-widest block mb-1">Vector Storage Node</label>
            <input type="text" defaultValue="localhost:5432/agentx" className="w-full px-3 py-2 rounded-xl border border-white/[0.08] bg-zinc-900 text-xs text-white focus:outline-none" />
          </div>
          <button 
            onClick={() => toast.success('OS configuration successfully updated.')}
            className="px-4 py-2 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white text-xs font-semibold transition-colors cursor-pointer"
          >
            Apply Config Changes
          </button>
        </div>
      </GlassCard>
    </div>
  );
};

// ==========================================
// 9. PROFILE VIEW
// ==========================================
export const ProfileView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <User className="w-5 h-5 text-indigo-400" />
            Developer Profile & Key Manager
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Manage your API keys, credentials, and digital operator settings.
          </p>
        </div>
      </div>

      <GlassCard className="p-6 space-y-4 max-w-xl">
        <h3 className="text-sm font-semibold text-white">Operator Information</h3>
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center border border-white/[0.08] shadow-inner text-indigo-400 font-mono text-sm font-bold">
            DEV
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white">Developer Admin</h4>
            <p className="text-[10px] font-mono text-emerald-400 mt-0.5">ROLE: SYSTEM_SUPERUSER</p>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};

// ==========================================
// 10. HELP & DOCUMENTATION VIEWS
// ==========================================
export const HelpView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-indigo-400" />
            Support Center
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Need assistance or found a system bug? Browse our operator channels.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <GlassCard className="p-5 space-y-2">
          <h3 className="text-xs font-bold text-white uppercase">OS Troubleshooting Guide</h3>
          <p className="text-[11px] text-slate-300">
            Read common issue solutions regarding database locks, redis retries, and offline LLM setups.
          </p>
        </GlassCard>
        <GlassCard className="p-5 space-y-2">
          <h3 className="text-xs font-bold text-white uppercase">Contact Engineering</h3>
          <p className="text-[11px] text-slate-300">
            Reach out directly to the AgentX Multi-Agent Core Development Team.
          </p>
        </GlassCard>
      </div>
    </div>
  );
};

export const DocumentationView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            Developer Documentation
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Explore API references, custom agent subclasses, and LangGraph routing nodes.
          </p>
        </div>
      </div>

      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm font-semibold text-white">API Reference Summary</h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          The AgentX backend exposes REST resources on `port 8000` including `/goals/` for dynamic DAG lifecycle triggers, `/workflows/` for HITL pause/resume callbacks, and `/auth/` for token issuance.
        </p>
      </GlassCard>
    </div>
  );
};

// ==========================================
// 11. ADMIN VIEW
// ==========================================
export const AdminView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-indigo-400" />
            Kernel Administrator Console
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Core operator diagnostics, Postgres migration status, and system reset utilities.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <GlassCard className="p-5 space-y-4 border-rose-500/10">
          <h3 className="text-xs font-bold text-rose-400 uppercase">Emergency Override</h3>
          <p className="text-[11px] text-slate-300">
            Terminate all executing graph loops and drop active EventBus listener queues.
          </p>
          <button 
            onClick={() => toast.error('Emergency halt triggered. Shutdown complete.')}
            className="px-4 py-2 rounded-xl bg-rose-500 hover:bg-rose-600 text-white text-xs font-semibold transition-colors cursor-pointer"
          >
            Trigger Kernel Halt
          </button>
        </GlassCard>
      </div>
    </div>
  );
};
