"use client";

import React from "react";
import { CheckCircle2, Clock, Play, Sparkles, AlertCircle, FileText, Download } from "lucide-react";

export const MissionTimeline: React.FC = () => {
  const steps = [
    { title: "Mission Initialized", status: "completed", time: "0.0s", detail: "Loaded user memory & digital twin profile." },
    { title: "Supervisor Intent Analysis", status: "completed", time: "0.4s", detail: "Classified goal category: Travel & Culture." },
    { title: "DAG Task Decomposition", status: "completed", time: "0.8s", detail: "Planner Agent generated 4 subtask dependencies." },
    { title: "Dynamic Capability Routing", status: "completed", time: "1.2s", detail: "Router Agent selected specialized AI domain agents." },
    { title: "Parallel Agent Execution", status: "completed", time: "2.1s", detail: "Executed Research, Travel, Verification, Governance simultaneously." },
    { title: "Quality Audit & Self-Reflection", status: "completed", time: "2.6s", detail: "Critic Engine verified fact grounding score: 100%." },
    { title: "Executive Master Synthesis", status: "completed", time: "3.1s", detail: "Persisted MissionResult and generated deliverable." }
  ];

  return (
    <div className="w-full space-y-4">
      <h3 className="text-sm font-bold text-white flex items-center space-x-2">
        <Clock className="w-4 h-4 text-indigo-400" />
        <span>Live Mission Execution Timeline</span>
      </h3>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
        {steps.map((s, idx) => (
          <div key={idx} className="relative flex items-start space-x-3">
            <div className="absolute -left-6 top-0.5 p-0.5 rounded-full bg-slate-950 border border-emerald-500/50 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-3.5 rounded-xl w-full">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold text-slate-100">{s.title}</span>
                <span className="text-slate-400 font-mono">{s.time}</span>
              </div>
              <p className="text-xs text-slate-400 mt-1">{s.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MissionTimeline;
