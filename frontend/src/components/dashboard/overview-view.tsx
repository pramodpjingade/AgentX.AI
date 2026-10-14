import React from 'react';
import { GlassCard } from '../ui/glass-card';
import { motion } from 'framer-motion';
import { 
  ShieldAlert, 
  GitFork, 
  Coins, 
  Network,
  CheckCircle,
  Database,
  Cpu
} from 'lucide-react';

export const OverviewView: React.FC = () => {
  const stats = [
    { label: 'Active Workflows', value: '3 Run Loops', icon: GitFork, color: 'text-indigo-400', glow: 'bg-indigo-500/10' },
    { label: 'Pending approvals', value: '2 Actions', icon: ShieldAlert, color: 'text-amber-400', glow: 'bg-amber-500/10' },
    { label: 'Accrued cost', value: '$0.001217', icon: Coins, color: 'text-emerald-400', glow: 'bg-emerald-500/10' },
    { label: 'Agent instances', value: '9 Online', icon: Network, color: 'text-purple-400', glow: 'bg-purple-500/10' },
  ];

  return (
    <div className="space-y-6">
      {/* Hero Welcome banner with Wireframe overlay */}
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative overflow-hidden rounded-3xl border border-white/[0.06] bg-slate-950/80 p-8 flex flex-col md:flex-row justify-between items-center shadow-[0_0_50px_rgba(99,102,241,0.05)]"
      >
        {/* Glowing aura effect */}
        <div className="absolute right-0 top-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-[80px]" />
        
        {/* Circuit board vector graphic overlay */}
        <svg className="absolute right-0 top-0 w-1/2 h-full opacity-15 text-indigo-400 pointer-events-none mix-blend-screen hidden md:block" viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="0.5">
          <path d="M10 20 H50 L60 30 H90" />
          <path d="M20 40 H70 L80 50 H95" />
          <path d="M40 70 H60 L70 80 H90" />
          <circle cx="90" cy="30" r="1" fill="currentColor" />
          <circle cx="95" cy="50" r="1" fill="currentColor" />
          <circle cx="90" cy="80" r="1" fill="currentColor" />
        </svg>

        <div className="relative z-10 space-y-4 max-w-xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/25 bg-indigo-500/5 text-xs text-indigo-300 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-ping" />
            AGENTX OS KERNEL V5.0
          </div>
          <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-white leading-tight">
            Autonomous multi-agent orchestration <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-500">fully active</span>
          </h2>
          <p className="text-slate-400 text-sm leading-relaxed">
            Ecosystem tasks routing, safety audits, and human authorization checks are initialized. Real-time NATS events pub/sub connected via database brokers.
          </p>
        </div>
      </motion.div>

      {/* Grid Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <GlassCard key={i} className="p-6 relative group" animate={true}>
              <div className="absolute top-4 right-4 w-10 h-10 rounded-xl flex items-center justify-center border border-white/[0.04] bg-white/[0.02]">
                <Icon className={`w-5 h-5 ${stat.color}`} />
              </div>
              <p className="text-xs text-slate-400 font-medium">{stat.label}</p>
              <h3 className="text-xl font-semibold text-white mt-2 tracking-tight group-hover:glow-text">
                {stat.value}
              </h3>
            </GlassCard>
          );
        })}
      </div>

      {/* System diagnostics row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="p-6 lg:col-span-2 space-y-4" hoverGlow={false}>
          <div className="flex items-center justify-between border-b border-white/[0.05] pb-4">
            <h3 className="text-sm font-semibold text-white">Active Core Services</h3>
            <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest">DIAGNOSTICS</span>
          </div>

          <div className="space-y-3">
            {[
              { name: 'FastAPI REST Gateway', status: 'healthy', detail: 'Port 8000 online' },
              { name: 'Zustand Memory Engine', status: 'healthy', detail: 'Local state synced' },
              { name: 'Model manager Router', status: 'healthy', detail: 'Mock fallback provider' },
              { name: 'Event dispatcher worker', status: 'healthy', detail: 'In-memory queue loop' },
            ].map((service, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl border border-white/[0.03] bg-white/[0.01]">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/5 border border-indigo-500/10 flex items-center justify-center">
                    <Cpu className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-white">{service.name}</h4>
                    <p className="text-[10px] text-slate-500">{service.detail}</p>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-emerald-400">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>online</span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* DB Connection info card */}
        <GlassCard className="p-6 flex flex-col justify-between" hoverGlow={true}>
          <div className="space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/5 border border-indigo-500/10 flex items-center justify-center">
              <Database className="w-6 h-6 text-indigo-400" />
            </div>
            <h3 className="text-sm font-semibold text-white">Relational Engine</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              FastAPI is currently running SQLite database operations locally for telemetry, capability tracking, and HITL authorization records.
            </p>
          </div>
          <div className="pt-4 border-t border-white/[0.05] mt-4 flex items-center justify-between text-[10px] font-mono text-slate-400">
            <span>DRIVER TYPE: SQLITE</span>
            <span className="text-emerald-400">CONNECTED</span>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
