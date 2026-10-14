import React, { useState, useEffect } from 'react';
import { GlassCard } from '../ui/glass-card';
import { approvalService, ApprovalResponse } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Check, 
  X, 
  Terminal,
  Loader2,
  Calendar
} from 'lucide-react';
import { toast } from 'sonner';

export const ApprovalsView: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalResponse[]>([]);
  const [activeTab, setActiveTab] = useState<'pending' | 'resolved'>('pending');
  const [loading, setLoading] = useState(false);

  const fetchApprovals = async () => {
    setLoading(true);
    try {
      // List either pending or completed (approved/rejected) approvals
      const filter = activeTab === 'pending' ? 'pending' : '';
      const data = await approvalService.listApprovals(filter);
      
      if (activeTab === 'resolved') {
        // filter out pending items if we want resolved only
        setApprovals(data.filter(item => item.status !== 'pending'));
      } else {
        setApprovals(data);
      }
    } catch (err) {
      console.error('Error loading approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, [activeTab]);

  const handleResolve = async (id: string, action: 'approved' | 'rejected') => {
    try {
      await approvalService.resolveApproval(id, action);
      toast.success(`Approval request resolved as ${action.toUpperCase()}`);
      fetchApprovals();
    } catch (err: any) {
      toast.error('Could not resolve request: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <GlassCard className="p-6 flex justify-between items-center" hoverGlow={false}>
        <div>
          <h2 className="text-xl font-semibold text-white">HITL Governance Console</h2>
          <p className="text-xs text-slate-400 mt-1">Review, authorize, or abort high-impact agent actions before tool executions execute.</p>
        </div>
        <div className="flex gap-1.5 p-1 rounded-xl bg-slate-900 border border-white/[0.05]">
          <button
            onClick={() => setActiveTab('pending')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wider transition-colors ${
              activeTab === 'pending' ? 'bg-indigo-500 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            PENDING
          </button>
          <button
            onClick={() => setActiveTab('resolved')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wider transition-colors ${
              activeTab === 'resolved' ? 'bg-indigo-500 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            HISTORY
          </button>
        </div>
      </GlassCard>

      {/* Main Approvals Grid */}
      {loading ? (
        <div className="flex justify-center items-center py-24">
          <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
        </div>
      ) : approvals.length === 0 ? (
        <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
          <ShieldCheck className="w-12 h-12 text-slate-600 mb-4" />
          <h3 className="text-sm font-semibold text-slate-300">
            {activeTab === 'pending' ? 'All Operations Authorized' : 'No governance history'}
          </h3>
          <p className="text-xs text-slate-500 mt-1 max-w-xs">
            {activeTab === 'pending' 
              ? 'No tools are currently frozen waiting for developer permissions.'
              : 'No resolved approval records found in database logs.'}
          </p>
        </GlassCard>
      ) : (
        <div className="space-y-4">
          <AnimatePresence mode="popLayout">
            {approvals.map((req) => (
              <motion.div
                key={req.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3 }}
              >
                <GlassCard className="p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-6" hoverGlow={true}>
                  <div className="space-y-3 flex-1">
                    <div className="flex items-center gap-3">
                      <span className="px-2.5 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-[10px] font-mono text-indigo-300 uppercase tracking-wider">
                        {req.agent_name}
                      </span>
                      <span className="text-xs font-semibold text-white font-mono">{req.tool_name}</span>
                      {req.status !== 'pending' && (
                        <span className={`text-[9px] px-2 py-0.5 rounded-full font-mono uppercase tracking-wider font-semibold ${
                          req.status === 'approved' 
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}>
                          {req.status}
                        </span>
                      )}
                    </div>

                    {/* Parameters Inspector */}
                    <div className="p-3.5 rounded-lg border border-white/[0.04] bg-slate-950 font-mono text-[11px] text-slate-300 max-w-2xl overflow-x-auto">
                      <div className="flex items-center gap-1.5 text-[9px] text-slate-500 uppercase tracking-wider mb-1.5">
                        <Terminal className="w-3.5 h-3.5 text-indigo-400" />
                        Execution Parameters
                      </div>
                      <pre>{JSON.stringify(req.parameters || {}, null, 2)}</pre>
                    </div>

                    <div className="flex items-center gap-1 text-[9px] font-mono text-slate-500">
                      <Calendar className="w-3.5 h-3.5" />
                      <span>Submitted: {new Date(req.created_at).toLocaleString()}</span>
                    </div>
                  </div>

                  {/* Actions (Only show if pending) */}
                  {req.status === 'pending' && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleResolve(req.id, 'approved')}
                        className="px-4 py-2 rounded-xl border border-emerald-500/20 bg-emerald-500/5 hover:bg-emerald-500/10 text-emerald-400 text-xs font-semibold flex items-center gap-1.5 transition-colors"
                      >
                        <Check className="w-4 h-4" /> Approve
                      </button>
                      <button
                        onClick={() => handleResolve(req.id, 'rejected')}
                        className="px-4 py-2 rounded-xl border border-rose-500/20 bg-rose-500/5 hover:bg-rose-500/10 text-rose-400 text-xs font-semibold flex items-center gap-1.5 transition-colors"
                      >
                        <X className="w-4 h-4" /> Reject
                      </button>
                    </div>
                  )}
                </GlassCard>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
};
