from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import manager

router = APIRouter()


@router.websocket("/images")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time processing updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages (optional)
            await websocket.receive_text()
            # Echo back or handle client messages if needed
            await websocket.send_json({"type": "pong", "message": "Connection alive"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
