type Page = 'dashboard' | 'projects' | 'agents' | 'compliance' | 'audit' | 'cost';

interface SidebarProps {
  current: Page;
  onNavigate: (page: Page) => void;
}

const NAV_ITEMS: { page: Page; label: string }[] = [
  { page: 'dashboard', label: 'Dashboard' },
  { page: 'projects', label: 'Projects' },
  { page: 'agents', label: 'Agents' },
  { page: 'compliance', label: 'Compliance' },
  { page: 'audit', label: 'Audit Log' },
  { page: 'cost', label: 'Cost Tracker' },
];

export default function Sidebar({ current, onNavigate }: SidebarProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-lg font-bold">AI-Empower</h1>
        <p className="text-xs text-gray-400">Coding Pilot</p>
      </div>
      <nav className="flex-1 py-4">
        {NAV_ITEMS.map(({ page, label }) => (
          <button
            key={page}
            onClick={() => onNavigate(page)}
            className={`w-full text-left px-4 py-2 text-sm transition-colors ${
              current === page
                ? 'bg-primary-600 text-white'
                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
            }`}
          >
            {label}
          </button>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-700 text-xs text-gray-500">v1.0.0</div>
    </div>
  );
}
