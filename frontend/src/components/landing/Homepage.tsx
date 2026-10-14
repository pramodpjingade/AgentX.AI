'use client';

import React, { useState } from 'react';
import { 
  motion, 
  AnimatePresence, 
  Variants 
} from 'framer-motion';
import { 
  Cpu, 
  Layers, 
  Sparkles, 
  ShieldCheck, 
  Check, 
  ChevronDown, 
  Zap, 
  Database, 
  Search, 
  Activity,
  Code2
} from 'lucide-react';
import { Hero } from './Hero';
import { Navbar } from './Navbar';
import { CommandDrawer } from './CommandDrawer';
import { InteractiveConsole } from './InteractiveConsole';
import { GlassCard } from '../ui/glass-card';

interface HomepageProps {
  onAuthClick: (mode: 'login' | 'signup') => void;
  isAuthenticated: boolean | null;
  onDashboardClick: () => void;
}

export const Homepage: React.FC<HomepageProps> = ({
  onAuthClick,
  isAuthenticated,
  onDashboardClick
}) => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(null);

  // Scroll reveal container settings
  const scrollReveal: Variants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] } }
  };

  const partners = ["Anthropic", "OpenAI", "Vercel", "HuggingFace", "Scale AI", "Mistral"];

  const features = [
    {
      icon: Cpu,
      title: "Asynchronous Event Bus",
      desc: "An in-memory and Redis-ready message broker driving high-concurrency inter-agent communication loops without blocking execution."
    },
    {
      icon: Layers,
      title: "LangGraph State Machine",
      desc: "Structured, cyclic state machines compiling workflow goals into dynamic DAG subtasks with self-healing auto-recovery routes."
    },
    {
      icon: ShieldCheck,
      title: "Human-in-the-Loop Gateways",
      desc: "Administrative approval walls gating sensitive tool actions. Operators can approve or reject agent requests in real-time from any device."
    }
  ];

  const agents = [
    {
      name: "Research Agent",
      role: "Information Aggregation",
      capabilities: ["Web Search Scrapers", "Semantic Synthesizer", "PDF Data Extraction"]
    },
    {
      name: "Coding Agent",
      role: "Source Compilation & Repair",
      capabilities: ["Python Code Sandbox", "Lint Fix Checker", "Self-Healing Rewrites"]
    },
    {
      name: "Analyst Agent",
      role: "Mathematical & projection models",
      capabilities: ["SQL Database Querying", "CSV Trend Plotting", "CAGR Financial Modeling"]
    }
  ];

  const pricingPlans = [
    {
      name: "Developer",
      price: "$0",
      desc: "Perfect for local evaluation and micro-agent loop modeling.",
      features: [
        "In-Memory Event Bus connection",
        "SQLite Local Database storage",
        "Up to 3 Agent DAG nodes per goal",
        "Community Slack Support"
      ],
      cta: "Initialize Free Loop",
      action: () => onAuthClick('signup')
    },
    {
      name: "Scale Operator",
      price: "$49",
      period: "/mo",
      desc: "For production loops and high-frequency agent orchestrations.",
      features: [
        "Redis Distributed Broker integration",
        "Full Postgres Schema adapter",
        "Unlimited Agent DAG levels",
        "Human-in-the-Loop Webhook approvals",
        "Prometheus & OpenTelemetry metrics",
        "Email & Discord Priority Support"
      ],
      cta: "Try Scale Free",
      featured: true,
      action: () => onAuthClick('signup')
    },
    {
      name: "Enterprise OS",
      price: "Custom",
      desc: "Dedicated instances and custom LLM router control grids.",
      features: [
        "SLA guaranteed execution loops",
        "On-premise airgapped deployments",
        "Custom Fine-tuned Router models",
        "Active directory & IAM integrations",
        "24/7 dedicated system engineer"
      ],
      cta: "Contact Operations",
      action: () => {}
    }
  ];

  const faqs = [
    {
      q: "What models does the ModelManager support?",
      a: "AgentX's ModelManager includes default routing configurations for OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet), Google (Gemini 1.5 Pro), and Local Ollama instances. If API keys are missing, the system automatically redirects requests to local mock responses to safeguard operation continuity."
    },
    {
      q: "How does the Self-Healing code mechanism work?",
      a: "When the Coding Agent executes a code compilation that triggers syntax or indentation failures, the loop routes the exception code block back into the Planning graph. The planner analyzes the compiler traceback logs, devises a corrective patch, and rewrites the block in real-time."
    },
    {
      q: "Can I self-host AgentX locally?",
      a: "Yes! AgentX is pre-configured to build on SQLite out of the box, allowing you to run all orchestrators, WebSocket controllers, and agent workers locally without setting up postgres or redis clusters."
    }
  ];

  return (
    <div className="min-h-screen bg-zinc-950 text-white relative font-sans">
      {/* Global Navigation and Command Menu Drawer */}
      <Navbar 
        onMenuToggle={() => setIsDrawerOpen(!isDrawerOpen)} 
        isMenuOpen={isDrawerOpen}
        onAuthClick={onAuthClick}
        isAuthenticated={isAuthenticated}
        onDashboardClick={onDashboardClick}
      />
      
      <CommandDrawer 
        isOpen={isDrawerOpen} 
        onClose={() => setIsDrawerOpen(false)}
        onNavigate={onDashboardClick}
        onAuthClick={onAuthClick}
        isAuthenticated={isAuthenticated}
      />

      {/* 1. Hero Viewport */}
      <section id="hero">
        <Hero />
      </section>

      {/* 2. Trusted By Scrolling Banner */}
      <section className="py-12 border-y border-white/[0.04] bg-zinc-950/40 relative z-10 overflow-hidden">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-6">Trusted by core teams at</p>
          <div className="flex flex-wrap items-center justify-center gap-8 md:gap-16 opacity-40">
            {partners.map((partner, key) => (
              <span key={key} className="text-sm font-mono font-bold tracking-wider hover:opacity-100 hover:text-indigo-400 transition-all select-none">
                {partner}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* 3. What is AgentX Feature Grid */}
      <section className="py-24 max-w-5xl mx-auto px-6 relative z-10">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={scrollReveal}
          className="text-center max-w-2xl mx-auto mb-16"
        >
          <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest">Platform Paradigm</span>
          <h2 className="text-3xl md:text-4xl font-extrabold mt-2 tracking-tight">
            An Autonomous Operating System for AI
          </h2>
          <p className="text-sm text-slate-400 mt-4 leading-relaxed">
            Move past basic chat interfaces. AgentX is a multi-process environment designed to coordinate specialized workflows, track API costs, and execute goals with self-correcting logic.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feat, key) => (
            <GlassCard key={key} className="p-8 border-white/[0.04] hover:-translate-y-1 transition-transform">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-6 text-indigo-400">
                <feat.icon className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold tracking-tight text-slate-100">{feat.title}</h3>
              <p className="text-xs text-slate-400 mt-3 leading-relaxed">{feat.desc}</p>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* 4. Meet Your AI Agents Showcase */}
      <section className="py-24 border-t border-white/[0.04] bg-zinc-950/20 relative z-10">
        <div className="max-w-5xl mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={scrollReveal}
            className="text-center max-w-2xl mx-auto mb-16"
          >
            <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest">Agent Registry</span>
            <h2 className="text-3xl md:text-4xl font-extrabold mt-2 tracking-tight">
              Specialized Core Agents
            </h2>
            <p className="text-sm text-slate-400 mt-4 leading-relaxed">
              Every workflow spawns dedicated agent processes matching your requirements, controlled and synchronized via a centralized planning node.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {agents.map((agent, key) => (
              <GlassCard key={key} className="p-8 border-white/[0.04] relative group">
                <div className="absolute top-4 right-4 flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-emerald-500/20 bg-emerald-500/5 text-[9px] font-mono text-emerald-400 uppercase">
                  <span className="w-1 h-1 rounded-full bg-emerald-400 animate-pulse" />
                  <span>Ready</span>
                </div>

                <span className="text-[10px] font-mono text-slate-500 tracking-wider uppercase block mb-1">{agent.role}</span>
                <h3 className="text-lg font-bold text-slate-200">{agent.name}</h3>
                
                <div className="mt-6 pt-4 border-t border-white/[0.04] space-y-2">
                  <span className="text-[9px] font-mono text-slate-500 uppercase tracking-wider block mb-1">Capabilities</span>
                  {agent.capabilities.map((cap, cKey) => (
                    <div key={cKey} className="flex items-center gap-2 text-xs text-slate-400">
                      <Check className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{cap}</span>
                    </div>
                  ))}
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* 5. Interactive Simulation Console */}
      <section className="py-24 border-t border-white/[0.04] relative z-10">
        <div className="max-w-5xl mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={scrollReveal}
            className="text-center max-w-2xl mx-auto mb-10"
          >
            <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest">Interactive Command Simulator</span>
            <h2 className="text-3xl md:text-4xl font-extrabold mt-2 tracking-tight">
              Test Drive the Agent Engine
            </h2>
            <p className="text-sm text-slate-400 mt-4 leading-relaxed">
              Select one of the preset CLI commands below to watch the AgentX orchestrator run plans, query tools, and generate responses in a simulated terminal environment.
            </p>
          </motion.div>

          <InteractiveConsole />
        </div>
      </section>

      {/* 6. Pricing Plans */}
      <section className="py-24 border-t border-white/[0.04] bg-zinc-950/20 relative z-10">
        <div className="max-w-5xl mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={scrollReveal}
            className="text-center max-w-2xl mx-auto mb-16"
          >
            <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest">Deploy Options</span>
            <h2 className="text-3xl md:text-4xl font-extrabold mt-2 tracking-tight">
              Simple, Transparent Pricing
            </h2>
            <p className="text-sm text-slate-400 mt-4 leading-relaxed">
              Start prototyping loops locally for free, or upgrade to Scale Operator for high-availability cloud cluster nodes.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 items-stretch">
            {pricingPlans.map((plan, key) => (
              <GlassCard 
                key={key} 
                className={`p-8 border-white/[0.04] flex flex-col justify-between relative ${
                  plan.featured ? 'border-indigo-500/30 shadow-[0_0_40px_-15px_rgba(99,102,241,0.15)] ring-1 ring-indigo-500/25' : ''
                }`}
              >
                {plan.featured && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 text-[9px] font-mono font-bold tracking-widest uppercase text-white shadow-lg">
                    Recommended
                  </span>
                )}

                <div>
                  <h3 className="text-lg font-bold text-slate-100">{plan.name}</h3>
                  <p className="text-xs text-slate-400 mt-2 min-h-[32px]">{plan.desc}</p>
                  
                  <div className="my-6 flex items-baseline gap-1">
                    <span className="text-4xl font-black text-white">{plan.price}</span>
                    {plan.period && <span className="text-xs font-mono text-slate-500">{plan.period}</span>}
                  </div>

                  <div className="space-y-3 pt-4 border-t border-white/[0.04]">
                    {plan.features.map((feature, fIdx) => (
                      <div key={fIdx} className="flex items-start gap-2.5 text-xs text-slate-400 leading-tight">
                        <Check className="w-3.5 h-3.5 text-indigo-400 mt-0.5 shrink-0" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  onClick={plan.action}
                  className={`w-full py-2.5 mt-8 rounded-xl font-medium text-xs tracking-wider transition-all duration-300 cursor-pointer ${
                    plan.featured 
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white shadow-lg shadow-indigo-500/10'
                      : 'bg-white/[0.02] border border-white/[0.06] hover:bg-white/[0.05] text-slate-300 hover:text-white'
                  }`}
                >
                  {plan.cta}
                </button>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* 7. Collapsible FAQ Section */}
      <section className="py-24 border-t border-white/[0.04] relative z-10">
        <div className="max-w-3xl mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={scrollReveal}
            className="text-center max-w-2xl mx-auto mb-16"
          >
            <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest">Support Core</span>
            <h2 className="text-3xl font-extrabold mt-2 tracking-tight">Frequently Asked Questions</h2>
          </motion.div>

          <div className="space-y-4">
            {faqs.map((faq, index) => {
              const isOpen = openFaqIndex === index;
              return (
                <div 
                  key={index} 
                  className="border border-white/[0.04] rounded-2xl bg-white/[0.01] overflow-hidden transition-all duration-300"
                >
                  <button
                    onClick={() => setOpenFaqIndex(isOpen ? null : index)}
                    className="w-full flex items-center justify-between p-5 text-left text-sm font-semibold text-slate-200 hover:text-white hover:bg-white/[0.01] transition-all cursor-pointer"
                  >
                    <span>{faq.q}</span>
                    <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-300 ${isOpen ? 'rotate-180 text-indigo-400' : ''}`} />
                  </button>
                  
                  <AnimatePresence initial={false}>
                    {isOpen && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: 'easeInOut' }}
                      >
                        <div className="p-5 pt-0 text-xs text-slate-400 leading-relaxed border-t border-white/[0.03] bg-zinc-950/20">
                          {faq.a}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 8. Final CTA Action block */}
      <section className="py-24 border-t border-white/[0.04] bg-gradient-to-b from-transparent to-indigo-950/10 relative z-10">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={scrollReveal}
            className="space-y-6"
          >
            <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest">Execute Goal</span>
            <h2 className="text-4xl md:text-5xl font-black tracking-tight leading-tight">
              Ready to Orchestrate your agent army?
            </h2>
            <p className="text-sm text-slate-400 max-w-lg mx-auto leading-relaxed">
              Launch AgentX locally or in the cloud. Prototyping multi-agent loops takes seconds.
            </p>
            <div className="pt-4">
              <button
                onClick={() => onAuthClick('signup')}
                className="py-3 px-8 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold text-xs tracking-wider transition-all duration-300 shadow-xl shadow-indigo-500/25 flex items-center justify-center gap-2 mx-auto cursor-pointer"
              >
                <Zap className="w-3.5 h-3.5 text-white" />
                <span>Initialize Platform Operator</span>
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* 9. Premium Multi-column Footer */}
      <footer className="py-16 border-t border-white/[0.04] bg-zinc-950/50 relative z-10">
        <div className="max-w-5xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center">
                <Activity className="w-3.5 h-3.5 text-white" />
              </div>
              <span className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
                Agent<span className="text-indigo-400">X</span> OS
              </span>
            </div>
            <p className="text-[10px] font-mono text-slate-600">
              Autonomous Multi-Agent OS & event-driven workflow scheduler.
            </p>
          </div>

          <div>
            <h4 className="text-[10px] font-mono text-slate-400 uppercase tracking-widest mb-4">Platform</h4>
            <div className="space-y-2 text-[11px] text-slate-500 font-mono">
              <p className="hover:text-slate-300 transition-colors cursor-pointer">Core Engine</p>
              <p className="hover:text-slate-300 transition-colors cursor-pointer">Agent Marketplace</p>
              <p className="hover:text-slate-300 transition-colors cursor-pointer">Pricing Tiers</p>
            </div>
          </div>

          <div>
            <h4 className="text-[10px] font-mono text-slate-400 uppercase tracking-widest mb-4">Resources</h4>
            <div className="space-y-2 text-[11px] text-slate-500 font-mono">
              <p className="hover:text-slate-300 transition-colors cursor-pointer">API Docs</p>
              <p className="hover:text-slate-300 transition-colors cursor-pointer">Developer Forum</p>
              <p className="hover:text-slate-300 transition-colors cursor-pointer">Roadmap</p>
            </div>
          </div>

          <div>
            <h4 className="text-[10px] font-mono text-slate-400 uppercase tracking-widest mb-4">Operator</h4>
            <div className="space-y-2 text-[11px] text-slate-500 font-mono">
              <p className="hover:text-slate-300 transition-colors cursor-pointer">Console Log</p>
              <p className="hover:text-slate-300 transition-colors cursor-pointer">Contact Support</p>
              <p className="text-emerald-500">System: Active</p>
            </div>
          </div>
        </div>

        <div className="max-w-5xl mx-auto px-6 mt-12 pt-6 border-t border-white/[0.03] flex justify-between items-center text-[9px] font-mono text-slate-600">
          <span>&copy; 2026 AgentX Ecosystem. All rights reserved.</span>
          <span>Security Clearance Level 4</span>
        </div>
      </footer>
    </div>
  );
};
