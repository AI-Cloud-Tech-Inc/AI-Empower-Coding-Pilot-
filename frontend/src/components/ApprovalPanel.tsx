import { useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { getApprovals } from '../services/api';

export default function ApprovalPanel() {
  const { data: report, loading } = useApi(useCallback(() => getApprovals(), []));

  if (loading) return <p className="text-gray-500">Loading approvals...</p>;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Approval Gates</h2>
        <p className="text-gray-500 mt-1">Human approval checkpoints for deployment workflows</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Total</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{report?.total_requests ?? 0}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Pending</p>
          <p className="text-2xl font-bold text-yellow-600 mt-1">{report?.pending ?? 0}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Approved</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{report?.approved ?? 0}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Rejected</p>
          <p className="text-2xl font-bold text-red-600 mt-1">{report?.rejected ?? 0}</p>
        </div>
      </div>

      {/* Available gates */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Gates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {(report?.gates ?? []).map((gate) => (
            <div key={gate} className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg">
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              <span className="text-sm font-medium text-gray-700 capitalize">
                {gate.replace(/_/g, ' ')}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Approval requests */}
      {report && report.requests.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Requests</h3>
          <div className="space-y-3">
            {report.requests.map((req, idx) => {
              const status = String(req.status ?? 'unknown');
              return (
                <div key={idx} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900 capitalize">
                      {String(req.checkpoint ?? '').replace(/_/g, ' ')}
                    </p>
                    <p className="text-xs text-gray-500">{String(req.description ?? '')}</p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      status.includes('approved')
                        ? 'bg-green-100 text-green-700'
                        : status === 'pending'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {status}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
