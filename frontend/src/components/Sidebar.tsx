type Page =
  | 'dashboard'
  | 'projects'
  | 'agents'
  | 'autogen'
  | 'compliance'
  | 'approvals'
  | 'audit'
  | 'cost';

interface SidebarProps {
  current: Page;
  onNavigate: (page: Page) => void;
}

const NAV_SECTIONS: { label: string; items: { page: Page; label: string; icon: string }[] }[] = [
  {
    label: 'Core',
    items: [
      { page: 'dashboard', label: 'Dashboard', icon: '\u25A0' },
      { page: 'projects', label: 'Projects', icon: '\u25B6' },
      { page: 'agents', label: 'Agents', icon: '\u2699' },
    ],
  },
  {
    label: 'Automation',
    items: [
      { page: 'autogen', label: 'Auto-Gen', icon: '\u26A1' },
      { page: 'approvals', label: 'Approvals', icon: '\u2714' },
    ],
  },
  {
    label: 'Governance',
    items: [
      { page: 'compliance', label: 'Compliance', icon: '\u2691' },
      { page: 'audit', label: 'Audit Log', icon: '\u2630' },
      { page: 'cost', label: 'Cost Tracker', icon: '\u2261' },
    ],
  },
];

export default function Sidebar({ current, onNavigate }: SidebarProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="p-5 border-b border-gray-700/50">
        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          AI-Empower
        </h1>
        <p className="text-xs text-gray-400 mt-0.5">Autonomous Coding Pilot</p>
      </div>
      <nav className="flex-1 py-3 overflow-y-auto">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label} className="mb-2">
            <p className="px-5 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-500">
              {section.label}
            </p>
            {section.items.map(({ page, label, icon }) => (
              <button
                key={page}
                onClick={() => onNavigate(page)}
                className={`w-full text-left px-5 py-2 text-sm flex items-center gap-3 transition-all duration-150 ${
                  current === page
                    ? 'bg-gradient-to-r from-blue-600/80 to-purple-600/60 text-white shadow-lg shadow-blue-500/10'
                    : 'text-gray-300 hover:bg-gray-800/60 hover:text-white'
                }`}
              >
                <span className="text-base w-5 text-center">{icon}</span>
                {label}
              </button>
            ))}
          </div>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-700/50">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-gray-500">v2.0.0 — AutoGen</span>
        </div>
      </div>
    </div>
  );
}
