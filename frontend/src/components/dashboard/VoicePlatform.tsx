"use client";

import React, { useState } from "react";
import { Mic, MicOff, Volume2, VolumeX, Sparkles, Radio, Settings } from "lucide-react";

export const VoicePlatform: React.FC = () => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState("Tap 'Start Listening' to converse with AgentX...");

  const toggleListening = () => {
    if (!isListening) {
      setIsListening(true);
      setTranscript("Listening... Speak your mission requirements now.");
      setTimeout(() => {
        setIsListening(false);
        setTranscript("Captured: 'Plan a 5-Day Cultural Trip to Paris'");
        setIsSpeaking(true);
        setTimeout(() => setIsSpeaking(false), 3000);
      }, 4000);
    } else {
      setIsListening(false);
      setTranscript("Voice session paused.");
    }
  };

  return (
    <div className="w-full h-full p-6 bg-slate-950 text-slate-100 flex flex-col items-center justify-center space-y-8">
      <div className="text-center space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
          <Radio className="w-3.5 h-3.5 animate-pulse" />
          <span>Real-Time Voice Experience Layer</span>
        </div>
        <h2 className="text-2xl font-bold text-white">Speak directly to your AI Operating System</h2>
        <p className="text-slate-400 text-xs max-w-md">
          Zero latency voice recognition, streaming speech responses, and instant wake-word support.
        </p>
      </div>

      {/* Animated Wave Visualizer */}
      <div className="flex items-center space-x-2 h-20">
        {[40, 75, 30, 90, 60, 100, 45, 80, 55, 35].map((h, i) => (
          <div
            key={i}
            className={`w-2 rounded-full transition-all duration-300 ${
              isListening
                ? "bg-indigo-500 animate-pulse"
                : isSpeaking
                ? "bg-emerald-400 animate-bounce"
                : "bg-slate-800"
            }`}
            style={{ height: isListening || isSpeaking ? `${h}%` : "20%" }}
          />
        ))}
      </div>

      {/* Big Voice Toggle Button */}
      <button
        onClick={toggleListening}
        className={`p-8 rounded-full shadow-2xl transition duration-300 cursor-pointer ${
          isListening
            ? "bg-red-600 hover:bg-red-500 ring-8 ring-red-500/20"
            : "bg-indigo-600 hover:bg-indigo-500 ring-8 ring-indigo-500/20"
        }`}
      >
        {isListening ? <MicOff className="w-10 h-10 text-white" /> : <Mic className="w-10 h-10 text-white" />}
      </button>

      {/* Live Transcript Display */}
      <div className="max-w-lg w-full p-4 bg-slate-900/80 border border-slate-800 rounded-xl text-center text-sm text-slate-300 font-mono">
        {transcript}
      </div>
    </div>
  );
};

export default VoicePlatform;
