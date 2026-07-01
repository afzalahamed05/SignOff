'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import api from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { MessageSquare, MapPin } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Comment { id: number; content: string; user_name: string; created_at: string; x_coord: number | null; y_coord: number | null; replies: Comment[]; }

function CommentThread({ comment, depth = 0, isSelected, onSelect }: { comment: Comment, depth?: number, isSelected: boolean, onSelect: () => void }) {
  const ref = useRef<HTMLDivElement>(null);

  // Auto-scroll to the comment when its pin is clicked on the canvas
  useEffect(() => {
    if (isSelected && ref.current) {
      ref.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [isSelected]);

  return (
    <div ref={ref} className={cn("p-3 rounded-lg transition-colors cursor-pointer", isSelected ? "bg-primary/5 border border-primary/20" : "hover:bg-gray-50")} onClick={onSelect}>
      <div className={depth > 0 ? "ml-4 border-l-2 border-gray-100 pl-3" : ""}>
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-semibold text-gray-800">{comment.user_name}</span>
          <div className="flex items-center gap-2">
            {comment.x_coord !== null && <MapPin className="h-3 w-3 text-primary" />}
            <span className="text-xs text-gray-400">{new Date(comment.created_at).toLocaleTimeString()}</span>
          </div>
        </div>
        <p className="text-sm text-gray-700 whitespace-pre-wrap">{comment.content}</p>
      </div>
      {comment.replies?.map(reply => <CommentThread key={reply.id} comment={reply} depth={depth + 1} isSelected={false} onSelect={onSelect} />)}
    </div>
  );
}

export function CommentPanel({ comments, pendingPin, onPinCreated, selectedCommentId, onSelectComment, workspaceId, projectId, milestoneId, deliverableId }: {
  comments: Comment[]; pendingPin: {x: number, y: number} | null; onPinCreated: () => void; selectedCommentId: number | null; onSelectComment: (id: number | null) => void; workspaceId: string; projectId: string; milestoneId: string; deliverableId: string;
}) {
  const [newComment, setNewComment] = useState('');
  const queryClient = useQueryClient();

  const handleSubmit = async (e: React.FormEvent, parentId?: number) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    try {
      const payload: { content: string; x_coord?: number; y_coord?: number; parent_id?: number } = { content: newComment };
      
      // If this is a new top-level comment and we have a pending pin, attach the coordinates
      if (!parentId && pendingPin) {
        payload.x_coord = pendingPin.x;
        payload.y_coord = pendingPin.y;
      }
      if (parentId) payload.parent_id = parentId;

      await api.post(`/workspaces/${workspaceId}/projects/${projectId}/milestones/${milestoneId}/deliverables/${deliverableId}/comments`, payload);
      setNewComment('');
      if (!parentId) onPinCreated(); // Clear the pending pin state
      queryClient.invalidateQueries({ queryKey: ['comments', deliverableId] });
    } catch { toast.error('Failed to post comment'); }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <h3 className="font-semibold flex items-center gap-2"><MessageSquare className="h-4 w-4" /> Feedback Thread</h3>
      </div>
      
      <div className="flex-1 overflow-auto p-4 space-y-2">
        {/* Inline prompt when a new pin is dropped on the canvas */}
        {pendingPin && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
            <p className="text-xs font-semibold text-blue-700 mb-2 flex items-center gap-1"><MapPin className="h-3 w-3" /> New Pin Dropped</p>
            <form onSubmit={(e) => handleSubmit(e)} className="space-y-2">
              <textarea 
                value={newComment} 
                onChange={e => setNewComment(e.target.value)} 
                placeholder="What needs to change here?" 
                className="w-full p-2 text-sm border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={2}
                autoFocus
              />
              <div className="flex gap-2">
                <Button type="submit" size="sm" className="flex-1">Save Pin</Button>
                <Button type="button" variant="ghost" size="sm" onClick={onPinCreated}>Cancel</Button>
              </div>
            </form>
          </div>
        )}

        {comments.length === 0 && !pendingPin ? (
          <p className="text-sm text-gray-500 text-center py-8">Click anywhere on the image to drop a pin and leave feedback.</p>
        ) : (
          comments.map(c => (
            <div key={c.id}>
              <CommentThread 
                comment={c} 
                isSelected={selectedCommentId === c.id} 
                onSelect={() => onSelectComment(selectedCommentId === c.id ? null : c.id)} 
              />
              {/* Inline reply box when a pin/thread is selected */}
              {selectedCommentId === c.id && (
                <form onSubmit={(e) => handleSubmit(e, c.id)} className="ml-4 mt-2 flex gap-2">
                  <input 
                    value={newComment} 
                    onChange={e => setNewComment(e.target.value)} 
                    placeholder="Reply..." 
                    className="flex-1 p-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <Button type="submit" size="sm">Reply</Button>
                </form>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}