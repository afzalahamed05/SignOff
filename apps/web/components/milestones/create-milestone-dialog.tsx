'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Plus } from 'lucide-react';
import api from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

const schema = z.object({
  name: z.string().min(3, 'Name is required'),
  description: z.string().optional(),
  amount: z.string().optional(),
  due_date: z.string().optional(),
});

type FormValues = {
  name: string;
  description?: string;
  amount?: string;
  due_date?: string;
};

export function CreateMilestoneDialog({ workspaceId, projectId }: { workspaceId: string, projectId: string }) {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { name: '', description: '', amount: '0', due_date: '' } });

  const onSubmit = async (data: FormValues) => {
    try {
      const payload = {
        ...data,
        amount: Number(data.amount) || 0,
        due_date: data.due_date || null,
      };
      await api.post(`/workspaces/${workspaceId}/projects/${projectId}/milestones`, payload);
      toast.success('Milestone created');
      queryClient.invalidateQueries({ queryKey: ['milestones', workspaceId, projectId] });
      setOpen(false);
      form.reset();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(detail || 'Failed');
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild><Button className="w-full md:w-auto"><Plus className="mr-2 h-4 w-4" /> Add Milestone</Button></DialogTrigger>
      <DialogContent>
        <DialogHeader><DialogTitle>Add New Milestone</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="name" render={({ field }) => (<FormItem><FormLabel>Name</FormLabel><FormControl><Input placeholder="Initial Concepts" {...field} /></FormControl><FormMessage /></FormItem>)} />
            <FormField control={form.control} name="description" render={({ field }) => (<FormItem><FormLabel>Description</FormLabel><FormControl><Input placeholder="3 distinct logo directions" {...field} /></FormControl><FormMessage /></FormItem>)} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="amount" render={({ field }) => (<FormItem><FormLabel>Amount ($)</FormLabel><FormControl><Input type="number" step="0.01" {...field} /></FormControl><FormMessage /></FormItem>)} />
              <FormField control={form.control} name="due_date" render={({ field }) => (<FormItem><FormLabel>Due Date</FormLabel><FormControl><Input type="date" {...field} /></FormControl><FormMessage /></FormItem>)} />
            </div>
            <Button type="submit" className="w-full">Create Milestone</Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}