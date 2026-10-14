import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auto-attach authorization token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('agentx_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export interface UserResponse {
  id: string;
  email: string;
  role: string;
  nickname?: string | null;
  created_at?: string;
}

export interface GoalResponse {
  id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
}

export interface TaskResponse {
  id: string;
  goal_id: string;
  assigned_agent: string;
  input_data: any;
  status: string;
  parent_task_id?: string | null;
  dependencies?: string[];
  priority?: string;
  estimated_execution_time?: number;
  estimated_token_usage?: number;
  required_apis?: string[];
  required_tools?: string[];
  confidence_score?: number;
  expected_output?: string;
  retry_policy?: any;
}

export interface GoalDetailResponse {
  goal: GoalResponse;
  tasks: TaskResponse[];
  mission_result?: any;
}

export interface ApprovalResponse {
  id: string;
  task_id: string | null;
  agent_name: string;
  tool_name: string;
  parameters: any;
  status: string;
  created_at: string;
}

export interface PluginResponse {
  id: string;
  plugin_name: string;
  version: string;
  is_active: boolean;
  dependencies: string[];
}

export const authService = {
  async signup(email: string, password: string): Promise<UserResponse> {
    const response = await api.post<UserResponse>('/auth/signup', { email, password });
    return response.data;
  },

  async login(email: string, password: string): Promise<string> {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    const response = await api.post<{ access_token: string }>('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    const { access_token } = response.data;
    if (typeof window !== 'undefined') {
      localStorage.setItem('agentx_token', access_token);
    }
    return access_token;
  },

  async getMe(): Promise<UserResponse> {
    const response = await api.get<UserResponse>('/auth/me');
    return response.data;
  },

  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('agentx_token');
    }
  },
};

export const goalService = {
  async createGoal(title: string, description: string): Promise<GoalResponse> {
    const response = await api.post<GoalResponse>('/goals/', { title, description });
    return response.data;
  },

  async listGoals(): Promise<GoalResponse[]> {
    const response = await api.get<GoalResponse[]>('/goals');
    return response.data;
  },

  async getGoal(goalId: string): Promise<GoalDetailResponse> {
    const response = await api.get<GoalDetailResponse>(`/goals/${goalId}`);
    return response.data;
  },
};

export const approvalService = {
  async listApprovals(statusFilter: string = 'pending'): Promise<ApprovalResponse[]> {
    const response = await api.get<ApprovalResponse[]>('/approvals', {
      params: { status_filter: statusFilter },
    });
    return response.data;
  },

  async resolveApproval(approvalId: string, action: 'approved' | 'rejected'): Promise<ApprovalResponse> {
    const response = await api.post<ApprovalResponse>(`/approvals/resolve/${approvalId}`, { action });
    return response.data;
  },
};

export const workflowService = {
  async getStatus(goalId: string): Promise<{ goal_id: string; status: string }> {
    const response = await api.get<{ goal_id: string; status: string }>(`/workflows/status/${goalId}`);
    return response.data;
  },

  async pauseWorkflow(goalId: string): Promise<{ goal_id: string; status: string }> {
    const response = await api.post<{ goal_id: string; status: string }>(`/workflows/pause/${goalId}`);
    return response.data;
  },

  async resumeWorkflow(goalId: string): Promise<{ goal_id: string; status: string }> {
    const response = await api.post<{ goal_id: string; status: string }>(`/workflows/resume/${goalId}`);
    return response.data;
  },

  async cancelWorkflow(goalId: string): Promise<{ goal_id: string; status: string }> {
    const response = await api.post<{ goal_id: string; status: string }>(`/workflows/cancel/${goalId}`);
    return response.data;
  },
};

export const pluginService = {
  async listPlugins(): Promise<PluginResponse[]> {
    const response = await api.get<PluginResponse[]>('/plugins');
    return response.data;
  },

  async installPlugin(pluginName: string, version: string, dependencies: string[] = []): Promise<PluginResponse> {
    const response = await api.post<PluginResponse>('/plugins', {
      plugin_name: pluginName,
      version,
      dependencies,
    });
    return response.data;
  },

  async uninstallPlugin(pluginName: string): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>(`/plugins/${pluginName}`);
    return response.data;
  },
};

export interface UserAdminResponse {
  id: string;
  email: string;
  role: string;
  created_at: string;
}

export interface SystemMetricsResponse {
  total_users: number;
  total_goals: number;
  total_model_calls: number;
  database_type: string;
}

export interface AuditLogResponse {
  id: string;
  provider: string;
  model_name: string;
  prompt_tokens: number;
  completion_tokens: number;
  latency_ms: number;
  status: string;
  created_at: string;
}

export const adminService = {
  async listUsers(): Promise<UserAdminResponse[]> {
    const response = await api.get<UserAdminResponse[]>('/admin/users');
    return response.data;
  },

  async updateUserRole(userId: string, role: string): Promise<UserAdminResponse> {
    const response = await api.put<UserAdminResponse>(`/admin/users/${userId}/role`, { role });
    return response.data;
  },

  async getMetrics(): Promise<SystemMetricsResponse> {
    const response = await api.get<SystemMetricsResponse>('/admin/system/metrics');
    return response.data;
  },

  async getAuditLogs(): Promise<AuditLogResponse[]> {
    const response = await api.get<AuditLogResponse[]>('/admin/audit-logs');
    return response.data;
  },
};

export interface ArtifactDescriptor {
  id: string;
  name: string;
  type: string;
  download_url?: string;
  metadata?: Record<string, any>;
}

export interface ActionDescriptor {
  id: string;
  action_type: string;
  label: string;
  payload?: Record<string, any>;
}

export interface ResponseMetadata {
  streaming?: boolean;
  conversation_title?: string;
  sources?: any[];
  follow_up_questions?: string[];
}

export interface StandardChatResponse {
  conversation_id: string;
  message_id: string;
  role: string;
  content: string;
  artifacts: ArtifactDescriptor[];
  actions: ActionDescriptor[];
  status: string;
  timestamp: number;
  metadata?: ResponseMetadata;
}

export interface ChatMessage {
  message_id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  metadata?: Record<string, any>;
}

export interface ConversationHistory {
  conversation_id: string;
  title: string;
  created_at: number;
  updated_at: number;
  messages: ChatMessage[];
}

export interface ChatStreamChunk {
  event: 'assistant_stream' | 'status_update' | 'artifact_ready' | 'mission_completed';
  conversation_id: string;
  message_id: string;
  content?: string;
  status_message?: string;
  progress_percentage?: number;
}

export const chatService = {
  async sendMessage(
    message: string,
    conversationId?: string,
    preferences: string[] = []
  ): Promise<StandardChatResponse> {
    const response = await api.post<StandardChatResponse>('/chat', {
      message,
      conversation_id: conversationId,
      streaming: false,
      preferences,
    });
    return response.data;
  },

  async listHistory(): Promise<ConversationHistory[]> {
    const response = await api.get<ConversationHistory[]>('/chat/history');
    return response.data;
  },

  async getConversation(conversationId: string): Promise<ConversationHistory> {
    const response = await api.get<ConversationHistory>(`/chat/${conversationId}`);
    return response.data;
  },

  async deleteConversation(conversationId: string): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>(`/chat/${conversationId}`);
    return response.data;
  },

  async regenerateMessage(conversationId: string): Promise<StandardChatResponse> {
    const response = await api.post<StandardChatResponse>(`/chat/${conversationId}/regenerate`);
    return response.data;
  },

  streamMessage(
    message: string,
    conversationId: string | undefined,
    preferences: string[] = [],
    onChunk: (chunk: ChatStreamChunk) => void,
    onComplete?: () => void,
    onError?: (err: any) => void
  ): () => void {
    const controller = new AbortController();
    const token = typeof window !== 'undefined' ? localStorage.getItem('agentx_token') : null;

    fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        streaming: true,
        preferences,
      }),
      signal: controller.signal,
    })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error(`HTTP error ${res.status}`);
        }
        const reader = res.body?.getReader();
        if (!reader) return;
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('data:')) {
              try {
                const jsonStr = trimmed.replace('data:', '').trim();
                const chunkData: ChatStreamChunk = JSON.parse(jsonStr);
                onChunk(chunkData);
              } catch (e) {
                console.error('Error parsing SSE chunk:', e);
              }
            }
          }
        }
        if (onComplete) onComplete();
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          if (onError) onError(err);
        }
      });

    return () => controller.abort();
  },
};

