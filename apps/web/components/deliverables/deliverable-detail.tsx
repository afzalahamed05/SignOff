'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Download, FileText } from 'lucide-react';
import api from '@/lib/api';
import { CanvasViewer } from './canvas-viewer';
import { CommentPanel } from './comment-panel';
import { AIPanel } from './ai-panel';
import { toast } from 'sonner';

interface Deliverable { id: number; file_name: string; file_type: string; storage_path: string; status: string; }
interface Comment { id: number; content: string; user_name: string; created_at: string; x_coord: number | null; y_coord: number | null; replies: Comment[]; }

interface AIResult { action_items?: Array<{ priority: string; category: string; action: string; resolved_contradictions: string | null }> }

export function DeliverableDetail({ deliverable, comments, workspaceId, projectId, milestoneId, aiResult, setAiResult }: {
  deliverable: Deliverable; comments: Comment[]; workspaceId: string; projectId: string; milestoneId: string; aiResult: AIResult | null; setAiResult: (r: AIResult | null) => void;
}) {
  const [selectedCommentId, setSelectedCommentId] = useState<number | null>(null);
  const [pendingPin, setPendingPin] = useState<{ x: number; y: number } | null>(null);

  // Fetch secure image URL
  const { data: imageData } = useQuery({
    queryKey: ['image-url', deliverable.storage_path],
    queryFn: async () => (await api.get(`/workspaces/${workspaceId}/storage/download-url`, { params: { file_path: deliverable.storage_path } })).data,
    enabled: !!deliverable.storage_path,
  });

  const handleDownload = async () => {
    try {
      const { data } = await api.get(`/workspaces/${workspaceId}/storage/download-url`, { params: { file_path: deliverable.storage_path } });
      window.open(data.url, '_blank');
    } catch { toast.error('Failed to get download link'); }
  };

  const isImage = deliverable.file_type.startsWith('image/');

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gray-50 overflow-hidden">
      {/* Left: Canvas & Comments */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="p-4 border-b bg-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className="h-6 w-6 text-gray-400" />
            <div>
              <h2 className="font-semibold">{deliverable.file_name}</h2>
              <p className="text-xs text-gray-500">{deliverable.file_type} • {deliverable.status.replace('_', ' ')}</p>
            </div>
          </div>
          <Button onClick={handleDownload} variant="outline" size="sm"><Download className="mr-2 h-4 w-4" /> Download Original</Button>
        </div>

        <div className="flex-1 overflow-auto p-8 flex items-center justify-center">
          {isImage && imageData?.url ? (
            <CanvasViewer 
              imageUrl={imageData.url} 
              comments={comments} 
              selectedCommentId={selectedCommentId}
              onSelectComment={setSelectedCommentId}
              onAddPin={setPendingPin}
            />
          ) : (
            <div className="text-center p-12 bg-white rounded-lg shadow-sm">
              <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">This file type cannot be previewed inline.</p>
              <Button onClick={handleDownload}><Download className="mr-2 h-4 w-4" /> Download to Review</Button>
            </div>
          )}
        </div>
      </div>

      {/* Right: Sidebar (Comments & AI) */}
      <div className="w-96 border-l bg-white flex flex-col shadow-lg overflow-hidden">
        <div className="flex-1 overflow-hidden flex flex-col">
          <CommentPanel 
            comments={comments} 
            pendingPin={pendingPin}
            onPinCreated={() => setPendingPin(null)}
            selectedCommentId={selectedCommentId}
            onSelectComment={setSelectedCommentId}
            workspaceId={workspaceId} 
            projectId={projectId} 
            milestoneId={milestoneId} 
            deliverableId={deliverable.id.toString()} 
          />
        </div>
        <div className="h-1/3 border-t flex flex-col overflow-hidden">
          <AIPanel 
            workspaceId={workspaceId} 
            projectId={projectId} 
            milestoneId={milestoneId} 
            deliverableId={deliverable.id.toString()} 
            aiResult={aiResult} 
            setAiResult={setAiResult} 
          />
        </div>
      </div>
    </div>
  );
}