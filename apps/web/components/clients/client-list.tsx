'use client';

import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { CreateClientDialog } from './create-client-dialog';

interface Client { id: number; name: string; email: string; company: string | null; }

export function ClientList({ clients, workspaceId }: { clients: Client[], workspaceId: string }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <CreateClientDialog workspaceId={workspaceId} />
      {clients.map((client) => (
        <Card key={client.id} className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle>{client.name}</CardTitle>
            <CardDescription>{client.company || 'No company'}</CardDescription>
            <p className="text-sm text-gray-500 mt-2">{client.email}</p>
          </CardHeader>
        </Card>
      ))}
    </div>
  );
}