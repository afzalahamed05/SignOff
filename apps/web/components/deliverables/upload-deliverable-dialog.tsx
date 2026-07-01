'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Upload } from 'lucide-react';
import api from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

export function UploadDeliverableDialog({ workspaceId, projectId, milestoneId }: { workspaceId: string, projectId: string, milestoneId: string }) {
  const [open, setOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      // 1. Get Presigned URL
      const { data: presignedData } = await api.get(`/workspaces/${workspaceId}/storage/presigned-url`, { params: { filename: file.name } });

      // 2. Upload directly to Supabase
      const uploadResponse = await fetch(presignedData.url, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${presignedData.token}`, 'Content-Type': file.type },
        body: file,
      });
      if (!uploadResponse.ok) throw new Error('Storage upload failed');

      // 3. Register in Backend
      await api.post(`/workspaces/${workspaceId}/projects/${projectId}/milestones/${milestoneId}/deliverables`, {
        file_name: file.name, file_type: file.type, file_size: file.size, storage_path: presignedData.file_path,
      });

      toast.success('File uploaded');
      queryClient.invalidateQueries({ queryKey: ['deliverables', workspaceId, projectId, milestoneId] });
      setOpen(false);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Upload failed';
      toast.error(message);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild><Button className="w-full md:w-auto"><Upload className="mr-2 h-4 w-4" /> Upload Deliverable</Button></DialogTrigger>
      <DialogContent>
        <DialogHeader><DialogTitle>Upload New Deliverable</DialogTitle></DialogHeader>
        <input type="file" ref={fileInputRef} onChange={handleUpload} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90" disabled={isUploading} />
        {isUploading && <p className="text-sm text-gray-500">Uploading directly to secure storage...</p>}
      </DialogContent>
    </Dialog>
  );
}