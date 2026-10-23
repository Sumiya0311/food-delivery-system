import asyncio
import json
import websockets


async def track_order():
    uri = "ws://127.0.0.1:8000/ws/orders/8"

    async with websockets.connect(uri) as websocket:
        print("Connected! Waiting for order updates...")

        while True:
            message = await websocket.recv()
            print("Live update:", json.loads(message))


asyncio.run(track_order())