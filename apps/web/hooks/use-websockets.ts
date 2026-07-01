import { useEffect, useRef } from 'react';

export interface WebSocketMessage {
  type: string;
  payload?: unknown;
}

export function useWebSocket(deliverableId: string | null, onMessage: (data: WebSocketMessage) => void) {
  const ws = useRef<WebSocket | null>(null);
  const onMessageRef = useRef(onMessage);

  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    if (!deliverableId) return;

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    ws.current = new WebSocket(`${wsUrl}/ws/deliverables/${deliverableId}`);

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage;
        onMessageRef.current(data);
      } catch (error) {
        console.error('Failed to parse WS message', error);
      }
    };

    ws.current.onerror = (e) => console.error('WS Error', e);
    ws.current.onclose = () => console.log('WS Closed');

    return () => { ws.current?.close(); };
  }, [deliverableId]);
}