import { useCallback, useEffect, useState } from 'react';
import { useApi } from '../hooks/useApi';
import { listAgents } from '../services/api';

const ROLE_CONFIG: Record<string, { color: string; bg: string; desc: string; icon: string }> = {
  architect: { color: 'text-purple-700', bg: 'bg-purple-100', desc: 'System design & architecture', icon: '\u{1F3D7}' },
  coder: { color: 'text-blue-700', bg: 'bg-blue-100', desc: 'Code generation & implementation', icon: '\u{1F4BB}' },
  tester: { color: 'text-green-700', bg: 'bg-green-100', desc: 'Test generation & execution', icon: '\u{1F9EA}' },
  security: { color: 'text-red-700', bg: 'bg-red-100', desc: 'SAST scanning & vulnerability detection', icon: '\u{1F6E1}' },
  docs: { color: 'text-amber-700', bg: 'bg-amber-100', desc: 'Auto-documentation generation', icon: '\u{1F4DD}' },
  reviewer: { color: 'text-indigo-700', bg: 'bg-indigo-100', desc: 'Code review & quality checks', icon: '\u{1F50D}' },
};

export default function AgentStatus() {
  const { data: agents, loading, refetch } = useApi(useCallback(() => listAgents(), []));
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    if (!autoRefresh) return;
    const timer = setInterval(refetch, 5000);
    return () => clearInterval(timer);
  }, [autoRefresh, refetch]);

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Agent Status</h2>
          <p className="text-gray-500 mt-1">6-agent parallel orchestration system — AutoGen group chat</p>
        </div>
        <button
          onClick={() => setAutoRefresh(!autoRefresh)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            autoRefresh
              ? 'bg-green-100 text-green-700 border border-green-200'
              : 'bg-gray-100 text-gray-600 border border-gray-200 hover:bg-gray-200'
          }`}
        >
          {autoRefresh ? 'Live' : 'Auto-Refresh Off'}
        </button>
      </div>

      {loading && <p className="text-gray-500">Loading agents...</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {agents?.map((agent) => {
          const config = ROLE_CONFIG[agent.role] ?? { color: 'text-gray-700', bg: 'bg-gray-100', desc: '', icon: '\u2699' };
          return (
            <div
              key={agent.agent_id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{config.icon}</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.color}`}>
                    {agent.role.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-xs text-gray-500 capitalize">{agent.status}</span>
                </div>
              </div>
              <p className="text-sm text-gray-600">{config.desc}</p>
              <div className="flex items-center justify-between mt-3">
                <p className="text-xs text-gray-400 font-mono">{agent.agent_id.slice(0, 16)}...</p>
                <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse" style={{ width: '100%' }} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Orchestration pipeline */}
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-6 shadow-lg">
        <h3 className="text-white font-semibold mb-4">AutoGen Group Chat Orchestration</h3>
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {['Architect', 'Coder', 'Tester', 'Security', 'Docs', 'Reviewer'].map((name, i) => (
            <div key={name} className="flex items-center gap-2 flex-shrink-0">
              <div className="px-3 py-1.5 bg-white/10 rounded-lg text-sm text-gray-200 border border-white/10">
                {name}
              </div>
              {i < 5 && (
                <svg className="w-4 h-4 text-gray-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              )}
            </div>
          ))}
        </div>
        <p className="text-gray-400 text-sm mt-3">
          Stage 1: Architect (sequential) &rarr; Stage 2: Coder &rarr; Stage 3: Tester + Security (parallel) &rarr; Stage 4: Docs + Reviewer (parallel)
        </p>
      </div>
    </div>
  );
}
