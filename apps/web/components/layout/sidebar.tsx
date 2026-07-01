'use client';

import Link from 'next/link';
import { usePathname, useParams } from 'next/navigation';
import { cn } from '@/lib/utils';
import { LayoutDashboard, FolderKanban, Users } from 'lucide-react';

export function Sidebar() {
  const pathname = usePathname();
  const params = useParams();
  const workspaceId = params.workspaceId as string | undefined;

  const mainNav = [
    { href: '/dashboard', label: 'Workspaces', icon: LayoutDashboard },
  ];

  const workspaceNav = workspaceId ? [
    { href: `/dashboard/${workspaceId}`, label: 'Projects', icon: FolderKanban },
    { href: `/dashboard/${workspaceId}/clients`, label: 'Clients', icon: Users },
  ] : [];

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-6 border-b">
        <h1 className="text-xl font-bold text-primary">SignOff AI</h1>
      </div>
      <nav className="flex-1 p-4 space-y-6">
        <div className="space-y-2">
          {mainNav.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link key={item.href} href={item.href}
                className={cn('flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                  isActive ? 'bg-primary text-primary-foreground' : 'text-gray-600 hover:bg-gray-100'
                )}>
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </div>

        {workspaceId && (
          <div className="space-y-2 pt-4 border-t">
            <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">Workspace</p>
            {workspaceNav.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link key={item.href} href={item.href}
                  className={cn('flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive ? 'bg-primary text-primary-foreground' : 'text-gray-600 hover:bg-gray-100'
                  )}>
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        )}
      </nav>
    </div>
  );
}