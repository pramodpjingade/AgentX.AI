import React, { useState, useEffect } from 'react';
import { GlassCard } from '../ui/glass-card';
import { pluginService, api, PluginResponse } from '@/services/api';
import { 
  Grid, 
  Search, 
  Cpu, 
  DownloadCloud, 
  Trash2, 
  Loader2,
  Sparkles,
  Link,
  ShieldCheck
} from 'lucide-react';
import { toast } from 'sonner';

export const PluginsView: React.FC = () => {
  const [plugins, setPlugins] = useState<PluginResponse[]>([]);
  const [query, setQuery] = useState('');
  const [discoveredAgents, setDiscoveredAgents] = useState<string[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [listLoading, setListLoading] = useState(false);
  
  // Plugin creation form states
  const [newPluginName, setNewPluginName] = useState('');
  const [newPluginVersion, setNewPluginVersion] = useState('1.0.0');

  const fetchPlugins = async () => {
    setListLoading(true);
    try {
      const data = await pluginService.listPlugins();
      setPlugins(data);
    } catch (err) {
      console.error('Error fetching plugins:', err);
    } finally {
      setListLoading(false);
    }
  };

  useEffect(() => {
    fetchPlugins();
  }, []);

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;
    setSearchLoading(true);
    try {
      // Fetch matched capabilities from Python FastAPI backend `/api/v1/plugins` (capability registries)
      // We will perform a direct call to test matching
      const response = await api.get('/plugins');
      
      // Simulating the dynamic capability matching return
      // e.g. web_scraper capability resolves to research_agent, stock_analysis_agent
      if (query.toLowerCase().includes('search') || query.toLowerCase().includes('scrap')) {
        setDiscoveredAgents(['research_agent', 'stock_analysis_agent']);
      } else {
        setDiscoveredAgents(['safety_guardian_agent', 'supervisor_agent']);
      }
      toast.success(`Discovered matching agents for: ${query}`);
    } catch (err: any) {
      toast.error('Search failed: ' + err.message);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleRegisterPlugin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPluginName || !newPluginVersion) return;
    try {
      await pluginService.installPlugin(newPluginName, newPluginVersion, ['research_agent']);
      toast.success(`Registered plugin: ${newPluginName}`);
      setNewPluginName('');
      fetchPlugins();
    } catch (err: any) {
      toast.error('Registration failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDeregister = async (name: string) => {
    try {
      await pluginService.uninstallPlugin(name);
      toast.warning(`Uninstalled plugin: ${name}`);
      fetchPlugins();
    } catch (err: any) {
      toast.error('Uninstall failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
      {/* Sidebar Discovery Panel */}
      <div className="space-y-6 lg:col-span-1">
        {/* Capability registry search */}
        <GlassCard className="p-6 space-y-4" hoverGlow={false}>
          <div className="flex items-center gap-2 border-b border-white/[0.05] pb-3">
            <Search className="w-5 h-5 text-indigo-400" />
            <h3 className="text-sm font-semibold text-white">Capability Discovery</h3>
          </div>

          <form onSubmit={handleQuery} className="space-y-3">
            <div className="space-y-1.5">
              <label className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">Required Capability</label>
              <input
                type="text"
                placeholder="e.g. web_scraper, search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-white/[0.07] bg-slate-900/30 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
                required
              />
            </div>

            <button
              type="submit"
              disabled={searchLoading}
              className="w-full py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs tracking-wider transition-colors flex items-center justify-center gap-2"
            >
              {searchLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'QUERY REGISTRY'}
            </button>
          </form>

          {/* Discovered Agents Output */}
          {discoveredAgents.length > 0 && (
            <div className="space-y-2 pt-3 border-t border-white/[0.05]">
              <h4 className="text-[9px] font-mono text-slate-500 uppercase tracking-widest">Matched Executor Agents</h4>
              <div className="space-y-1.5">
                {discoveredAgents.map((agent, i) => (
                  <div key={i} className="flex items-center gap-2 p-2 rounded-lg border border-white/[0.04] bg-white/[0.01] text-xs text-white">
                    <Cpu className="w-4 h-4 text-indigo-400" />
                    <span>{agent}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </GlassCard>

        {/* Plugin creation registry */}
        <GlassCard className="p-6 space-y-4" hoverGlow={false}>
          <div className="flex items-center gap-2 border-b border-white/[0.05] pb-3">
            <DownloadCloud className="w-5 h-5 text-indigo-400" />
            <h3 className="text-sm font-semibold text-white">Register Plugin Extension</h3>
          </div>

          <form onSubmit={handleRegisterPlugin} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">Plugin Identifier</label>
              <input
                type="text"
                placeholder="e.g. stock_analysis_agent"
                value={newPluginName}
                onChange={(e) => setNewPluginName(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-white/[0.07] bg-slate-900/30 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">Extension Version</label>
              <input
                type="text"
                value={newPluginVersion}
                onChange={(e) => setNewPluginVersion(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-white/[0.07] bg-slate-900/30 text-sm text-white focus:outline-none focus:border-indigo-500/50 transition-colors"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full py-2 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-medium text-xs tracking-wider transition-colors"
            >
              REGISTER EXTENSION
            </button>
          </form>
        </GlassCard>
      </div>

      {/* Plugins Directory */}
      <div className="lg:col-span-2 space-y-4">
        <GlassCard className="p-6" hoverGlow={false}>
          <div className="flex items-center justify-between border-b border-white/[0.05] pb-4">
            <h3 className="text-sm font-semibold text-white">Plugin Registry Directory</h3>
            <span className="text-[10px] font-mono text-indigo-400 tracking-wider">MARKETPLACE</span>
          </div>

          {listLoading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            </div>
          ) : plugins.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Grid className="w-10 h-10 text-slate-600 mb-2" />
              <p className="text-xs text-slate-400">No active plugin extensions registered.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              {plugins.map((plugin) => (
                <GlassCard key={plugin.id} className="p-4 flex flex-col justify-between h-40" hoverGlow={true}>
                  <div className="space-y-2">
                    <div className="flex justify-between items-start">
                      <h4 className="text-xs font-semibold text-white truncate max-w-[140px]">{plugin.plugin_name}</h4>
                      <span className="text-[9px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                        v{plugin.version}
                      </span>
                    </div>

                    <div className="flex items-center gap-1 text-[9px] text-slate-500 font-mono">
                      <Link className="w-3 h-3 text-indigo-400" />
                      <span>Deps: {plugin.dependencies.join(', ')}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-white/[0.04] mt-3">
                    <div className="flex items-center gap-1.5 text-[9px] text-emerald-400 font-mono">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>active</span>
                    </div>

                    <button
                      onClick={() => handleDeregister(plugin.plugin_name)}
                      className="p-1.5 rounded-lg border border-rose-500/20 bg-rose-500/5 hover:bg-rose-500/10 text-rose-400 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </GlassCard>
              ))}
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  );
};
