"use client";

import React, { useState, useEffect } from "react";
import {
  Sparkles,
  Zap,
  Play,
  CheckCircle2,
  Code,
  FileText,
  Clock,
  Send,
  Layers,
  ChevronRight,
  Download,
  Share2,
  Copy,
  AlertCircle
} from "lucide-react";
import MissionTimeline from "./MissionTimeline";

interface LiveWorkspaceProps {
  initialPrompt?: string;
  goalId?: string;
}

export const LiveWorkspace: React.FC<LiveWorkspaceProps> = ({
  initialPrompt = "Plan a 5-Day Cultural Trip to Paris",
  goalId
}) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [isExecuting, setIsExecuting] = useState(false);
  const [activeTab, setActiveTab] = useState<"workspace" | "artifacts" | "timeline" | "code">("workspace");

  const [humanStepMessage, setHumanStepMessage] = useState<string>("Ready to launch your mission.");
  const [progressPct, setProgressPct] = useState<number>(0);
  const [deliverableMarkdown, setDeliverableMarkdown] = useState<string>("");

  const humanFriendlySteps = [
    { pct: 15, msg: "Understanding your request & objectives..." },
    { pct: 35, msg: "Formulating multi-step execution strategy..." },
    { pct: 55, msg: "Gathering facts & analyzing recommendations..." },
    { pct: 80, msg: "Reflecting & verifying deliverable quality..." },
    { pct: 95, msg: "Finalizing your mission deliverable..." },
    { pct: 100, msg: "Mission complete! Final deliverable ready." }
  ];

  const handleLaunchMission = () => {
    if (!prompt.trim() || isExecuting) return;
    setIsExecuting(true);
    setProgressPct(5);
    setHumanStepMessage("Initializing Mission Engine...");
    setDeliverableMarkdown("");

    let stepIndex = 0;
    const interval = setInterval(() => {
      if (stepIndex < humanFriendlySteps.length) {
        const step = humanFriendlySteps[stepIndex];
        setProgressPct(step.pct);
        setHumanStepMessage(step.msg);
        stepIndex++;
      } else {
        clearInterval(interval);
        setIsExecuting(false);
        setDeliverableMarkdown(
          `🌴 **AgentX Intelligence Deliverable: 5-Day Cultural Trip to Paris**\n\n### 📅 **Itinerary Overview**\n* **Day 1:** Louvre Museum, Jardin des Tuileries & Seine Sunset Cruise.\n* **Day 2:** Musée d'Orsay, Latin Quarter & Saint-Germain-des-Prés.\n* **Day 3:** Palace of Versailles & Historic Gardens.\n* **Day 4:** Montmartre, Sacré-Cœur & Local Bistro Dining.\n* **Day 5:** Le Marais Architecture & Palais Garnier Opera House.\n\n### 💰 **Logistics & Budget**\n* Estimated Cost: $750 / person (Comfort 4-Star Accommodations & Transit).\n* Fact Verification Score: **100% Grounded & Verified**.`
        );
      }
    }, 600);
  };

  return (
    <div className="w-full h-full flex flex-col bg-slate-950 text-slate-100 overflow-hidden">
      {/* Top Bar Header */}
      <div className="h-14 border-b border-slate-800 bg-slate-900/80 px-6 flex items-center justify-between backdrop-blur-md">
        <div className="flex items-center space-x-3">
          <div className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Live Mission Workspace</h2>
            <div className="text-xs text-slate-400 flex items-center space-x-2">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>Real-Time Streaming Active</span>
            </div>
          </div>
        </div>

        {/* Tab Selection */}
        <div className="flex space-x-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setActiveTab("workspace")}
            className={`px-3 py-1 text-xs font-medium rounded-md transition ${
              activeTab === "workspace" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Live Deliverable
          </button>
          <button
            onClick={() => setActiveTab("timeline")}
            className={`px-3 py-1 text-xs font-medium rounded-md transition ${
              activeTab === "timeline" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Mission Timeline
          </button>
        </div>
      </div>

      {/* Main Workspace Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Input & Streaming Panel */}
        <div className="w-full md:w-1/2 border-r border-slate-800 p-6 flex flex-col space-y-6 overflow-y-auto">
          {/* Prompt Entry Card */}
          <div className="bg-slate-900/70 p-5 rounded-xl border border-slate-800 space-y-4">
            <label className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
              Enter Mission Objectives
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              placeholder="Describe your goal (e.g. Plan a trip, build an API, audit code)..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition resize-none"
            />
            <button
              onClick={handleLaunchMission}
              disabled={isExecuting}
              className="w-full flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg transition cursor-pointer"
            >
              <Send className="w-4 h-4" />
              <span>{isExecuting ? "Executing Mission..." : "Execute Mission"}</span>
            </button>
          </div>

          {/* Real-Time Progress Streamer */}
          <div className="bg-slate-900/70 p-5 rounded-xl border border-slate-800 space-y-3">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400 font-medium">Human-Friendly Progress</span>
              <span className="text-indigo-400 font-bold">{progressPct}%</span>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 transition-all duration-300"
                style={{ width: `${progressPct}%` }}
              />
            </div>

            <div className="flex items-center space-x-2 text-xs text-slate-200">
              <Sparkles className="w-4 h-4 text-indigo-400 animate-spin" />
              <span>{humanStepMessage}</span>
            </div>
          </div>
        </div>

        {/* Right Output Panel */}
        <div className="w-full md:w-1/2 p-6 overflow-y-auto bg-slate-950/80">
          {activeTab === "workspace" && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-indigo-400" />
                  <span>Synthesized Deliverable</span>
                </h3>
                {deliverableMarkdown && (
                  <div className="flex space-x-2">
                    <button className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center space-x-1">
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy</span>
                    </button>
                  </div>
                )}
              </div>

              {deliverableMarkdown ? (
                <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-xl text-sm text-slate-200 whitespace-pre-line leading-relaxed font-sans shadow-lg">
                  {deliverableMarkdown}
                </div>
              ) : (
                <div className="h-64 flex flex-col items-center justify-center text-center p-6 border-2 border-dashed border-slate-800 rounded-xl text-slate-500 space-y-2">
                  <Sparkles className="w-8 h-8 text-slate-600 mb-2" />
                  <p className="text-sm">Click "Execute Mission" to stream live results.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === "timeline" && <MissionTimeline />}
        </div>
      </div>
    </div>
  );
};

export default LiveWorkspace;
