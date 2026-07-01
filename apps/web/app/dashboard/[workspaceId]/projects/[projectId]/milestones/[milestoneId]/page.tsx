'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { useParams } from 'next/navigation';
import { DeliverableList } from '@/components/deliverables/deliverable-list';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

export default function MilestoneDeliverablesPage() {
  const params = useParams();
  const { workspaceId, projectId, milestoneId } = params as { workspaceId: string, projectId: string, milestoneId: string };

  const { data: deliverables, isLoading } = useQuery({
    queryKey: ['deliverables', workspaceId, projectId, milestoneId],
    queryFn: async () => (await api.get(`/workspaces/${workspaceId}/projects/${projectId}/milestones/${milestoneId}/deliverables`)).data,
  });

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <Link href={`/dashboard/${workspaceId}/projects/${projectId}`}><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
        <h1 className="text-3xl font-bold">Deliverables</h1>
      </div>
      {isLoading ? <p className="text-gray-500">Loading...</p> : <DeliverableList deliverables={deliverables || []} workspaceId={workspaceId} projectId={projectId} milestoneId={milestoneId} />}
    </div>
  );
}