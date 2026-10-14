'use client';

import React, { useState, useEffect } from 'react';
import { GlassCard } from '../ui/glass-card';
import { 
  Users, 
  Building, 
  CreditCard, 
  ShieldCheck, 
  Activity, 
  Cpu, 
  ShieldAlert, 
  Trash2, 
  RefreshCw, 
  UserCheck, 
  Server, 
  Clock, 
  Coins, 
  Lock, 
  AlertTriangle,
  Loader2,
  Database,
  Terminal
} from 'lucide-react';
import { toast } from 'sonner';
import { adminService, UserAdminResponse, SystemMetricsResponse, AuditLogResponse } from '@/services/api';

// ==========================================
// 1. ADMIN DASHBOARD VIEW
// ==========================================
export const AdminDashboardView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Server className="w-5 h-5 text-indigo-400" />
            Control Center Dashboard
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Global operational overview of the AgentX enterprise cluster and cognitive workloads.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <GlassCard className="p-5 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Users className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] font-mono text-zinc-400 uppercase">Total User Seats</p>
            <h3 className="text-lg font-bold text-white mt-0.5">3 / 25 Active</h3>
          </div>
        </GlassCard>

        <GlassCard className="p-5 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Building className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] font-mono text-zinc-400 uppercase">Active Organizations</p>
            <h3 className="text-lg font-bold text-white mt-0.5">1 Tenants</h3>
          </div>
        </GlassCard>

        <GlassCard className="p-5 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <CreditCard className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] font-mono text-zinc-400 uppercase">Token Spend (MTD)</p>
            <h3 className="text-lg font-bold text-white mt-0.5">$18.42</h3>
          </div>
        </GlassCard>

        <GlassCard className="p-5 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] font-mono text-zinc-400 uppercase">Kernel System Health</p>
            <h3 className="text-lg font-bold text-emerald-400 mt-0.5">99.98%</h3>
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="lg:col-span-2 p-6 space-y-4">
          <h3 className="text-sm font-semibold text-white">System Logs & Event Streaming Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3.5 rounded-xl border border-white/[0.04] bg-white/[0.01]">
              <span className="text-xs font-mono text-zinc-300">FastAPI Orchestrator Gateway</span>
              <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">ONLINE</span>
            </div>
            <div className="flex justify-between items-center p-3.5 rounded-xl border border-white/[0.04] bg-white/[0.01]">
              <span className="text-xs font-mono text-zinc-300">Asynchronous Event Bus Queue</span>
              <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">CONNECTED</span>
            </div>
            <div className="flex justify-between items-center p-3.5 rounded-xl border border-white/[0.04] bg-white/[0.01]">
              <span className="text-xs font-mono text-zinc-300">Vector Search Pool Size</span>
              <span className="text-[10px] font-mono text-zinc-400">15 / 50 Connections</span>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-6 space-y-4">
          <h3 className="text-sm font-semibold text-white">Security Alerts</h3>
          <div className="space-y-3">
            <div className="p-3.5 rounded-xl border border-amber-500/10 bg-amber-500/[0.01] flex items-start gap-3">
              <AlertTriangle className="w-4.5 h-4.5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-xs font-bold text-white">Development Seeding Triggered</h4>
                <p className="text-[10px] text-zinc-400 mt-0.5">Admin and Developer accounts seeded successfully on startup.</p>
              </div>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

// ==========================================
// 2. USER SEAT MANAGEMENT (WITH ROLE EDITS)
// ==========================================
export const UserManagementView: React.FC = () => {
  const [users, setUsers] = useState<UserAdminResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await adminService.listUsers();
      setUsers(data);
    } catch (err: any) {
      toast.error('Failed to load seats: ' + (err.message || 'Permission denied.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      setUpdatingId(userId);
      await adminService.updateUserRole(userId, newRole);
      toast.success('User role updated successfully.');
      fetchUsers();
    } catch (err: any) {
      toast.error('Failed to update role: ' + (err.message || 'Unknown error'));
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-400" />
            User Seat & Access Controls
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Provision user licenses, assign RBAC workspaces, and modify security group bindings.
          </p>
        </div>
        <button 
          onClick={fetchUsers} 
          className="p-2 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.08] text-zinc-300 hover:text-white transition-colors cursor-pointer"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <GlassCard className="p-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-12 space-y-3">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            <p className="text-xs font-mono text-zinc-400 uppercase tracking-wider">RETRIEVING REGISTERED USERS...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-white/[0.06] text-zinc-400 font-mono uppercase tracking-wider text-[10px]">
                  <th className="pb-3 pl-2">Email Address</th>
                  <th className="pb-3">User Identifier</th>
                  <th className="pb-3">Assigned Role</th>
                  <th className="pb-3">Created Date</th>
                  <th className="pb-3 pr-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-white/[0.01] transition-colors">
                    <td className="py-4 pl-2 font-semibold text-white">{u.email}</td>
                    <td className="py-4 font-mono text-zinc-400 text-[11px]">{u.id}</td>
                    <td className="py-4">
                      {updatingId === u.id ? (
                        <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
                      ) : (
                        <select
                          value={u.role}
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          className="bg-zinc-900 border border-white/[0.08] text-zinc-200 text-xs rounded-lg px-2.5 py-1 focus:outline-none focus:border-indigo-500/50"
                        >
                          <option value="user">User</option>
                          <option value="developer">Developer</option>
                          <option value="admin">Admin</option>
                        </select>
                      )}
                    </td>
                    <td className="py-4 text-zinc-400">{new Date(u.created_at).toLocaleDateString()}</td>
                    <td className="py-4 pr-2 text-right">
                      <button 
                        onClick={() => toast.error('Seat deletion is restricted in development environment.')}
                        className="p-1.5 rounded-lg hover:bg-rose-500/10 text-rose-400/80 hover:text-rose-400 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>
    </div>
  );
};

// ==========================================
// 3. ORGANIZATIONS / TENANTS VIEW
// ==========================================
export const OrganizationManagementView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Building className="w-5 h-5 text-indigo-400" />
            Enterprise Tenants & Organizations
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Configure multi-tenancy parameters, map subdomains, and toggle organization features.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <GlassCard className="p-5 border-indigo-500/10 bg-indigo-500/[0.01] flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="px-2.5 py-0.5 rounded-full text-[9px] font-mono font-bold uppercase tracking-wider border bg-indigo-500/10 border-indigo-500/20 text-indigo-400">
                DEFAULT TENANT
              </span>
              <span className="text-[10px] font-mono text-zinc-500">ID: tenant_default</span>
            </div>
            <h3 className="text-sm font-semibold text-white">AgentX Enterprise Default</h3>
            <p className="text-xs text-zinc-400">
              Primary organization group managing administrative operator seats.
            </p>
          </div>
          <div className="border-t border-white/[0.03] pt-3 flex justify-between items-center text-[10px] font-mono text-zinc-500">
            <span>MEMBERS: 3</span>
            <span className="text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer uppercase">CONFIGURE</span>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

// ==========================================
// 4. BILLING & COST ANALYSIS
// ==========================================
export const BillingCostsView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-indigo-400" />
            Billing & Token Expenditures
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Track OpenAI/Anthropic model spending, monitor API credit balances, and set monthly hard limits.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="p-6 space-y-4 lg:col-span-2">
          <h3 className="text-sm font-semibold text-white">Monthly Expenditure Summary</h3>
          <div className="space-y-4">
            <div className="w-full bg-zinc-900/60 rounded-xl p-4 border border-white/[0.04] space-y-3">
              <div className="flex justify-between text-xs">
                <span className="text-zinc-400">Monthly Spending Budget</span>
                <span className="text-white font-mono font-bold">$18.42 / $200.00</span>
              </div>
              <div className="w-full h-2 rounded-full bg-zinc-950 overflow-hidden">
                <div className="h-full bg-indigo-500 transition-all duration-300" style={{ width: '9.21%' }} />
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest px-1">Spend by Provider</h4>
              <div className="flex justify-between p-3 rounded-lg border border-white/[0.03] bg-white/[0.01] text-xs">
                <span className="text-zinc-300 font-semibold">OpenAI API Connection</span>
                <span className="text-white font-mono">$12.18</span>
              </div>
              <div className="flex justify-between p-3 rounded-lg border border-white/[0.03] bg-white/[0.01] text-xs">
                <span className="text-zinc-300 font-semibold">Anthropic Claude Router</span>
                <span className="text-white font-mono">$6.24</span>
              </div>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-6 space-y-4 h-fit">
          <h3 className="text-sm font-semibold text-white">Corporate Invoices</h3>
          <p className="text-xs text-zinc-400">
            No invoices generated yet for the current billing cycle. Default development tier active.
          </p>
        </GlassCard>
      </div>
    </div>
  );
};

// ==========================================
// 5. SECURITY & AUDIT LOGS VIEW
// ==========================================
export const SecurityAuditsView: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await adminService.getAuditLogs();
      setLogs(data);
    } catch (err: any) {
      toast.error('Failed to load audit logs: ' + (err.message || 'Permission denied.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-indigo-400" />
            Security Events & Audit Logs
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Trace administrative configuration adjustments, API invocations, and cryptographic keys deployment.
          </p>
        </div>
        <button 
          onClick={fetchLogs} 
          className="p-2 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.08] text-zinc-300 hover:text-white transition-colors cursor-pointer"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <GlassCard className="p-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-12 space-y-3">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            <p className="text-xs font-mono text-zinc-400 uppercase tracking-wider">RETRIEVING AUDIT LOG STREAM...</p>
          </div>
        ) : logs.length === 0 ? (
          <p className="text-xs text-zinc-500 text-center py-12">No recent model calls or administrative audit logs found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-white/[0.06] text-zinc-400 font-mono uppercase tracking-wider text-[10px]">
                  <th className="pb-3 pl-2">Timestamp</th>
                  <th className="pb-3">Provider</th>
                  <th className="pb-3">Model</th>
                  <th className="pb-3">Prompt/Comp Tokens</th>
                  <th className="pb-3">Latency (ms)</th>
                  <th className="pb-3 pr-2 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {logs.map((l) => (
                  <tr key={l.id} className="hover:bg-white/[0.01] transition-colors">
                    <td className="py-4 pl-2 text-zinc-400 font-mono text-[11px]">
                      {new Date(l.created_at).toLocaleTimeString()}
                    </td>
                    <td className="py-4 font-semibold text-white uppercase">{l.provider}</td>
                    <td className="py-4 text-zinc-300">{l.model_name}</td>
                    <td className="py-4 text-zinc-400 font-mono">
                      {l.prompt_tokens} / {l.completion_tokens}
                    </td>
                    <td className="py-4 text-zinc-400 font-mono">{l.latency_ms}ms</td>
                    <td className="py-4 pr-2 text-right">
                      <span className={`text-[8px] font-mono font-bold px-2 py-0.5 rounded-full uppercase border ${
                        l.status === 'success'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                      }`}>
                        {l.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>
    </div>
  );
};

// ==========================================
// 6. SYSTEM HEALTH & DIAGNOSTICS VIEW
// ==========================================
export const SystemHealthView: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await adminService.getMetrics();
      setMetrics(data);
    } catch (err: any) {
      toast.error('Failed to load system metrics: ' + (err.message || 'Permission denied.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-white/[0.05] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400" />
            System Health & Telemetry
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Monitor infrastructure usage metrics, database connections, and memory status.
          </p>
        </div>
        <button 
          onClick={fetchMetrics} 
          className="p-2 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.08] text-zinc-300 hover:text-white transition-colors cursor-pointer"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-12 space-y-3">
          <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
          <p className="text-xs font-mono text-zinc-400 uppercase tracking-wider">LOADING HEALTH METRICS...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <GlassCard className="p-6 space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Database className="w-4 h-4 text-indigo-400" />
              Database Engine
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between text-xs">
                <span className="text-zinc-400">Database System</span>
                <span className="text-white font-mono uppercase">{metrics?.database_type}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-zinc-400">Total User Records</span>
                <span className="text-white font-mono">{metrics?.total_users}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-zinc-400">Total Goals Persistent</span>
                <span className="text-white font-mono">{metrics?.total_goals}</span>
              </div>
            </div>
          </GlassCard>

          <GlassCard className="p-6 space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Terminal className="w-4 h-4 text-indigo-400" />
              Model Call Telemetry
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between text-xs">
                <span className="text-zinc-400">Total Logs Tracked</span>
                <span className="text-white font-mono">{metrics?.total_model_calls}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-zinc-400">Logs Queue Capacity</span>
                <span className="text-white font-mono">10,000 max</span>
              </div>
            </div>
          </GlassCard>

          <GlassCard className="p-6 space-y-4">
            <h3 className="text-sm font-semibold text-rose-400 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4" />
              Emergency Reset
            </h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Drop all dynamic workflow runs, clear active log registers, and reset user sessions.
            </p>
            <button 
              onClick={() => toast.error('Emergency cleanup is disabled in development mode.')}
              className="w-full py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/25 text-rose-400 text-xs font-semibold transition-colors cursor-pointer"
            >
              Trigger System Reset
            </button>
          </GlassCard>
        </div>
      )}
    </div>
  );
};
