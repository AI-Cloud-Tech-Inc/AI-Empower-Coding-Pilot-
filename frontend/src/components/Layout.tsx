import type { ReactNode } from 'react';

interface LayoutProps {
  sidebar: ReactNode;
  children: ReactNode;
}

export default function Layout({ sidebar, children }: LayoutProps) {
  return (
    <div className="flex h-screen">
      <aside className="w-64 bg-gray-900 text-white flex-shrink-0">{sidebar}</aside>
      <main className="flex-1 overflow-auto bg-gray-50 p-6">{children}</main>
    </div>
  );
}
