from fastapi import WebSocket
from typing import Dict, Set
import redis.asyncio as redis
import json
import asyncio
from app.core.config import settings

class ConnectionManager:
    def __init__(self):
        # Map: deliverable_id -> Set of WebSockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.redis_client: redis.Redis = redis.from_url(settings.REDIS_URL)

    async def connect(self, websocket: WebSocket, deliverable_id: int):
        await websocket.accept()
        if deliverable_id not in self.active_connections:
            self.active_connections[deliverable_id] = set()
        self.active_connections[deliverable_id].add(websocket)
        print(f"Client connected to deliverable {deliverable_id}")

    def disconnect(self, websocket: WebSocket, deliverable_id: int):
        if deliverable_id in self.active_connections:
            self.active_connections[deliverable_id].discard(websocket)
            if not self.active_connections[deliverable_id]:
                del self.active_connections[deliverable_id]
        print(f"Client disconnected from deliverable {deliverable_id}")

    async def broadcast(self, deliverable_id: int, message: dict):
        # Publish to Redis channel so all backend instances receive it
        await self.redis_client.publish(
            f"deliverable:{deliverable_id}:events", 
            json.dumps(message)
        )

    async def start_subscriber(self):
        """Background task that listens to Redis and broadcasts to WebSockets."""
        pubsub = self.redis_client.pubsub()
        # Subscribe to all deliverable event channels
        await pubsub.psubscribe("deliverable:*:events")
        
        async for message in pubsub.listen():
            if message["type"] == "pmessage":
                try:
                    # channel format: "deliverable:{id}:events"
                    channel_parts = message["channel"].decode().split(":")
                    if len(channel_parts) >= 2:
                        deliverable_id = int(channel_parts[1])
                        data = json.loads(message["data"])
                        
                        # Broadcast to active connections for this deliverable
                        if deliverable_id in self.active_connections:
                            disconnected = []
                            for connection in self.active_connections[deliverable_id]:
                                try:
                                    await connection.send_json(data)
                                except Exception:
                                    disconnected.append(connection)
                            
                            for conn in disconnected:
                                # Find key to remove safely
                                for did, conns in self.active_connections.items():
                                    if conn in conns:
                                        conns.remove(conn)
                except Exception as e:
                    print(f"WebSocket subscriber error: {e}")

# Singleton instance
manager = ConnectionManager()