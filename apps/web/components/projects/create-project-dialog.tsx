'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus } from 'lucide-react';
import api from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

const schema = z.object({
  name: z.string().min(3, 'Name is required'),
  description: z.string().optional(),
  client_id: z.string().optional(),
});

type FormValues = {
  name: string;
  description?: string;
  client_id?: string;
};

interface Client { id: number; name: string; }

export function CreateProjectDialog({ workspaceId, clients }: { workspaceId: string, clients: Client[] }) {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { name: '', description: '', client_id: 'none' } });

  const onSubmit = async (data: FormValues) => {
    try {
      const payload = {
        ...data,
        description: data.description || undefined,
        client_id: data.client_id && data.client_id !== 'none' ? Number(data.client_id) : undefined,
      };
      await api.post(`/workspaces/${workspaceId}/projects`, payload);
      toast.success('Project created');
      queryClient.invalidateQueries({ queryKey: ['projects', workspaceId] });
      setOpen(false);
      form.reset();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(detail || 'Failed');
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Card className="border-dashed border-2 flex items-center justify-center h-40 hover:bg-gray-50 cursor-pointer transition-colors">
          <div className="text-center"><Plus className="mx-auto h-8 w-8 text-gray-400" /><p className="mt-2 text-sm font-medium text-gray-500">New Project</p></div>
        </Card>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader><DialogTitle>Create New Project</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="name" render={({ field }) => (
              <FormItem><FormLabel>Project Name</FormLabel><FormControl><Input placeholder="Website Redesign" {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="description" render={({ field }) => (
              <FormItem><FormLabel>Description</FormLabel><FormControl><Input placeholder="Brief overview..." {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="client_id" render={({ field }) => (
              <FormItem>
                <FormLabel>Client</FormLabel>
                <Select onValueChange={field.onChange} value={field.value ?? 'none'}>
                  <FormControl><SelectTrigger><SelectValue placeholder="Select a client" /></SelectTrigger></FormControl>
                  <SelectContent>
                    <SelectItem value="none">No Client</SelectItem>
                    {clients.map(c => <SelectItem key={c.id} value={c.id.toString()}>{c.name}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <Button type="submit" className="w-full">Create Project</Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}