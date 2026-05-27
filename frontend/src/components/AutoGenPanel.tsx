import { useCallback, useState } from 'react';
import { useApi } from '../hooks/useApi';
import { generateAll, getAutoGenCapabilities } from '../services/api';
import type { AutoGenResult } from '../types';

export default function AutoGenPanel() {
  const { data: caps } = useApi(useCallback(() => getAutoGenCapabilities(), []));
  const [projectName, setProjectName] = useState('');
  const [result, setResult] = useState<AutoGenResult | null>(null);
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    if (!projectName.trim()) return;
    setGenerating(true);
    try {
      const arch = {
        components: [
          { name: 'api_layer', type: 'service', description: 'REST API' },
          { name: 'frontend', type: 'application', description: 'Web UI' },
          { name: 'database', type: 'infrastructure', description: 'Data store' },
        ],
        tech_stack: {
          frameworks: ['FastAPI', 'React'],
          databases: ['PostgreSQL'],
          languages: ['Python', 'TypeScript'],
          infrastructure: ['Docker', 'Terraform'],
        },
      };
      const res = await generateAll(arch, projectName);
      setResult(res);
    } finally {
      setGenerating(false);
    }
  };

  const engines = [
    { key: 'scaffolding', label: 'Project Scaffolding', color: 'blue' },
    { key: 'cicd', label: 'CI/CD Pipelines', color: 'green' },
    { key: 'docker', label: 'Docker Configs', color: 'purple' },
    { key: 'terraform', label: 'Terraform IaC', color: 'orange' },
  ] as const;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Auto-Generation</h2>
        <p className="text-gray-500 mt-1">Generate scaffolding, CI/CD, Docker, and Terraform automatically</p>
      </div>

      {/* Capabilities */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {caps?.engines.map((engine) => (
          <div key={engine.name} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-gray-900 capitalize">{engine.name}</h3>
            <p className="text-xs text-gray-500 mt-1">{engine.description}</p>
            <div className="mt-3 flex flex-wrap gap-1">
              {(engine.templates ?? engine.platforms ?? engine.runtimes ?? engine.providers ?? []).map((t) => (
                <span key={t} className="px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600">
                  {t}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Generator */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Generate Project Files</h3>
        <div className="flex gap-3">
          <input
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="Project name (e.g., my-app)"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none text-sm"
          />
          <button
            onClick={handleGenerate}
            disabled={generating || !projectName.trim()}
            className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 font-medium text-sm transition-all"
          >
            {generating ? 'Generating...' : 'Generate All'}
          </button>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Generated Files</h3>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
              {result.total_files_generated} files
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {engines.map(({ key, label, color }) => {
              const data = result[key] as { files: string[]; count: number };
              return (
                <div key={key} className="border border-gray-200 rounded-lg p-4">
                  <h4 className={`font-medium text-${color}-700 mb-2`}>{label}</h4>
                  <p className="text-sm text-gray-500 mb-2">{data.count} files generated</p>
                  <div className="space-y-1">
                    {data.files.map((f) => (
                      <p key={f} className="text-xs font-mono text-gray-600 bg-gray-50 px-2 py-1 rounded">
                        {f}
                      </p>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
