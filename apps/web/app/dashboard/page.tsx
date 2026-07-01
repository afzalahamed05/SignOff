'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { WorkspaceList } from '@/components/workspaces/workspace-list';

export default function DashboardPage() {
  const { data: workspaces, isLoading } = useQuery({
    queryKey: ['workspaces'],
    queryFn: async () => {
      const res = await api.get('/workspaces');
      return res.data;
    },
  });

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Your Workspaces</h1>
      {isLoading ? (
        <p className="text-gray-500">Loading workspaces...</p>
      ) : (
        <WorkspaceList workspaces={workspaces || []} />
      )}
    </div>
  );
}