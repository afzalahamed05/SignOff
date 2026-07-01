'use client';

import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { CreateWorkspaceDialog } from './create-workspace-dialog';

interface Workspace {
  id: number;
  name: string;
  slug: string;
}

export function WorkspaceList({ workspaces }: { workspaces: Workspace[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <CreateWorkspaceDialog />
      {workspaces.map((ws) => (
        <Link key={ws.id} href={`/dashboard/${ws.id}`}>
          <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
            <CardHeader>
              <CardTitle>{ws.name}</CardTitle>
              <CardDescription>/{ws.slug}</CardDescription>
            </CardHeader>
          </Card>
        </Link>
      ))}
    </div>
  );
}