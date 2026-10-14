'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Play, RotateCcw, AlertTriangle } from 'lucide-react';
import { GlassCard } from '../ui/glass-card';

interface LogLine {
  text: string;
  type: 'system' | 'supervisor' | 'agent' | 'success' | 'warning';
}

const PRESETS = [
  {
    title: "Market Analysis Loop",
    command: "initialize-agent-workflow --goal 'analyze market trends for solar energy'",
    logs: [
      { text: "sys::kernel: Booting workflow orchestrator loop...", type: "system" },
      { text: "supervisor: Decomposing goal into execution DAG...", type: "supervisor" },
      { text: "planner: Task 1 -> Research Agent (Fetch current energy trends)", type: "system" },
      { text: "planner: Task 2 -> Analyst Agent (Compute CAGR projection model)", type: "system" },
      { text: "orchestrator: Executing task 1 [Research Agent]...", type: "system" },
      { text: "researcher: Querying Tavily Search Engine... Found 24 active vectors.", type: "agent" },
      { text: "researcher: Top trend: Solar efficiency grew 4.2% in EU.", type: "agent" },
      { text: "orchestrator: Task 1 finished. Dispatching task 2 [Analyst Agent]...", type: "system" },
      { text: "analyst: Running modeling script process... Calculated CAGR at 11.4%.", type: "agent" },
      { text: "supervisor: Consolidating subtask outputs...", type: "supervisor" },
      { text: "sys::kernel: SUCCESS. Workflow loop completed in 1.48s.", type: "success" }
    ]
  },
  {
    title: "Self-Healing Code Build",
    command: "run-build --heal --source 'process_logs.py'",
    logs: [
      { text: "sys::kernel: Initializing python linter tool...", type: "system" },
      { text: "supervisor: Triggering code compilation verification...", type: "supervisor" },
      { text: "compiler: SyntaxError at line 24: IndentationError", type: "warning" },
      { text: "orchestrator: Launching self-healing daemon [Coding Agent]...", type: "system" },
      { text: "coder: Rewriting block at line 24-28... Aligning spaces.", type: "agent" },
      { text: "coder: Applying patch changes to database models.", type: "agent" },
      { text: "compiler: Re-running lint checks... OK.", type: "system" },
      { text: "sys::kernel: SUCCESS. Patch successfully committed to production.", type: "success" }
    ]
  }
];

export const InteractiveConsole: React.FC = () => {
  const [selectedPreset, setSelectedPreset] = useState<number | null>(null);
  const [logs, setLogs] = useState<LogLine[]>([
    { text: "AgentX Virtual Console. Choose a preset above to simulate execution.", type: "system" }
  ]);
  const [isRunning, setIsRunning] = useState(false);
  const [inputVal, setInputVal] = useState('');
  const logEndRef = useRef<HTMLDivElement>(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    if (selectedPreset !== null) {
      logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, selectedPreset]);

  const runSimulation = async (presetIndex: number) => {
    if (isRunning) return;
    setIsRunning(true);
    setSelectedPreset(presetIndex);
    setLogs([]);

    const preset = PRESETS[presetIndex];
    setInputVal(preset.command);

    for (let i = 0; i < preset.logs.length; i++) {
      // Simulate real-time streaming delay
      await new Promise((resolve) => setTimeout(resolve, 600));
      setLogs((prev) => [...prev, preset.logs[i] as LogLine]);
    }
    setIsRunning(false);
  };

  const resetConsole = () => {
    setLogs([{ text: "AgentX Virtual Console. Choose a preset above to simulate execution.", type: "system" }]);
    setInputVal('');
    setSelectedPreset(null);
    setIsRunning(false);
  };

  return (
    <div className="w-full max-w-4xl mx-auto py-12 px-6">
      {/* Preset selection header */}
      <div className="flex flex-wrap gap-3 mb-6 justify-center">
        {PRESETS.map((p, idx) => (
          <button
            key={idx}
            onClick={() => runSimulation(idx)}
            disabled={isRunning}
            className={`px-4 py-2 rounded-xl text-xs font-mono border transition-all cursor-pointer ${
              selectedPreset === idx
                ? 'bg-indigo-500/10 border-indigo-500/40 text-indigo-400 font-semibold'
                : 'bg-white/[0.01] border-white/[0.05] text-slate-400 hover:text-white hover:border-white/10'
            }`}
          >
            {p.title}
          </button>
        ))}

        {(selectedPreset !== null || isRunning) && (
          <button
            onClick={resetConsole}
            className="p-2 rounded-xl bg-white/[0.01] border border-white/[0.05] text-slate-400 hover:text-rose-400 hover:border-rose-500/30 transition-all cursor-pointer"
            title="Reset Terminal"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Glassmorphic Terminal Card */}
      <GlassCard hoverGlow={true} className="p-0 border-white/[0.06] overflow-hidden shadow-2xl">
        {/* Terminal Header Bar */}
        <div className="bg-slate-900/40 border-b border-white/[0.05] px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500/70" />
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500/70" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
          </div>
          <span className="text-[10px] font-mono text-slate-500 select-none uppercase tracking-widest">
            AgentX Terminal Simulation
          </span>
          <Terminal className="w-3.5 h-3.5 text-slate-600" />
        </div>

        {/* Log Viewer Port */}
        <div className="h-64 overflow-y-auto bg-slate-950/75 p-6 font-mono text-xs text-slate-300 space-y-2 select-text leading-relaxed">
          {logs.map((line, key) => (
            <div key={key} className="flex items-start gap-2">
              {line.type === 'system' && (
                <span className="text-slate-500">[$]</span>
              )}
              {line.type === 'supervisor' && (
                <span className="text-indigo-400 font-bold">[supervisor]</span>
              )}
              {line.type === 'agent' && (
                <span className="text-purple-400">[agent]</span>
              )}
              {line.type === 'success' && (
                <span className="text-emerald-400 font-semibold">[success]</span>
              )}
              {line.type === 'warning' && (
                <span className="text-amber-500 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> [warn]</span>
              )}
              <span className={
                line.type === 'success' ? 'text-emerald-300' :
                line.type === 'warning' ? 'text-amber-300' : 'text-slate-300'
              }>
                {line.text}
              </span>
            </div>
          ))}
          {/* Simulated blink cursor */}
          {isRunning && (
            <div className="flex items-center gap-1.5 text-indigo-400 animate-pulse">
              <span className="text-indigo-400">&gt;</span>
              <span>Processing kernel operations...</span>
            </div>
          )}
          <div ref={logEndRef} />
        </div>

        {/* Terminal Input Bar */}
        <div className="bg-slate-900/20 border-t border-white/[0.04] p-3 px-4 flex items-center gap-3">
          <span className="text-xs font-mono text-slate-500 select-none">root@agentx-os:~#</span>
          <input
            type="text"
            readOnly
            placeholder="Choose preset above to execute command..."
            value={inputVal}
            className="flex-1 bg-transparent text-xs font-mono text-indigo-400 focus:outline-none placeholder-slate-600"
          />
        </div>
      </GlassCard>
    </div>
  );
};
