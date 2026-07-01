'use client';

import Image from 'next/image';
import { useRef } from 'react';
import { cn } from '@/lib/utils';
import { MessageCircle } from 'lucide-react';

interface Comment {
  id: number;
  x_coord: number | null;
  y_coord: number | null;
  user_name: string;
}

interface CanvasViewerProps {
  imageUrl: string;
  comments: Comment[];
  selectedCommentId: number | null;
  onSelectComment: (id: number | null) => void;
  onAddPin: (coords: { x: number; y: number }) => void;
}

export function CanvasViewer({ imageUrl, comments, selectedCommentId, onSelectComment, onAddPin }: CanvasViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  const handleImageClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    
    // Prevent dropping a new pin if the user clicked on an existing pin
    if ((e.target as HTMLElement).closest('[data-pin]')) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    onAddPin({ x, y });
    onSelectComment(null);
  };

  const handlePinClick = (e: React.MouseEvent, commentId: number) => {
    e.stopPropagation();
    onSelectComment(commentId === selectedCommentId ? null : commentId);
  };

  // Filter comments that have coordinates to render as pins
  const pinComments = comments.filter(c => c.x_coord !== null && c.y_coord !== null);

  return (
    <div 
      ref={containerRef}
      className="relative w-full max-w-4xl mx-auto bg-gray-100 rounded-lg shadow-inner overflow-hidden cursor-crosshair"
      onClick={handleImageClick}
    >
      <Image
        src={imageUrl}
        alt="Deliverable"
        width={1200}
        height={800}
        className="w-full h-auto block select-none pointer-events-none"
        draggable={false}
        unoptimized
      />
      
      {/* Render Pins */}
      {pinComments.map((comment) => (
        <button
          key={comment.id}
          data-pin
          style={{ left: `${comment.x_coord}%`, top: `${comment.y_coord}%` }}
          className={cn(
            "absolute w-8 h-8 -ml-4 -mt-4 rounded-full flex items-center justify-center text-xs font-bold shadow-lg transition-all transform hover:scale-110 z-10",
            selectedCommentId === comment.id 
              ? "bg-primary text-primary-foreground ring-4 ring-primary/20" 
              : "bg-white text-gray-800 border-2 border-primary hover:bg-primary hover:text-primary-foreground"
          )}
          onClick={(e) => handlePinClick(e, comment.id)}
          title={`Comment by ${comment.user_name}`}
        >
          <MessageCircle className="h-4 w-4" />
        </button>
      ))}
    </div>
  );
}