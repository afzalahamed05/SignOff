from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket import manager

router = APIRouter(tags=["websockets"])

@router.websocket("/ws/deliverables/{deliverable_id}")
async def websocket_endpoint(websocket: WebSocket, deliverable_id: int):
    await manager.connect(websocket, deliverable_id)
    try:
        while True:
            # Keep connection alive or receive messages if needed
            # For now, the server pushes updates, client can send 'ping'
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, deliverable_id)