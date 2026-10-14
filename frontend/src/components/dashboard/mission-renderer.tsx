'use client';

import React, { useState } from 'react';
import { GlassCard } from '../ui/glass-card';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Compass, 
  BookOpen, 
  Code, 
  FileText, 
  PenTool, 
  Activity, 
  Briefcase, 
  Download, 
  Bookmark, 
  CheckCircle2, 
  MapPin, 
  Sun, 
  DollarSign, 
  Calendar, 
  ExternalLink, 
  Copy, 
  Check, 
  Sparkles, 
  Loader2, 
  Layers, 
  ShieldCheck, 
  ChevronRight,
  Share2,
  Terminal,
  Play
} from 'lucide-react';
import { toast } from 'sonner';

export interface MissionResultPayload {
  mission_id: string;
  title: string;
  description: string;
  category: 'travel' | 'learning' | 'coding' | 'research' | 'writing' | 'fitness' | 'business' | 'finance' | 'general';
  status: string;
  progress_step: string;
  progress_percentage: number;
  deliverable: any;
}

interface MissionRendererProps {
  mission: MissionResultPayload;
}

export const MissionRenderer: React.FC<MissionRendererProps> = ({ mission }) => {
  const [copiedCode, setCopiedCode] = useState(false);
  const [activeCodeFile, setActiveCodeFile] = useState(0);
  const [checkedChecklist, setCheckedChecklist] = useState<Record<number, boolean>>({});

  const isExecuting = mission.status === 'executing' || mission.status === 'running' || mission.status === 'pending';

  // Helper for progress screen
  if (isExecuting) {
    return (
      <GlassCard className="p-10 space-y-6 text-center max-w-2xl mx-auto my-8 border-indigo-500/20 bg-zinc-950/80">
        <div className="flex flex-col items-center space-y-4">
          <div className="relative">
            <div className="w-16 h-16 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-indigo-400 animate-pulse" />
            </div>
          </div>
          <div>
            <span className="text-[10px] font-mono uppercase tracking-widest text-indigo-400 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20">
              MISSION IN PROGRESS
            </span>
            <h3 className="text-xl font-bold text-white mt-3 tracking-tight">{mission.title}</h3>
            <p className="text-xs text-zinc-400 mt-1 max-w-md mx-auto">{mission.description}</p>
          </div>
        </div>

        <div className="space-y-2 pt-4 border-t border-white/[0.05]">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-indigo-300 font-semibold">{mission.progress_step || 'Processing goal...'}</span>
            <span className="text-zinc-400 font-bold">{mission.progress_percentage || 45}%</span>
          </div>
          <div className="w-full h-2 rounded-full bg-zinc-900 overflow-hidden border border-white/[0.05]">
            <motion.div 
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
              initial={{ width: '0%' }}
              animate={{ width: `${mission.progress_percentage || 45}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <p className="text-[10px] text-zinc-500 font-sans mt-2">
            AgentX is processing your request. Finalizing mission deliverable...
          </p>
        </div>
      </GlassCard>
    );
  }

  const deliverable = mission.deliverable || {};
  const category = mission.category || 'general';

  // ----------------------------------------------------
  // 1. TRAVEL DELIVERABLE VIEW
  // ----------------------------------------------------
  if (category === 'travel') {
    return (
      <div className="space-y-6">
        {/* Travel Header Hero Card */}
        <GlassCard className="p-6 md:p-8 space-y-4 border-indigo-500/20 bg-gradient-to-br from-indigo-950/20 via-zinc-950 to-zinc-950">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/[0.06] pb-6">
            <div>
              <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold uppercase tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5 w-fit">
                <Compass className="w-3.5 h-3.5" /> TRAVEL PLANNER DELIVERABLE
              </span>
              <h2 className="text-2xl font-extrabold text-white mt-2.5 tracking-tight">{mission.title}</h2>
              <p className="text-xs text-zinc-300 mt-1 max-w-2xl leading-relaxed">{deliverable.summary}</p>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {(deliverable.actions || ['Download PDF', 'Save Mission']).map((act: string) => (
                <button
                  key={act}
                  onClick={() => toast.success(`${act} initiated.`)}
                  className="px-3.5 py-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs text-white font-medium flex items-center gap-1.5 transition-all cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5 text-indigo-400" /> {act}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
            <div className="p-3.5 rounded-xl border border-white/[0.04] bg-white/[0.01] flex items-center gap-3">
              <Calendar className="w-4 h-4 text-indigo-400" />
              <div>
                <p className="text-[10px] font-mono text-zinc-400 uppercase">Duration</p>
                <p className="text-xs font-bold text-white">{deliverable.duration || '5 Days'}</p>
              </div>
            </div>
            <div className="p-3.5 rounded-xl border border-white/[0.04] bg-white/[0.01] flex items-center gap-3">
              <Sun className="w-4 h-4 text-amber-400" />
              <div>
                <p className="text-[10px] font-mono text-zinc-400 uppercase">Forecast</p>
                <p className="text-xs font-bold text-white">{deliverable.weather || '27°C • Clear'}</p>
              </div>
            </div>
            <div className="p-3.5 rounded-xl border border-white/[0.04] bg-white/[0.01] flex items-center gap-3">
              <DollarSign className="w-4 h-4 text-emerald-400" />
              <div>
                <p className="text-[10px] font-mono text-zinc-400 uppercase">Estimated Budget</p>
                <p className="text-xs font-bold text-white">{deliverable.budget_estimate || '$1,200'}</p>
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Day-by-day Itinerary Accordion / Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <MapPin className="w-4 h-4 text-indigo-400" /> Day-by-Day Itinerary Schedule
            </h3>

            <div className="space-y-3">
              {(deliverable.itinerary || []).map((item: any) => (
                <GlassCard key={item.day} className="p-5 space-y-3 hover:border-indigo-500/30 transition-all">
                  <div className="flex justify-between items-center border-b border-white/[0.04] pb-2.5">
                    <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-md border border-indigo-500/20">
                      DAY {item.day}
                    </span>
                    <span className="text-xs font-semibold text-white">{item.title}</span>
                  </div>
                  
                  <ul className="space-y-2 text-xs text-zinc-300">
                    {item.activities?.map((act: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                        <span>{act}</span>
                      </li>
                    ))}
                  </ul>

                  <div className="grid grid-cols-2 gap-2 pt-2 text-[10px] font-mono text-zinc-400 border-t border-white/[0.03]">
                    <span>STAY: <strong className="text-zinc-200">{item.stay}</strong></span>
                    <span>MEALS: <strong className="text-zinc-200">{item.meals}</strong></span>
                  </div>
                </GlassCard>
              ))}
            </div>
          </div>

          {/* Sidebar Cards (Hotels, Packing, Tips) */}
          <div className="space-y-6">
            <GlassCard className="p-5 space-y-3">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Recommended Stays</h4>
              <div className="space-y-2.5">
                {(deliverable.hotels || []).map((h: any) => (
                  <div key={h.name} className="p-3 rounded-xl border border-white/[0.04] bg-white/[0.01] space-y-1">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-semibold text-white">{h.name}</span>
                      <span className="text-amber-400 font-mono text-[10px]">{h.rating}</span>
                    </div>
                    <p className="text-[10px] text-zinc-400">{h.highlight} • <strong className="text-zinc-200">{h.price}</strong></p>
                  </div>
                ))}
              </div>
            </GlassCard>

            <GlassCard className="p-5 space-y-3">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Packing Checklist</h4>
              <div className="space-y-2">
                {(deliverable.packing_checklist || []).map((item: string, idx: number) => (
                  <label key={idx} className="flex items-center gap-2 text-xs text-zinc-300 cursor-pointer select-none">
                    <input 
                      type="checkbox"
                      checked={!!checkedChecklist[idx]}
                      onChange={(e) => setCheckedChecklist({ ...checkedChecklist, [idx]: e.target.checked })}
                      className="rounded border-zinc-700 bg-zinc-900 text-indigo-500 focus:ring-0"
                    />
                    <span className={checkedChecklist[idx] ? 'line-through text-zinc-500' : ''}>{item}</span>
                  </label>
                ))}
              </div>
            </GlassCard>
          </div>
        </div>
      </div>
    );
  }

  // ----------------------------------------------------
  // 2. LEARNING DELIVERABLE VIEW
  // ----------------------------------------------------
  if (category === 'learning') {
    return (
      <div className="space-y-6">
        <GlassCard className="p-6 md:p-8 space-y-4 border-indigo-500/20 bg-gradient-to-br from-purple-950/20 via-zinc-950 to-zinc-950">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/[0.06] pb-6">
            <div>
              <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold uppercase tracking-widest bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center gap-1.5 w-fit">
                <BookOpen className="w-3.5 h-3.5" /> LEARNING HUB DELIVERABLE
              </span>
              <h2 className="text-2xl font-extrabold text-white mt-2.5 tracking-tight">{mission.title}</h2>
              <p className="text-xs text-zinc-300 mt-1 max-w-2xl leading-relaxed">{deliverable.summary}</p>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {(deliverable.actions || ['Download Guide', 'Bookmark']).map((act: string) => (
                <button
                  key={act}
                  onClick={() => toast.success(`${act} initiated.`)}
                  className="px-3.5 py-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs text-white font-medium flex items-center gap-1.5 transition-all cursor-pointer"
                >
                  <Bookmark className="w-3.5 h-3.5 text-purple-400" /> {act}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(deliverable.roadmap || []).map((phase: any) => (
              <GlassCard key={phase.phase} className="p-4 space-y-2 border-white/[0.04]">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold text-white">{phase.phase}</span>
                  <span className="text-[10px] font-mono text-purple-400 px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20">
                    {phase.duration}
                  </span>
                </div>
                <ul className="space-y-1 text-xs text-zinc-400">
                  {phase.topics?.map((t: string, i: number) => (
                    <li key={i} className="flex items-center gap-1.5">
                      <ChevronRight className="w-3 h-3 text-purple-400" /> {t}
                    </li>
                  ))}
                </ul>
              </GlassCard>
            ))}
          </div>
        </GlassCard>

        {/* Practice Schedule & Resources */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <GlassCard className="p-5 space-y-3">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">Weekly Practice Schedule</h4>
            <div className="space-y-2">
              {(deliverable.practice_schedule || []).map((s: any, idx: number) => (
                <div key={idx} className="p-3 rounded-xl border border-white/[0.04] bg-white/[0.01] flex justify-between items-center text-xs">
                  <span className="font-mono text-purple-400">{s.day}</span>
                  <span className="text-zinc-200 font-medium">{s.focus}</span>
                </div>
              ))}
            </div>
          </GlassCard>

          <GlassCard className="p-5 space-y-3">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">Milestones & Achievements</h4>
            <div className="space-y-2">
              {(deliverable.achievements || []).map((ach: string, idx: number) => (
                <div key={idx} className="p-3 rounded-xl border border-emerald-500/10 bg-emerald-500/[0.01] flex items-center gap-2 text-xs text-emerald-300 font-semibold">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> {ach}
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>
    );
  }

  // ----------------------------------------------------
  // 3. CODING WORKSPACE DELIVERABLE VIEW
  // ----------------------------------------------------
  if (category === 'coding') {
    const files = deliverable.files || [];
    const currentFile = files[activeCodeFile] || files[0] || { filename: 'main.ts', code: '// No code generated' };

    return (
      <div className="space-y-6">
        <GlassCard className="p-6 md:p-8 space-y-4 border-indigo-500/20 bg-zinc-950">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/[0.06] pb-6">
            <div>
              <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold uppercase tracking-widest bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center gap-1.5 w-fit">
                <Code className="w-3.5 h-3.5" /> PROJECT WORKSPACE DELIVERABLE
              </span>
              <h2 className="text-2xl font-extrabold text-white mt-2.5 tracking-tight">{mission.title}</h2>
              <p className="text-xs text-zinc-300 mt-1 max-w-2xl leading-relaxed">{deliverable.summary}</p>
            </div>

            <div className="flex flex-wrap gap-2">
              {(deliverable.actions || ['Download Project ZIP', 'Deploy']).map((act: string) => (
                <button
                  key={act}
                  onClick={() => toast.success(`${act} initiated.`)}
                  className="px-3.5 py-2 rounded-xl bg-blue-500 hover:bg-blue-600 text-xs text-white font-semibold flex items-center gap-1.5 transition-all cursor-pointer shadow-lg shadow-blue-500/20"
                >
                  <Download className="w-3.5 h-3.5" /> {act}
                </button>
              ))}
            </div>
          </div>

          {/* Interactive Code Explorer */}
          <div className="rounded-2xl border border-white/[0.08] bg-zinc-950 overflow-hidden space-y-0">
            {/* File Tabs */}
            <div className="flex items-center justify-between border-b border-white/[0.08] bg-zinc-900/60 px-4 py-2 overflow-x-auto">
              <div className="flex items-center gap-1">
                {files.map((f: any, idx: number) => (
                  <button
                    key={f.filename}
                    onClick={() => setActiveCodeFile(idx)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono flex items-center gap-2 transition-all cursor-pointer ${
                      activeCodeFile === idx
                        ? 'bg-blue-500/20 border border-blue-500/30 text-blue-300 font-bold'
                        : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.03]'
                    }`}
                  >
                    <Terminal className="w-3.5 h-3.5" /> {f.filename}
                  </button>
                ))}
              </div>

              <button
                onClick={() => {
                  navigator.clipboard.writeText(currentFile.code);
                  setCopiedCode(true);
                  toast.success('Code copied to clipboard!');
                  setTimeout(() => setCopiedCode(false), 2000);
                }}
                className="p-1.5 text-xs text-zinc-400 hover:text-white flex items-center gap-1 transition-colors cursor-pointer"
              >
                {copiedCode ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>

            {/* Code Box */}
            <pre className="p-4 text-xs font-mono text-zinc-300 leading-relaxed overflow-x-auto bg-zinc-950 max-h-[380px]">
              <code>{currentFile.code}</code>
            </pre>
          </div>
        </GlassCard>

        {/* Deployment Steps */}
        <GlassCard className="p-6 space-y-3">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider">Deployment & Setup Instructions</h4>
          <div className="space-y-2">
            {(deliverable.deployment_guide || []).map((step: string, idx: number) => (
              <div key={idx} className="p-3 rounded-xl border border-white/[0.04] bg-white/[0.01] text-xs text-zinc-300 font-mono">
                {step}
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    );
  }

  // ----------------------------------------------------
  // 4. RESEARCH / WRITING / GENERAL DELIVERABLE VIEW
  // ----------------------------------------------------
  return (
    <div className="space-y-6">
      <GlassCard className="p-6 md:p-8 space-y-4 border-indigo-500/20 bg-zinc-950">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/[0.06] pb-6">
          <div>
            <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold uppercase tracking-widest bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center gap-1.5 w-fit">
              <FileText className="w-3.5 h-3.5" /> MISSION DELIVERABLE
            </span>
            <h2 className="text-2xl font-extrabold text-white mt-2.5 tracking-tight">{mission.title}</h2>
            <p className="text-xs text-zinc-300 mt-1 max-w-2xl leading-relaxed">{deliverable.summary}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            {(deliverable.actions || ['Save Mission', 'Export PDF']).map((act: string) => (
              <button
                key={act}
                onClick={() => toast.success(`${act} initiated.`)}
                className="px-3.5 py-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs text-white font-medium flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <Download className="w-3.5 h-3.5 text-indigo-400" /> {act}
              </button>
            ))}
          </div>
        </div>

        {/* Content workspace */}
        <div className="p-6 rounded-2xl border border-white/[0.04] bg-zinc-900/40 text-xs text-zinc-200 leading-relaxed font-sans whitespace-pre-wrap">
          {deliverable.full_content || deliverable.report_body || deliverable.content || deliverable.summary || 'Mission output generated successfully.'}
        </div>
      </GlassCard>
    </div>
  );
};
