"use client";

import React, { useState } from "react";
import {
  Sparkles,
  Zap,
  Play,
  Bookmark,
  TrendingUp,
  Clock,
  CheckCircle2,
  Cpu,
  Layers,
  ArrowRight,
  PlusCircle,
  FolderOpen
} from "lucide-react";

interface MissionCenterProps {
  onStartMission?: (prompt: string) => void;
  onSelectMission?: (missionId: string) => void;
}

export const MissionCenter: React.FC<MissionCenterProps> = ({
  onStartMission,
  onSelectMission
}) => {
  const [activeTab, setActiveTab] = useState<"overview" | "templates" | "insights">("overview");

  const templates = [
    {
      title: "5-Day Travel & Culture Itinerary",
      description: "Decompose destination research, transport costs, attractions, and day-by-day routing.",
      category: "Travel",
      prompt: "Plan a 5-Day Cultural Trip to Paris focusing on historical landmarks, local cuisine, and budget recommendations."
    },
    {
      title: "Full-Stack FastAPI Microservice",
      description: "Generate asynchronous API routes, Pydantic schemas, unit tests, and Docker deployment.",
      category: "Engineering",
      prompt: "Build an asynchronous Python FastAPI REST application for user authentication with JWT, PostgreSQL, and unit tests."
    },
    {
      title: "Enterprise Cybersecurity Audit",
      description: "Scan system configurations, evaluate zero-trust policies, and generate compliance reports.",
      category: "Security",
      prompt: "Conduct an enterprise security audit for a cloud-native microservice architecture, identifying PII risks and RBAC vulnerabilities."
    },
    {
      title: "Competitor Market Intelligence",
      description: "Gather web pricing data, feature comparisons, and executive strategic summaries.",
      category: "Business",
      prompt: "Perform a competitive analysis of top AI productivity platforms, comparing pricing models, feature matrices, and target market segments."
    }
  ];

  const recentMissions = [
    { id: "m-101", title: "Plan a 5-Day Cultural Trip to Paris", status: "COMPLETED", duration: "3s", category: "travel", time: "10 mins ago" },
    { id: "m-102", title: "FastAPI REST Application Deployment", status: "COMPLETED", duration: "4s", category: "coding", time: "1 hour ago" },
    { id: "m-103", title: "Basketball Training & Athletic Syllabus", status: "COMPLETED", duration: "2s", category: "education", time: "3 hours ago" }
  ];

  return (
    <div className="w-full h-full flex flex-col bg-slate-950 text-slate-100 overflow-y-auto p-6 space-y-6">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-900/60 via-purple-900/40 to-slate-900 border border-indigo-500/20 p-8 backdrop-blur-xl shadow-2xl">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 font-semibold text-xs tracking-widest uppercase mb-2">
              <Sparkles className="w-4 h-4 text-indigo-400 animate-pulse" />
              <span>AgentX OS — Mission Intelligence Center</span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Collaborate with your living AI Operating System.
            </h1>
            <p className="mt-2 text-slate-300 text-sm max-w-2xl">
              Autonomous multi-agent execution, hybrid vector knowledge retrieval, self-reflection, and real-time streaming.
            </p>
          </div>

          <button
            onClick={() => onStartMission && onStartMission("Plan a 5-Day Cultural Trip to Paris")}
            className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-3 rounded-xl shadow-lg hover:shadow-indigo-500/25 transition duration-200 cursor-pointer"
          >
            <PlusCircle className="w-5 h-5" />
            <span>Launch New Mission</span>
          </button>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8 pt-6 border-t border-slate-800/80">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-bold text-white">100%</div>
              <div className="text-xs text-slate-400">Execution Reliability</div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-bold text-white">3.1s</div>
              <div className="text-xs text-slate-400">Average Latency</div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-bold text-white">14 Agents</div>
              <div className="text-xs text-slate-400">Active Multi-Agent Swarm</div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-bold text-white">7 Engines</div>
              <div className="text-xs text-slate-400">Core AI Architecture</div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab("overview")}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition ${
            activeTab === "overview" ? "bg-slate-800 text-indigo-400 border border-indigo-500/30" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Recent & Active Missions
        </button>
        <button
          onClick={() => setActiveTab("templates")}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition ${
            activeTab === "templates" ? "bg-slate-800 text-indigo-400 border border-indigo-500/30" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Mission Templates
        </button>
        <button
          onClick={() => setActiveTab("insights")}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition ${
            activeTab === "insights" ? "bg-slate-800 text-indigo-400 border border-indigo-500/30" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Daily AI Insights
        </button>
      </div>

      {/* Overview Section */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Missions List */}
          <div className="lg:col-span-2 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center space-x-2">
              <Clock className="w-5 h-5 text-indigo-400" />
              <span>Recent Mission Executions</span>
            </h3>

            <div className="space-y-3">
              {recentMissions.map((m) => (
                <div
                  key={m.id}
                  onClick={() => onSelectMission && onSelectMission(m.id)}
                  className="group flex items-center justify-between p-4 bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-indigo-500/40 rounded-xl transition duration-150 cursor-pointer"
                >
                  <div className="flex items-center space-x-4">
                    <div className="p-3 rounded-lg bg-slate-800 group-hover:bg-indigo-500/20 text-indigo-400 transition">
                      <Bookmark className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-slate-100 group-hover:text-indigo-300 transition">
                        {m.title}
                      </h4>
                      <div className="flex items-center space-x-3 mt-1 text-xs text-slate-400">
                        <span className="uppercase tracking-wider font-mono text-indigo-400/90">{m.category}</span>
                        <span>•</span>
                        <span>Duration: {m.duration}</span>
                        <span>•</span>
                        <span>{m.time}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {m.status}
                    </span>
                    <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-1 transition" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Recommendation Sidebar */}
          <div className="p-5 bg-slate-900/70 rounded-xl border border-slate-800 space-y-4">
            <h3 className="text-md font-bold text-white flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-indigo-400" />
              <span>Recommended Next Actions</span>
            </h3>

            <p className="text-xs text-slate-400">
              Based on your recent digital twin profile and workspace activity, AgentX suggests:
            </p>

            <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50 space-y-2">
              <div className="text-xs font-semibold text-indigo-300">✈️ Travel Optimization</div>
              <div className="text-xs text-slate-300">Generate budget transport breakdown for Paris cultural tour.</div>
              <button
                onClick={() => onStartMission && onStartMission("Generate budget transport breakdown for Paris cultural tour.")}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center space-x-1"
              >
                <span>Run suggestion</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>

            <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50 space-y-2">
              <div className="text-xs font-semibold text-emerald-300">⚡ Code Generation</div>
              <div className="text-xs text-slate-300">Build FastAPI REST endpoints for JWT auth with PostgreSQL.</div>
              <button
                onClick={() => onStartMission && onStartMission("Build FastAPI REST endpoints for JWT auth with PostgreSQL.")}
                className="text-xs text-emerald-400 hover:text-emerald-300 font-medium flex items-center space-x-1"
              >
                <span>Run suggestion</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === "templates" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {templates.map((tpl, i) => (
            <div
              key={i}
              className="p-5 bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-indigo-500/40 rounded-xl transition duration-150 flex flex-col justify-between"
            >
              <div>
                <div className="flex justify-between items-start mb-2">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    {tpl.category}
                  </span>
                </div>
                <h4 className="text-md font-bold text-white mb-2">{tpl.title}</h4>
                <p className="text-xs text-slate-400 mb-4">{tpl.description}</p>
              </div>

              <button
                onClick={() => onStartMission && onStartMission(tpl.prompt)}
                className="w-full flex items-center justify-center space-x-2 bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs font-medium py-2.5 rounded-lg transition"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Launch Template</span>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Daily Insights Tab */}
      {activeTab === "insights" && (
        <div className="p-6 bg-slate-900/60 rounded-xl border border-slate-800 space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            <span>AgentX Executive AI Insights</span>
          </h3>
          <p className="text-sm text-slate-300 leading-relaxed">
            All 7 core AI engines (Mission Execution, Multi-Agent Swarm, Tool Gateway, Cognitive Memory, Multi-Model Router, Autonomous Reasoning, and Enterprise Knowledge Platform) are operating with 100% health and zero latency bottlenecks.
          </p>
        </div>
      )}
    </div>
  );
};

export default MissionCenter;
