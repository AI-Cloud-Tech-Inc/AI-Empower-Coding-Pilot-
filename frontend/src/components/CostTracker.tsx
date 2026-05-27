import { useCallback } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useApi } from '../hooks/useApi';
import { getCostReport } from '../services/api';

const COST_TREND = [
  { day: 'Mon', cost: 0.12, tokens: 3200 },
  { day: 'Tue', cost: 0.28, tokens: 7400 },
  { day: 'Wed', cost: 0.15, tokens: 4100 },
  { day: 'Thu', cost: 0.42, tokens: 11200 },
  { day: 'Fri', cost: 0.31, tokens: 8300 },
  { day: 'Sat', cost: 0.08, tokens: 2100 },
  { day: 'Sun', cost: 0.05, tokens: 1300 },
];

export default function CostTracker() {
  const { data: report, loading } = useApi(useCallback(() => getCostReport(), []));

  if (loading) return <p className="text-gray-500">Loading cost report...</p>;

  const usedPct = report?.budget_used_pct ?? 0;

  return (
    <div className="space-y-8 animate-fadeIn">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Cost Tracker</h2>
        <p className="text-gray-500 mt-1">Token budgeting and cost optimization dashboard</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Total Tokens</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {(report?.total_tokens ?? 0).toLocaleString()}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Total Cost</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            ${(report?.total_cost_usd ?? 0).toFixed(4)}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Budget Left</p>
          <p className="text-2xl font-bold text-green-600 mt-1">
            ${(report?.budget_remaining_usd ?? 0).toFixed(2)}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Records</p>
          <p className="text-2xl font-bold text-purple-600 mt-1">{report?.total_records ?? 0}</p>
        </div>
      </div>

      {/* Budget bar */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">Budget Usage</h3>
          <span className="text-sm text-gray-500">{usedPct.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-700 ${
              usedPct > 80 ? 'bg-red-500' : usedPct > 50 ? 'bg-yellow-500' : 'bg-gradient-to-r from-blue-500 to-purple-500'
            }`}
            style={{ width: `${Math.min(usedPct, 100)}%` }}
          />
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-400">
          <span>$0</span>
          <span>${(report?.budget_usd ?? 50).toFixed(0)}</span>
        </div>
        {report?.alert_triggered && (
          <p className="mt-2 text-sm text-amber-600 font-medium animate-pulse">
            Budget alert threshold reached
          </p>
        )}
      </div>

      {/* Cost Trend Chart */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Trend (7-Day)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={COST_TREND}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="day" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} tickFormatter={(v: number) => `$${v}`} />
            <Tooltip
              contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
              formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Cost']}
            />
            <defs>
              <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="cost"
              stroke="#6366f1"
              strokeWidth={2}
              fill="url(#costGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {report?.recommendations && report.recommendations.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
          <div className="space-y-2">
            {report.recommendations.map((r, i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg border border-amber-100">
                <span className="text-amber-500 font-bold">!</span>
                <p className="text-sm text-gray-700">{r}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
