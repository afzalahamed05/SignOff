import asyncio
import websockets
import json
import requests

async def test_ws():
    # 1. Connect to WS
    uri = "ws://localhost:8000/ws/deliverables/1"
    async with websockets.connect(uri) as websocket:
        print("Connected to WS. Waiting for events... (5s timeout)")
        
        # 2. Trigger an API event (Create a comment) in another thread/process
        # For this test, assume deliverable 1 exists in workspace 1, project 1, milestone 1
        # You would normally do this via Swagger UI simultaneously
        
        try:
            # Wait 1 second to see if we get the ping/pong or an event
            response = await asyncio.wait_for(websocket.recv(), timeout=20.0)
            data = json.loads(response)
            print(f"RECEIVED: {data}")
        except asyncio.TimeoutError:
            print("No event received in 20 seconds. (Did you trigger a comment creation?)")

if __name__ == "__main__":
    asyncio.run(test_ws())