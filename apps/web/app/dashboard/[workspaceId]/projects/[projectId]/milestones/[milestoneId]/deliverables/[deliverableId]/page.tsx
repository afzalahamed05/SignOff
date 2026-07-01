'use client';

import { useState, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { useParams } from 'next/navigation';
import { DeliverableDetail } from '@/components/deliverables/deliverable-detail';
import { useWebSocket } from '@/hooks/use-websockets';

interface DeliverableItem {
  id: number;
  file_name: string;
  file_type: string;
  storage_path: string;
  status: string;
}

interface CommentItem {
  id: number;
  content: string;
  user_name: string;
  created_at: string;
  x_coord: number | null;
  y_coord: number | null;
  replies: CommentItem[];
}

interface AIResult {
  action_items?: Array<{
    priority: string;
    category: string;
    action: string;
    resolved_contradictions: string | null;
  }>;
}

interface WSMessage {
  type: string;
  payload?: unknown;
}

export default function DeliverableReviewPage() {
  const params = useParams();
  const { workspaceId, projectId, milestoneId, deliverableId } = params as { workspaceId: string, projectId: string, milestoneId: string, deliverableId: string };
  const queryClient = useQueryClient();
  const [aiResult, setAiResult] = useState<AIResult | null>(null);

  const { data: deliverable } = useQuery<DeliverableItem | undefined>({
    queryKey: ['deliverable', deliverableId],
    queryFn: async () => {
      const all = (await api.get<DeliverableItem[]>(`/workspaces/${workspaceId}/projects/${projectId}/milestones/${milestoneId}/deliverables`)).data;
      return all.find((d) => d.id === Number(deliverableId));
    },
  });

  const { data: comments = [] } = useQuery<CommentItem[]>({
    queryKey: ['comments', deliverableId],
    queryFn: async () => (await api.get<CommentItem[]>(`/workspaces/${workspaceId}/projects/${projectId}/milestones/${milestoneId}/deliverables/${deliverableId}/comments`)).data,
  });

  const handleWSMessage = useCallback((data: WSMessage) => {
    if (data.type === 'new_comment') queryClient.invalidateQueries({ queryKey: ['comments', deliverableId] });
    if (data.type === 'ai_synthesis_completed') {
      const payload = data.payload as { result?: unknown } | undefined;
      const result = payload?.result;
      setAiResult(typeof result === 'object' && result !== null ? result as AIResult : null);
    }
  }, [deliverableId, queryClient]);

  useWebSocket(deliverableId, handleWSMessage);

  if (!deliverable) return <p className="p-8">Loading...</p>;

  return (
    <DeliverableDetail 
      deliverable={deliverable} 
      comments={comments} 
      workspaceId={workspaceId} 
      projectId={projectId} 
      milestoneId={milestoneId} 
      aiResult={aiResult} 
      setAiResult={setAiResult} 
    />
  );
}