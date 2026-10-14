"use client";

import React from "react";
import { Bell, CheckCircle2, AlertCircle, Info, Download, X } from "lucide-react";

interface NotificationCenterProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const notifications = [
    { id: 1, type: "success", title: "Mission Completed", message: "Plan a 5-Day Cultural Trip to Paris", time: "2m ago" },
    { id: 2, type: "download", title: "Artifact Ready", message: "FastAPI REST API code deliverable", time: "1h ago" },
    { id: 3, type: "info", title: "Knowledge Indexed", message: "AgentX Architecture guidelines synced", time: "3h ago" }
  ];

  return (
    <div className="fixed top-16 right-6 w-80 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-50 overflow-hidden backdrop-blur-xl">
      <div className="p-4 border-b border-slate-800 flex justify-between items-center">
        <div className="flex items-center space-x-2 text-sm font-bold text-white">
          <Bell className="w-4 h-4 text-indigo-400" />
          <span>Notifications</span>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="divide-y divide-slate-800/60 max-h-80 overflow-y-auto">
        {notifications.map((n) => (
          <div key={n.id} className="p-3.5 hover:bg-slate-800/40 transition flex items-start space-x-3">
            {n.type === "success" && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />}
            {n.type === "download" && <Download className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />}
            {n.type === "info" && <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />}

            <div className="flex-1">
              <div className="flex justify-between items-center text-xs font-semibold text-slate-100">
                <span>{n.title}</span>
                <span className="text-slate-500 font-mono text-[10px]">{n.time}</span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">{n.message}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NotificationCenter;
