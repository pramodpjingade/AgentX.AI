"use client";

import React from "react";
import { FolderOpen, FileText, Code, Image as ImageIcon, Download, Share2, Eye } from "lucide-react";

export const ArtifactCenter: React.FC = () => {
  const artifacts = [
    { name: "Paris_Cultural_Trip_Itinerary.md", type: "Markdown", size: "4.2 KB", date: "Today" },
    { name: "FastAPI_Authentication_Service.py", type: "Code", size: "12.8 KB", date: "Today" },
    { name: "Basketball_Academy_Syllabus.pdf", type: "PDF Document", size: "245 KB", date: "Yesterday" },
    { name: "Cybersecurity_RBAC_Audit_Report.docx", type: "Word Document", size: "88 KB", date: "2 days ago" }
  ];

  return (
    <div className="w-full h-full p-6 bg-slate-950 text-slate-100 overflow-y-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <FolderOpen className="w-5 h-5 text-indigo-400" />
            <span>Artifact Center</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Manage, download, and share generated deliverables across all executed missions.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {artifacts.map((art, idx) => (
          <div
            key={idx}
            className="p-4 bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 rounded-xl flex items-center justify-between transition"
          >
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-slate-800 rounded-lg text-indigo-400">
                {art.type === "Code" ? <Code className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
              </div>
              <div>
                <h4 className="text-sm font-semibold text-white">{art.name}</h4>
                <div className="text-xs text-slate-400 mt-0.5 flex space-x-2">
                  <span>{art.type}</span>
                  <span>•</span>
                  <span>{art.size}</span>
                  <span>•</span>
                  <span>{art.date}</span>
                </div>
              </div>
            </div>

            <div className="flex space-x-2">
              <button className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition">
                <Download className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ArtifactCenter;
