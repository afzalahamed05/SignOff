'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { useParams } from 'next/navigation';
import { ClientList } from '@/components/clients/client-list';

export default function ClientsPage() {
  const params = useParams();
  const workspaceId = params.workspaceId as string;

  const { data: clients, isLoading } = useQuery({
    queryKey: ['clients', workspaceId],
    queryFn: async () => (await api.get(`/workspaces/${workspaceId}/clients`)).data,
  });

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Clients</h1>
      {isLoading ? <p className="text-gray-500">Loading clients...</p> : <ClientList clients={clients || []} workspaceId={workspaceId} />}
    </div>
  );
}