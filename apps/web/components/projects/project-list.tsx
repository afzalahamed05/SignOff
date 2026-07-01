'use client';

import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { CreateProjectDialog } from './create-project-dialog';

interface Project { id: number; name: string; description: string | null; status: string; client_id: number | null; }
interface Client { id: number; name: string; }

export function ProjectList({ projects, clients, workspaceId }: { projects: Project[], clients: Client[], workspaceId: string }) {
  const getClientName = (clientId: number | null) => clientId ? clients.find(c => c.id === clientId)?.name || 'Unknown' : 'No Client';

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <CreateProjectDialog workspaceId={workspaceId} clients={clients} />
      {projects.map((project) => (
        <Link key={project.id} href={`/dashboard/${workspaceId}/projects/${project.id}`}>
          <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle>{project.name}</CardTitle>
                <span className={`px-2 py-1 text-xs rounded-full capitalize ${project.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                  {project.status}
                </span>
              </div>
              <CardDescription>{getClientName(project.client_id)}</CardDescription>
              {project.description && <p className="text-sm text-gray-600 mt-2 line-clamp-2">{project.description}</p>}
            </CardHeader>
          </Card>
        </Link>
      ))}
    </div>
  );
}