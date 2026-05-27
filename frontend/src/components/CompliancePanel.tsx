import { useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { getCompliance } from '../services/api';

const FRAMEWORK_INFO: Record<string, { label: string; color: string }> = {
  hipaa: { label: 'HIPAA', color: 'blue' },
  pci: { label: 'PCI-DSS', color: 'purple' },
  soc2: { label: 'SOC 2', color: 'indigo' },
  gdpr: { label: 'GDPR', color: 'green' },
};

export default function CompliancePanel() {
  const { data: report, loading } = useApi(useCallback(() => getCompliance(), []));

  if (loading) return <p className="text-gray-500">Loading compliance report...</p>;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Compliance</h2>
        <p className="text-gray-500 mt-1">Enterprise compliance framework — HIPAA / PCI-DSS / SOC 2 / GDPR</p>
      </div>

      {/* Overall status */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-3">
          <div
            className={`w-4 h-4 rounded-full ${report?.compliant ? 'bg-green-500' : 'bg-red-500'}`}
          />
          <span className="text-lg font-semibold text-gray-900">
            {report?.compliant ? 'All Compliant' : 'Violations Found'}
          </span>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          {report?.total_violations ?? 0} violation(s) across 4 frameworks
        </p>
      </div>

      {/* Framework cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(FRAMEWORK_INFO).map(([key, { label, color }]) => {
          const data = report?.[key as keyof typeof report] as Record<string, unknown> | undefined;
          const compliant = (data?.compliant as boolean) ?? true;
          const violations = (data?.violations as unknown[]) ?? [];

          return (
            <div key={key} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <h3 className={`font-semibold text-${color}-700`}>{label}</h3>
                <span className={`w-3 h-3 rounded-full ${compliant ? 'bg-green-500' : 'bg-red-500'}`} />
              </div>
              <p className={`text-lg font-bold ${compliant ? 'text-green-600' : 'text-red-600'}`}>
                {compliant ? 'Compliant' : `${violations.length} Violation(s)`}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {(
                  (data?.controls_checked as unknown[])
                  ?? (data?.requirements_checked as unknown[])
                  ?? (data?.criteria_checked as unknown[])
                  ?? (data?.articles_checked as unknown[])
                  ?? []
                ).length} controls checked
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
