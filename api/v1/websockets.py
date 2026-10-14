import json
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from loguru import logger

router = APIRouter()

class ConnectionManager:
    """Manages active WebSocket connections grouped by goal_id or conversation_id."""
    def __init__(self):
        # Maps connection_id (str) -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, socket: WebSocket, channel_id: str, role: str = "user"):
        """Accept connection and add it to the channel pool with user role context."""
        await socket.accept()
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []
        self.active_connections[channel_id].append({"socket": socket, "role": role})
        logger.info(f"Client connected to channel '{channel_id}' with role '{role}'. Active connection sets: {len(self.active_connections)}")

    def disconnect(self, socket: WebSocket, channel_id: str):
        """Remove connection from the channel pool."""
        if channel_id in self.active_connections:
            self.active_connections[channel_id] = [conn for conn in self.active_connections[channel_id] if conn["socket"] != socket]
            if not self.active_connections[channel_id]:
                del self.active_connections[channel_id]
        logger.info(f"Client disconnected from channel: {channel_id}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message directly to a single socket."""
        await websocket.send_text(message)

    async def broadcast_to_channel(self, channel_id: str, message: dict):
        """Broadcast payload to all sockets listening to a channel with role-based stream filtering."""
        if channel_id in self.active_connections:
            event_name = message.get("event") or message.get("event_type") or ""
            is_user_event = event_name in [
                "assistant_stream", "assistant_message", "artifact_ready", 
                "approval_required", "notification", "status_update",
                "MissionStarted", "MissionProgress", "MissionCompleted", 
                "MissionResult", "MissionArtifactGenerated", "connected", "user_input", "pong"
            ]

            for item in self.active_connections[channel_id]:
                conn_socket = item["socket"]
                conn_role = item["role"]

                # If user role is "user", omit internal developer/admin trace logs
                if conn_role == "user" and not is_user_event:
                    continue

                try:
                    await conn_socket.send_text(json.dumps(message))
                except Exception as e:
                    logger.warning(f"Error broadcasting message to socket: {e}")

# Global connection manager instance
manager = ConnectionManager()

@router.websocket("/{channel_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    channel_id: str,
    token: str = Query(None)  # Can be used for WebSocket auth validation
):
    """WebSocket endpoint to connect to live stream channels with strict RBAC."""
    from jose import jwt
    from authentication.jwt_handler import JWT_SECRET, JWT_ALGORITHM
    from database.connection import async_session
    from database.models import User, Goal
    from sqlalchemy.future import select
    from uuid import UUID

    user = None
    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            email = payload.get("sub")
            user_id_str = payload.get("user_id")
            if email and user_id_str:
                async with async_session() as db:
                    result = await db.execute(select(User).where(User.id == UUID(user_id_str)))
                    user = result.scalars().first()
        except Exception:
            pass

    if not user:
        await websocket.accept()
        await websocket.send_json({
            "event": "error",
            "message": "Unauthorized. Invalid token."
        })
        await websocket.close(code=4001)
        return

    # Enforce Role-Based Access Control on channel_id
    is_developer_channel = channel_id in ["system_logs", "live_events", "agent_trace", "global_metrics"]
    
    # Check if channel_id is a Goal UUID
    is_goal_uuid = False
    try:
        goal_uuid = UUID(channel_id)
        is_goal_uuid = True
    except ValueError:
        pass

    if is_developer_channel:
        if user.role not in ["admin", "developer"]:
            await websocket.accept()
            await websocket.send_json({
                "event": "error",
                "message": "Forbidden. Developer or Admin access required."
            })
            await websocket.close(code=4003)
            return
    elif is_goal_uuid:
        async with async_session() as db:
            result = await db.execute(select(Goal).where(Goal.id == UUID(channel_id)))
            goal = result.scalars().first()
            if goal and user.role not in ["admin", "developer"] and goal.user_id != user.id:
                await websocket.accept()
                await websocket.send_json({
                    "event": "error",
                    "message": "Forbidden. You do not own this workflow."
                })
                await websocket.close(code=4003)
                return
    else:
        # General non-standard channels
        if user.role not in ["admin", "developer"]:
            await websocket.accept()
            await websocket.send_json({
                "event": "error",
                "message": "Forbidden. Developer or Admin access required."
            })
            await websocket.close(code=4003)
            return

    await manager.connect(websocket, channel_id, role=user.role if user else "user")
    
    # Send connection acknowledgment
    await websocket.send_json({
        "event": "connected",
        "channel": channel_id,
        "message": "Real-time logs connection established"
    })
    
    try:
        while True:
            # Keep connection alive, listen for any user interruptions
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                logger.info(f"Received WebSocket frame on {channel_id}: {message}")
                
                # Check for ping event and echo back pong
                if message.get("event") == "ping":
                    await websocket.send_json({"event": "pong"})
                else:
                    # Echo message or broadcast back to channel as a standard echo
                    await manager.broadcast_to_channel(channel_id, {
                        "event": "user_input",
                        "content": message.get("content")
                    })
            except json.JSONDecodeError:
                # Handle raw text frame
                await websocket.send_json({
                    "event": "error",
                    "message": "Invalid JSON frame received"
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel_id)
