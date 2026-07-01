'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { useParams } from 'next/navigation';
import { MilestoneList } from '@/components/milestones/milestone-list';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

export default function ProjectMilestonesPage() {
  const params = useParams();
  const workspaceId = params.workspaceId as string;
  const projectId = params.projectId as string;

  const { data: project } = useQuery({
    queryKey: ['project', workspaceId, projectId],
    queryFn: async () => (await api.get(`/workspaces/${workspaceId}/projects/${projectId}`)).data,
  });

  const { data: milestones, isLoading } = useQuery({
    queryKey: ['milestones', workspaceId, projectId],
    queryFn: async () => (await api.get(`/workspaces/${workspaceId}/projects/${projectId}/milestones`)).data,
  });

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <Link href={`/dashboard/${workspaceId}`}><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
        <div>
          <h1 className="text-3xl font-bold">{project?.name || 'Project'}</h1>
          <p className="text-gray-500">Milestones & Deliverables</p>
        </div>
      </div>
      {isLoading ? <p className="text-gray-500">Loading milestones...</p> : <MilestoneList milestones={milestones || []} workspaceId={workspaceId} projectId={projectId} />}
    </div>
  );
}