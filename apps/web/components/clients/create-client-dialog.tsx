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
import { Plus } from 'lucide-react';
import api from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

const schema = z.object({
  name: z.string().min(2, 'Name is required'),
  email: z.string().email('Invalid email'),
  company: z.string().optional(),
});

type FormValues = {
  name: string;
  email: string;
  company?: string;
};

export function CreateClientDialog({ workspaceId }: { workspaceId: string }) {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { name: '', email: '', company: '' } });

  const onSubmit = async (data: FormValues) => {
    try {
      await api.post(`/workspaces/${workspaceId}/clients`, data);
      toast.success('Client added');
      queryClient.invalidateQueries({ queryKey: ['clients', workspaceId] });
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
          <div className="text-center"><Plus className="mx-auto h-8 w-8 text-gray-400" /><p className="mt-2 text-sm font-medium text-gray-500">Add Client</p></div>
        </Card>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader><DialogTitle>Add New Client</DialogTitle></DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="name" render={({ field }) => (<FormItem><FormLabel>Contact Name</FormLabel><FormControl><Input placeholder="Jane Doe" {...field} /></FormControl><FormMessage /></FormItem>)} />
            <FormField control={form.control} name="email" render={({ field }) => (<FormItem><FormLabel>Email</FormLabel><FormControl><Input placeholder="jane@client.com" {...field} /></FormControl><FormMessage /></FormItem>)} />
            <FormField control={form.control} name="company" render={({ field }) => (<FormItem><FormLabel>Company</FormLabel><FormControl><Input placeholder="Acme Corp" {...field} /></FormControl><FormMessage /></FormItem>)} />
            <Button type="submit" className="w-full">Add Client</Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}