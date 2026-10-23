from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket_manager import manager

router = APIRouter(
    prefix="/ws",
    tags=["Real-Time Order Tracking"]
)


@router.websocket("/orders/{order_id}")
async def track_order(
    websocket: WebSocket,
    order_id: int
):
    await manager.connect(order_id, websocket)

    try:
        await websocket.send_json({
            "event": "connected",
            "order_id": order_id,
            "message": "Connected to real-time order tracking"
        })

        while True:
            # Keep the connection alive while waiting for messages.
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(order_id, websocket)

    except Exception:
        manager.disconnect(order_id, websocket)