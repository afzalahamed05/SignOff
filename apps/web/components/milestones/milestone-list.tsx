'use client';

import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CreateMilestoneDialog } from './create-milestone-dialog';
import api from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

interface Invoice { id: number; status: string; hosted_invoice_url: string | null; }
interface Milestone { id: number; name: string; description: string | null; amount: number; status: string; due_date: string | null; invoice: Invoice | null; }

export function MilestoneList({ milestones, workspaceId, projectId }: { milestones: Milestone[], workspaceId: string, projectId: string }) {
  const queryClient = useQueryClient();

  const handleGenerateInvoice = async (e: React.MouseEvent, milestoneId: number) => {
    e.preventDefault(); // Prevent navigating to the milestone detail page
    try {
      await api.post(`/workspaces/${workspaceId}/projects/${projectId}/milestones/${milestoneId}/generate-invoice`);
      toast.success('Invoice generated!');
      queryClient.invalidateQueries({ queryKey: ['milestones', workspaceId, projectId] });
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(detail || 'Failed to generate invoice');
    }
  };

  return (
    <div className="space-y-4">
      <CreateMilestoneDialog workspaceId={workspaceId} projectId={projectId} />
      {milestones.map((m) => (
        <Link key={m.id} href={`/dashboard/${workspaceId}/projects/${projectId}/milestones/${m.id}`}>
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{m.name}</CardTitle>
                  <CardDescription>{m.description || 'No description'}</CardDescription>
                </div>
                <span className={`px-3 py-1 text-xs font-medium rounded-full capitalize ${
                  m.status === 'completed' || m.status === 'approved' ? 'bg-green-100 text-green-800' : 
                  m.status === 'in_progress' || m.status === 'in_review' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                }`}>{m.status.replace('_', ' ')}</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between text-sm text-gray-600 mb-3">
                <span>Amount: ${m.amount.toLocaleString()}</span>
                <span>Due: {m.due_date ? new Date(m.due_date).toLocaleDateString() : 'No due date'}</span>
              </div>

              {/* Invoice Actions */}
              {m.invoice ? (
                <div className="pt-3 border-t flex justify-between items-center">
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                    m.invoice.status === 'paid' ? 'bg-green-100 text-green-800' : 
                    m.invoice.status === 'overdue' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    Invoice: {m.invoice.status}
                  </span>
                  {m.invoice.status !== 'paid' && m.invoice.hosted_invoice_url && (
                    <a href={m.invoice.hosted_invoice_url} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()}>
                      <Button size="sm" variant="outline">Pay Now</Button>
                    </a>
                  )}
                </div>
              ) : (
                m.status === 'completed' && (
                  <Button size="sm" className="w-full mt-2" onClick={(e) => handleGenerateInvoice(e, m.id)}>
                    Generate Invoice
                  </Button>
                )
              )}
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}