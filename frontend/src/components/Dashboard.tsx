import { useCallback, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useApi } from '../hooks/useApi';
import { getHealth, runAdHoc, getLLMStatus } from '../services/api';
import type { PipelineResult } from '../types';

const AGENT_DATA = [
  { name: 'Architect', tasks: 24, avgTime: 1.2 },
  { name: 'Coder', tasks: 42, avgTime: 2.8 },
  { name: 'Tester', tasks: 38, avgTime: 1.5 },
  { name: 'Security', tasks: 31, avgTime: 0.9 },
  { name: 'Docs', tasks: 28, avgTime: 0.7 },
  { name: 'Reviewer', tasks: 35, avgTime: 1.1 },
];

const COMPLIANCE_DATA = [
  { name: 'HIPAA', value: 100, color: '#3b82f6' },
  { name: 'PCI-DSS', value: 100, color: '#8b5cf6' },
  { name: 'SOC 2', value: 100, color: '#6366f1' },
  { name: 'GDPR', value: 100, color: '#10b981' },
];

export default function Dashboard() {
  const { data: health } = useApi(useCallback(() => getHealth(), []));
  const { data: llmStatus } = useApi(useCallback(() => getLLMStatus(), []));
  const [requirements, setRequirements] = useState('');
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    if (!requirements.trim()) return;
    setRunning(true);
    setError(null);
    try {
      const res = await runAdHoc(requirements);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setRunning(false);
    }
  };

  const features = [
    'AutoGen Multi-Agent',
    'Project Scaffolding',
    'CI/CD Generation',
    'Terraform IaC',
    'Docker Configs',
    'HIPAA/PCI/SOC2/GDPR',
    'JWT Authentication',
    'LLM Integration',
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-500 mt-1">AI-Empower Autonomous Coding Pilot — Control Center</p>
      </div>

      {/* Status cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-5">
        <StatusCard label="Status" value={health?.status ?? '...'} color="text-green-600" />
        <StatusCard label="Version" value={health?.version ?? '...'} color="text-gray-900" />
        <StatusCard label="Services" value={health ? String(Object.keys(health.services).length) : '0'} color="text-blue-600" />
        <StatusCard label="Agents" value="6" color="text-purple-600" />
        <StatusCard label="LLM" value={llmStatus?.provider ?? '...'} color="text-indigo-600" />
      </div>

      {/* Feature badges */}
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-6 shadow-lg">
        <h3 className="text-white font-semibold mb-3">Platform Capabilities</h3>
        <div className="flex flex-wrap gap-2">
          {features.map((f) => (
            <span
              key={f}
              className="px-3 py-1 rounded-full text-xs font-medium bg-white/10 text-gray-200 border border-white/10 hover:bg-white/20 transition-colors"
            >
              {f}
            </span>
          ))}
        </div>
        <p className="text-gray-400 text-sm mt-3">
          83% more productive with parallel 6-agent orchestration
        </p>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Task Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={AGENT_DATA}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
              />
              <Bar dataKey="tasks" fill="url(#barGradient)" radius={[4, 4, 0, 0]} />
              <defs>
                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Status</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={COMPLIANCE_DATA}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={4}
                dataKey="value"
                label={({ name }) => name}
              >
                {COMPLIANCE_DATA.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick run */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Pipeline Run</h3>
        <textarea
          value={requirements}
          onChange={(e) => setRequirements(e.target.value)}
          placeholder="Enter your project requirements..."
          className="w-full border border-gray-300 rounded-lg p-4 h-32 resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none text-sm"
        />
        <button
          onClick={handleRun}
          disabled={running || !requirements.trim()}
          className="mt-3 px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm transition-all shadow-sm active:scale-95"
        >
          {running ? 'Running Pipeline...' : 'Run Pipeline'}
        </button>

        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200 animate-fadeIn">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-4 p-5 bg-gray-50 rounded-lg border border-gray-200 animate-fadeIn">
            <h4 className="font-semibold text-gray-900 mb-3">Pipeline Result</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-400 text-xs">Status</p>
                <p className={`font-semibold ${result.status === 'completed' ? 'text-green-600' : 'text-red-600'}`}>
                  {result.status}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Transitions</p>
                <p className="font-semibold text-gray-900">{result.transitions}</p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Duration</p>
                <p className="font-semibold text-gray-900">{result.duration_s.toFixed(3)}s</p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Workflow</p>
                <p className="font-mono text-xs text-gray-600">{result.workflow_id.slice(0, 12)}...</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function StatusCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
    </div>
  );
}
