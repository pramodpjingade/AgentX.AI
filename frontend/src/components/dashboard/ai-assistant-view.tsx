'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAppStore } from '@/store';
import { GlassCard } from '../ui/glass-card';
import { 
  chatService, 
  ConversationHistory, 
  ChatMessage, 
  ChatStreamChunk
} from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Mic, 
  Paperclip, 
  ArrowRight, 
  Brain, 
  Cpu, 
  Plus,
  Trash2,
  RefreshCw,
  Copy,
  Download,
  Check,
  MessageSquare,
  Globe,
  Code,
  Compass,
  Loader2,
  FileText,
  Zap
} from 'lucide-react';
import { toast } from 'sonner';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const QUICK_PROMPTS = [
  {
    icon: Compass,
    title: "Plan a trip to Kerala",
    desc: "Custom 7-day backwater tour itinerary",
    prompt: "Plan a 7-day luxury trip to Kerala with houseboats, backwaters, and beach resorts."
  },
  {
    icon: Code,
    title: "Build a REST API",
    desc: "FastAPI server boilerplate with JWT auth",
    prompt: "Design a RESTful API backend using Python FastAPI with JWT authentication and SQLite."
  },
  {
    icon: Brain,
    title: "Teach me basketball",
    desc: "Syllabus for dribbling & Form shooting",
    prompt: "Create a beginner-friendly 4-week practice plan for learning basketball fundamentals."
  },
  {
    icon: Zap,
    title: "Get fitness routine",
    desc: "Strength training split & nutrition guide",
    prompt: "Formulate a 5-day progressive strength training workout split with macro nutrition tips."
  }
];

export const AIAssistantView: React.FC = () => {
  const { user } = useAppStore();
  const [conversations, setConversations] = useState<ConversationHistory[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentProgress, setCurrentProgress] = useState<number>(0);
  const [currentStatusMsg, setCurrentStatusMsg] = useState<string>('');
  const [selectedPreferences, setSelectedPreferences] = useState<string[]>(['web_search']);
  const [isVoiceListening, setIsVoiceListening] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [loadingHistory, setLoadingHistory] = useState(true);

  const chatContainerRef = useRef<HTMLDivElement>(null);
  const streamAbortRef = useRef<(() => void) | null>(null);

  // Load conversation history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  // Auto-scroll chat to bottom when messages update
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, currentStatusMsg, isStreaming]);

  const loadHistory = async () => {
    try {
      setLoadingHistory(true);
      const history = await chatService.listHistory();
      setConversations(history);
      if (history.length > 0 && !activeConvId) {
        setActiveConvId(history[0].conversation_id);
        setMessages(history[0].messages || []);
      }
    } catch (err) {
      console.error('Failed to load chat history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSelectConversation = async (convId: string) => {
    if (isStreaming) {
      toast.warning('Please wait for the current response to complete.');
      return;
    }
    setActiveConvId(convId);
    try {
      const detail = await chatService.getConversation(convId);
      setMessages(detail.messages || []);
    } catch (err) {
      toast.error('Failed to load conversation details.');
    }
  };

  const handleNewChat = () => {
    if (isStreaming) {
      toast.warning('Please wait for the active stream to finish.');
      return;
    }
    setActiveConvId(null);
    setMessages([]);
    setInputValue('');
  };

  const handleDeleteConversation = async (e: React.MouseEvent, convId: string) => {
    e.stopPropagation();
    try {
      await chatService.deleteConversation(convId);
      setConversations(prev => prev.filter(c => c.conversation_id !== convId));
      if (activeConvId === convId) {
        handleNewChat();
      }
      toast.success('Conversation deleted');
    } catch (err) {
      toast.error('Failed to delete conversation');
    }
  };

  const togglePreference = (pref: string) => {
    setSelectedPreferences(prev => 
      prev.includes(pref) ? prev.filter(p => p !== pref) : [...prev, pref]
    );
  };

  const handleSendMessage = async (textToSend?: string) => {
    const messageText = (textToSend || inputValue).trim();
    if (!messageText || isStreaming) return;

    setInputValue('');
    setIsStreaming(true);
    setCurrentProgress(10);
    setCurrentStatusMsg('Connecting to AgentX AI Core...');

    const userMsgId = 'usr_' + Date.now();
    const assistantMsgId = 'ast_' + Date.now();
    const targetConvId = activeConvId || undefined;

    // Append user message immediately
    const userMsg: ChatMessage = {
      message_id: userMsgId,
      conversation_id: targetConvId || 'temp',
      role: 'user',
      content: messageText,
      timestamp: Date.now() / 1000
    };

    // Append empty placeholder for assistant
    const placeholderAssistantMsg: ChatMessage = {
      message_id: assistantMsgId,
      conversation_id: targetConvId || 'temp',
      role: 'assistant',
      content: '',
      timestamp: Date.now() / 1000
    };

    setMessages(prev => [...prev, userMsg, placeholderAssistantMsg]);

    let accumulatedContent = '';

    const cancelStream = chatService.streamMessage(
      messageText,
      targetConvId,
      selectedPreferences,
      (chunk: ChatStreamChunk) => {
        if (chunk.conversation_id && !activeConvId) {
          setActiveConvId(chunk.conversation_id);
        }

        if (chunk.event === 'status_update') {
          if (chunk.status_message) setCurrentStatusMsg(chunk.status_message);
          if (chunk.progress_percentage !== undefined) setCurrentProgress(chunk.progress_percentage);
        } else if (chunk.event === 'assistant_stream') {
          if (chunk.content) {
            accumulatedContent += chunk.content;
            setMessages(prev => prev.map(m => {
              if (m.message_id === assistantMsgId) {
                return { ...m, content: accumulatedContent };
              }
              return m;
            }));
          }
        } else if (chunk.event === 'mission_completed') {
          setCurrentProgress(100);
          setCurrentStatusMsg('Completed');
        }
      },
      async () => {
        setIsStreaming(false);
        setCurrentStatusMsg('');
        loadHistory();
      },
      (err) => {
        console.error('Chat stream error:', err);
        toast.error('Stream interrupted: ' + (err.message || 'Error occurred'));
        setIsStreaming(false);
        setCurrentStatusMsg('');
      }
    );

    streamAbortRef.current = cancelStream;
  };

  const handleRegenerate = async () => {
    if (!activeConvId || isStreaming) return;
    setIsStreaming(true);
    setCurrentProgress(15);
    setCurrentStatusMsg('Regenerating AI response...');

    try {
      const resp = await chatService.regenerateMessage(activeConvId);
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          message_id: resp.message_id,
          conversation_id: resp.conversation_id,
          role: 'assistant',
          content: resp.content,
          timestamp: resp.timestamp
        }
      ]);
      toast.success('Response regenerated successfully.');
    } catch (err) {
      toast.error('Failed to regenerate response.');
    } finally {
      setIsStreaming(false);
      setCurrentStatusMsg('');
    }
  };

  const handleCopyText = (content: string, index: number) => {
    navigator.clipboard.writeText(content);
    setCopiedIndex(index);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleVoiceToggle = () => {
    setIsVoiceListening(!isVoiceListening);
    if (!isVoiceListening) {
      toast.info('Listening for voice input...');
      setTimeout(() => {
        setInputValue('Plan a 5-day holiday in Kerala');
        setIsVoiceListening(false);
        toast.success('Voice transcribed!');
      }, 2500);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-120px)] max-w-7xl mx-auto gap-4 py-2 relative z-10">
      
      {/* Left Sidebar: Conversation Threads */}
      <GlassCard className="w-full lg:w-72 p-4 flex flex-col justify-between border-white/[0.06] shrink-0 bg-zinc-950/60 backdrop-blur-xl">
        <div className="space-y-4 overflow-hidden flex flex-col h-full">
          {/* New Chat Button */}
          <button
            onClick={handleNewChat}
            className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold text-xs tracking-wider transition-all shadow-md shadow-indigo-500/20 flex items-center justify-center gap-2 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>NEW CHAT</span>
          </button>

          {/* Conversation List */}
          <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
            <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest px-2 py-1">
              RECENT CONVERSATIONS
            </div>

            {loadingHistory ? (
              <div className="p-4 text-center text-zinc-500 font-mono text-xs flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                <span>Loading threads...</span>
              </div>
            ) : conversations.length === 0 ? (
              <div className="p-4 text-center text-zinc-500 text-xs italic">
                No conversations yet. Start a new chat!
              </div>
            ) : (
              conversations.map((conv) => {
                const isActive = activeConvId === conv.conversation_id;

                return (
                  <div
                    key={conv.conversation_id}
                    onClick={() => handleSelectConversation(conv.conversation_id)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs transition-all cursor-pointer group ${
                      isActive
                        ? 'bg-indigo-500/15 border border-indigo-500/30 text-white font-semibold'
                        : 'text-zinc-400 hover:text-white hover:bg-white/[0.04]'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 overflow-hidden">
                      <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-indigo-400' : 'text-zinc-500'}`} />
                      <span className="truncate">{conv.title || 'Conversation'}</span>
                    </div>

                    <button
                      onClick={(e) => handleDeleteConversation(e, conv.conversation_id)}
                      className="p-1 text-zinc-600 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-opacity"
                      title="Delete thread"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </GlassCard>

      {/* Main Chat Workspace */}
      <GlassCard className="flex-1 flex flex-col justify-between border-white/[0.06] bg-zinc-950/60 backdrop-blur-xl overflow-hidden p-4 sm:p-6">
        
        {/* Chat Feed Area */}
        <div 
          ref={chatContainerRef} 
          className="flex-1 overflow-y-auto space-y-6 pr-2 mb-4 scrollbar-thin scrollbar-thumb-zinc-800"
        >
          {messages.length === 0 ? (
            /* Empty State Hero Screen */
            <div className="h-full flex flex-col items-center justify-center text-center space-y-8 max-w-2xl mx-auto py-8">
              <div className="flex flex-col items-center space-y-3">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 via-indigo-600 to-purple-600 flex items-center justify-center shadow-2xl shadow-indigo-500/30">
                  <Brain className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-extrabold text-white tracking-tight">
                    Agent<span className="text-indigo-400">X</span> Assistant
                  </h2>
                  <p className="text-xs font-mono text-zinc-400 uppercase tracking-widest mt-1">
                    AUTONOMOUS MULTI-AGENT CONVERSATIONAL ENGINE
                  </p>
                </div>
              </div>

              <p className="text-sm text-zinc-300 max-w-md">
                Ask me to plan trip itineraries, write REST APIs, summarize research, or automate complex workflows.
              </p>

              {/* Quick Template Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
                {QUICK_PROMPTS.map((item, idx) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(item.prompt)}
                      className="p-3.5 rounded-2xl border border-white/[0.05] bg-white/[0.01] hover:bg-white/[0.04] hover:border-indigo-500/30 text-left transition-all flex items-start gap-3 cursor-pointer group"
                    >
                      <div className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0 group-hover:scale-110 transition-transform">
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="overflow-hidden">
                        <h4 className="text-xs font-bold text-white group-hover:text-indigo-300 transition-colors">{item.title}</h4>
                        <p className="text-[11px] text-zinc-400 mt-0.5 line-clamp-1">{item.desc}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Active Message List */
            messages.map((msg, idx) => {
              const isUser = msg.role === 'user';

              return (
                <motion.div
                  key={msg.message_id || idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {!isUser && (
                    <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 text-white font-bold text-xs shadow-md shadow-indigo-500/20 mt-1">
                      X
                    </div>
                  )}

                  <div className={`max-w-[85%] space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
                    <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                      isUser
                        ? 'bg-indigo-600 text-white rounded-br-none shadow-md shadow-indigo-600/20'
                        : 'bg-zinc-900/80 border border-white/[0.08] text-zinc-200 rounded-bl-none shadow-lg'
                    }`}>
                      {msg.content ? (
                        isUser ? (
                          <div className="whitespace-pre-wrap font-sans">{msg.content}</div>
                        ) : (
                          <div className="prose prose-invert prose-sm max-w-none font-sans
                            prose-p:my-1 prose-p:leading-relaxed
                            prose-headings:text-white prose-headings:font-bold prose-headings:mt-3 prose-headings:mb-1
                            prose-h1:text-base prose-h2:text-sm prose-h3:text-sm
                            prose-strong:text-indigo-300 prose-strong:font-semibold
                            prose-em:text-zinc-300
                            prose-ul:my-1 prose-ul:pl-4 prose-li:my-0.5 prose-li:text-zinc-200
                            prose-ol:my-1 prose-ol:pl-4
                            prose-code:bg-zinc-800 prose-code:text-emerald-300 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-code:font-mono prose-code:before:content-none prose-code:after:content-none
                            prose-pre:bg-zinc-900 prose-pre:border prose-pre:border-white/10 prose-pre:rounded-xl prose-pre:p-3 prose-pre:overflow-x-auto prose-pre:my-2
                            prose-blockquote:border-l-2 prose-blockquote:border-indigo-500 prose-blockquote:pl-3 prose-blockquote:text-zinc-400 prose-blockquote:italic prose-blockquote:my-2
                            prose-table:text-xs prose-th:text-zinc-300 prose-td:text-zinc-400 prose-table:border-collapse
                            prose-a:text-indigo-400 prose-a:underline hover:prose-a:text-indigo-300
                          ">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                          </div>
                        )
                      ) : isStreaming && idx === messages.length - 1 ? (
                        <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>Generating response...</span>
                        </div>
                      ) : (
                        <span className="text-zinc-500 italic">Empty response</span>
                      )}
                    </div>

                    {/* Assistant Message Toolbar */}
                    {!isUser && msg.content && (
                      <div className="flex items-center gap-2 pt-1 px-1">
                        <button
                          onClick={() => handleCopyText(msg.content, idx)}
                          className="p-1.5 rounded-lg text-zinc-500 hover:text-white hover:bg-white/[0.05] transition-colors text-xs flex items-center gap-1 cursor-pointer"
                          title="Copy text"
                        >
                          {copiedIndex === idx ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                          <span className="text-[10px]">Copy</span>
                        </button>

                        {idx === messages.length - 1 && (
                          <button
                            onClick={handleRegenerate}
                            disabled={isStreaming}
                            className="p-1.5 rounded-lg text-zinc-500 hover:text-indigo-400 hover:bg-white/[0.05] transition-colors text-xs flex items-center gap-1 cursor-pointer disabled:opacity-50"
                            title="Regenerate"
                          >
                            <RefreshCw className="w-3.5 h-3.5" />
                            <span className="text-[10px]">Regenerate</span>
                          </button>
                        )}
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="w-8 h-8 rounded-xl bg-zinc-800 border border-white/[0.08] flex items-center justify-center shrink-0 text-zinc-300 font-bold text-xs mt-1">
                      {user?.email ? user.email.charAt(0).toUpperCase() : 'U'}
                    </div>
                  )}
                </motion.div>
              );
            })
          )}

          {/* Live Progress Banner during Streaming */}
          {isStreaming && (
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-3.5 rounded-2xl bg-zinc-900/90 border border-indigo-500/30 space-y-2 backdrop-blur-md"
            >
              <div className="flex justify-between items-center text-xs">
                <span className="text-indigo-400 font-bold flex items-center gap-1.5 font-mono">
                  <Cpu className="w-3.5 h-3.5 animate-spin text-indigo-400" />
                  {currentStatusMsg || 'Processing mission...'}
                </span>
                <span className="text-zinc-400 font-mono">{currentProgress}%</span>
              </div>
              <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden border border-white/[0.05]">
                <div 
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300"
                  style={{ width: `${currentProgress}%` }}
                />
              </div>
            </motion.div>
          )}
        </div>

        {/* Input Bar & Preferences Area */}
        <div className="space-y-3 pt-2 border-t border-white/[0.05]">
          
          {/* Capability Preference Toggles */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
            <button
              type="button"
              onClick={() => togglePreference('web_search')}
              className={`px-3 py-1 rounded-xl border text-[11px] font-medium transition-all flex items-center gap-1.5 cursor-pointer shrink-0 ${
                selectedPreferences.includes('web_search')
                  ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                  : 'bg-white/[0.02] border-white/[0.06] text-zinc-400 hover:text-white'
              }`}
            >
              <Globe className="w-3 h-3" /> Web Search
            </button>

            <button
              type="button"
              onClick={() => togglePreference('code_mode')}
              className={`px-3 py-1 rounded-xl border text-[11px] font-medium transition-all flex items-center gap-1.5 cursor-pointer shrink-0 ${
                selectedPreferences.includes('code_mode')
                  ? 'bg-purple-500/20 border-purple-500/40 text-purple-300'
                  : 'bg-white/[0.02] border-white/[0.06] text-zinc-400 hover:text-white'
              }`}
            >
              <Code className="w-3 h-3" /> Code Generation
            </button>

            <button
              type="button"
              onClick={() => togglePreference('deep_research')}
              className={`px-3 py-1 rounded-xl border text-[11px] font-medium transition-all flex items-center gap-1.5 cursor-pointer shrink-0 ${
                selectedPreferences.includes('deep_research')
                  ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                  : 'bg-white/[0.02] border-white/[0.06] text-zinc-400 hover:text-white'
              }`}
            >
              <Brain className="w-3 h-3" /> Deep Research
            </button>
          </div>

          {/* Main Input Control Box */}
          <div className="relative flex items-center bg-zinc-900/80 border border-white/[0.08] focus-within:border-indigo-500/50 rounded-2xl p-2 shadow-2xl backdrop-blur-xl transition-all">
            <div className="pl-3 pr-2 text-indigo-400">
              <Sparkles className="w-4 h-4 animate-pulse" />
            </div>

            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Ask AgentX Assistant anything..."
              className="flex-1 bg-transparent border-none text-white text-sm focus:outline-none placeholder-zinc-500 py-1.5 font-sans"
              disabled={isStreaming}
            />

            <div className="flex items-center gap-1.5 pr-1">
              <button
                type="button"
                onClick={handleVoiceToggle}
                className={`p-2 rounded-xl border transition-colors cursor-pointer ${
                  isVoiceListening
                    ? 'bg-rose-500/20 border-rose-500/40 text-rose-300 animate-pulse'
                    : 'text-zinc-500 hover:text-white border-transparent hover:bg-white/[0.04]'
                }`}
                title="Voice Input"
              >
                <Mic className="w-4 h-4" />
              </button>

              <button
                type="button"
                onClick={() => handleSendMessage()}
                disabled={!inputValue.trim() || isStreaming}
                className="p-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 disabled:opacity-40 text-white shadow-md shadow-indigo-500/20 transition-all cursor-pointer"
              >
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

      </GlassCard>
    </div>
  );
};

export default AIAssistantView;
