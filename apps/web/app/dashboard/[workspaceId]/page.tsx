'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { useParams } from 'next/navigation';
import { ProjectList } from '@/components/projects/project-list';

export default function WorkspaceProjectsPage() {
  const params = useParams();
  const workspaceId = params.workspaceId as string;

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects', workspaceId],
    queryFn: async () => (await api.get(`/workspaces/${workspaceId}/projects`)).data,
  });

  const { data: clients } = useQuery({
    queryKey: ['clients', workspaceId],
    queryFn: async () => (await api.get(`/workspaces/${workspaceId}/clients`)).data,
  });

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Projects</h1>
      {isLoading ? <p className="text-gray-500">Loading projects...</p> : <ProjectList projects={projects || []} clients={clients || []} workspaceId={workspaceId} />}
    </div>
  );
}