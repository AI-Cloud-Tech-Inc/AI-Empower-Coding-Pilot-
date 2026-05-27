import { useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { getCostReport } from '../services/api';

export default function CostTracker() {
  const { data: report, loading } = useApi(useCallback(() => getCostReport(), []));

  if (loading) return <p className="text-gray-500">Loading cost report...</p>;

  const usedPct = report?.budget_used_pct ?? 0;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Cost Tracker</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Total Tokens</h3>
          <p className="text-2xl font-bold">{(report?.total_tokens ?? 0).toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Total Cost</h3>
          <p className="text-2xl font-bold">${(report?.total_cost_usd ?? 0).toFixed(4)}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Budget Remaining</h3>
          <p className="text-2xl font-bold">
            ${(report?.budget_remaining_usd ?? 0).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Budget bar */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold mb-3">Budget Usage</h3>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className={`h-4 rounded-full transition-all ${
              usedPct > 80 ? 'bg-red-500' : usedPct > 50 ? 'bg-yellow-500' : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(usedPct, 100)}%` }}
          />
        </div>
        <p className="text-sm text-gray-500 mt-1">{usedPct.toFixed(1)}% of budget used</p>
      </div>

      {report?.recommendations && report.recommendations.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-3">Recommendations</h3>
          <ul className="space-y-1 text-sm text-gray-700">
            {report.recommendations.map((r, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-yellow-500 mt-0.5">*</span>
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
