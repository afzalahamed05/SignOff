'use client';

import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { UploadDeliverableDialog } from './upload-deliverable-dialog';

interface Deliverable { id: number; version: number; file_name: string; file_type: string; status: string; }

export function DeliverableList({ deliverables, workspaceId, projectId, milestoneId }: { deliverables: Deliverable[], workspaceId: string, projectId: string, milestoneId: string }) {
  return (
    <div className="space-y-4">
      <UploadDeliverableDialog workspaceId={workspaceId} projectId={projectId} milestoneId={milestoneId} />
      {deliverables.map((d) => (
        <Link key={d.id} href={`/dashboard/${workspaceId}/projects/${projectId}/milestones/${milestoneId}/deliverables/${d.id}`}>
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{d.file_name}</CardTitle>
                  <CardDescription>Version {d.version} • {d.file_type}</CardDescription>
                </div>
                <span className={`px-3 py-1 text-xs font-medium rounded-full capitalize ${
                  d.status === 'approved' ? 'bg-green-100 text-green-800' : 
                  d.status === 'in_review' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                }`}>{d.status.replace('_', ' ')}</span>
              </div>
            </CardHeader>
          </Card>
        </Link>
      ))}
    </div>
  );
}