'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sparkles, Loader2, AlertCircle, CheckCircle2, ArrowUp, ArrowDown, Minus } from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

interface ActionItem { priority: string; category: string; action: string; resolved_contradictions: string | null; }
interface AIResult { action_items?: ActionItem[] }

export function AIPanel({ workspaceId, projectId, milestoneId, deliverableId, aiResult, setAiResult }: {
  workspaceId: string; projectId: string; milestoneId: string; deliverableId: string; aiResult: AIResult | null; setAiResult: (r: AIResult | null) => void;
}) {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSynthesize = async () => {
    setIsProcessing(true);
    setAiResult(null);
    try {
      await api.post(`/workspaces/${workspaceId}/projects/${projectId}/milestones/${milestoneId}/deliverables/${deliverableId}/ai/synthesize`);
      toast.success('AI is analyzing the feedback...');
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(detail || 'Failed to start AI');
      setIsProcessing(false);
    }
  };

  // Reset processing state when result arrives
  if (aiResult && isProcessing) setIsProcessing(false);

  const getPriorityIcon = (priority: string) => {
    if (priority === 'High') return <ArrowUp className="h-4 w-4 text-red-500" />;
    if (priority === 'Medium') return <Minus className="h-4 w-4 text-yellow-500" />;
    return <ArrowDown className="h-4 w-4 text-green-500" />;
  };

  return (
    <Card className="h-full border-none shadow-none rounded-none flex flex-col">
      <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50 border-b">
        <CardTitle className="flex items-center gap-2 text-lg"><Sparkles className="h-5 w-5 text-purple-600" /> AI Synthesizer</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto p-4 space-y-4">
        {!aiResult && !isProcessing && (
          <div className="text-center py-8 space-y-4">
            <p className="text-sm text-gray-600">Let the AI read through all the feedback threads and generate a clean, prioritized action list for the design team.</p>
            <Button onClick={handleSynthesize} className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
              <Sparkles className="mr-2 h-4 w-4" /> Synthesize Feedback
            </Button>
          </div>
        )}

        {isProcessing && (
          <div className="text-center py-8 space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-purple-600 mx-auto" />
            <p className="text-sm text-gray-600">Local AI is analyzing the discussion threads...</p>
          </div>
        )}

        {aiResult?.action_items && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-green-600 bg-green-50 p-2 rounded-md">
              <CheckCircle2 className="h-4 w-4" />
              <span className="text-sm font-medium">Synthesis Complete</span>
            </div>
            {aiResult.action_items.map((item: ActionItem, idx: number) => (
              <div key={idx} className="border rounded-lg p-3 space-y-2 hover:shadow-sm transition-shadow">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500 uppercase">{item.category}</span>
                  <div className="flex items-center gap-1">{getPriorityIcon(item.priority)}<span className="text-xs font-medium">{item.priority}</span></div>
                </div>
                <p className="text-sm font-medium">{item.action}</p>
                {item.resolved_contradictions && (
                  <div className="flex items-start gap-1 text-xs text-blue-600 bg-blue-50 p-2 rounded">
                    <AlertCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    <span>{item.resolved_contradictions}</span>
                  </div>
                )}
              </div>
            ))}
            <Button variant="outline" className="w-full mt-4" onClick={() => setAiResult(null)}>Run Again</Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}