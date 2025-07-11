"""
Enhanced WebSocket Manager for Real-time Collaboration in DealVerse OS
Optimized for scalability, reliability, and performance
"""
import json
import logging
import time
import weakref
from typing import Dict, List, Set, Any, Optional, Tuple
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from collections import defaultdict, deque
import asyncio
from dataclasses import dataclass, field

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class ConnectionMetrics:
    """Metrics for monitoring WebSocket connections"""
    connected_at: datetime
    last_activity: datetime
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    reconnect_count: int = 0
    error_count: int = 0


@dataclass
class MessageQueue:
    """Message queue for reliable delivery"""
    messages: deque = field(default_factory=deque)
    max_size: int = 1000

    def add_message(self, message: Dict[str, Any]) -> bool:
        """Add message to queue, return False if queue is full"""
        if len(self.messages) >= self.max_size:
            # Remove oldest message to make room
            self.messages.popleft()

        self.messages.append({
            **message,
            "queued_at": datetime.utcnow().isoformat(),
            "message_id": str(uuid4())
        })
        return True

    def get_pending_messages(self) -> List[Dict[str, Any]]:
        """Get all pending messages and clear queue"""
        messages = list(self.messages)
        self.messages.clear()
        return messages


@dataclass
class RateLimiter:
    """Rate limiter for WebSocket messages"""
    max_messages: int = 100
    time_window: int = 60  # seconds
    message_timestamps: deque = field(default_factory=deque)

    def is_allowed(self) -> bool:
        """Check if message is allowed based on rate limit"""
        now = time.time()

        # Remove old timestamps outside the time window
        while self.message_timestamps and self.message_timestamps[0] < now - self.time_window:
            self.message_timestamps.popleft()

        # Check if under limit
        if len(self.message_timestamps) < self.max_messages:
            self.message_timestamps.append(now)
            return True

        return False


class EnhancedConnectionManager:
    """Enhanced WebSocket connection manager with scalability and reliability features"""

    def __init__(self):
        # Active connections by user ID
        self.active_connections: Dict[str, WebSocket] = {}

        # Connection metrics for monitoring
        self.connection_metrics: Dict[str, ConnectionMetrics] = {}

        # Message queues for offline users
        self.message_queues: Dict[str, MessageQueue] = defaultdict(MessageQueue)

        # Rate limiters per user
        self.rate_limiters: Dict[str, RateLimiter] = defaultdict(RateLimiter)

        # Document rooms - users connected to specific documents
        self.document_rooms: Dict[str, Set[str]] = {}

        # Deal rooms - users connected to specific deals
        self.deal_rooms: Dict[str, Set[str]] = {}

        # Organization rooms - users connected to organization-wide updates
        self.organization_rooms: Dict[str, Set[str]] = {}

        # User sessions with metadata
        self.user_sessions: Dict[str, Dict[str, Any]] = {}

        # Message history for rooms (limited)
        self.message_history: Dict[str, List[Dict[str, Any]]] = {}

        # Connection health monitoring
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}

        # Performance metrics
        self.total_connections = 0
        self.total_messages_sent = 0
        self.total_messages_received = 0
        self.peak_concurrent_connections = 0

        # Cleanup task for inactive connections
        self.cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_started = False
        
    def _start_cleanup_task(self):
        """Start background task for cleaning up inactive connections"""
        if not self._cleanup_started:
            try:
                if self.cleanup_task is None or self.cleanup_task.done():
                    self.cleanup_task = asyncio.create_task(self._cleanup_inactive_connections())
                    self._cleanup_started = True
            except RuntimeError:
                # No event loop running, will start cleanup when first connection is made
                pass

    async def _cleanup_inactive_connections(self):
        """Background task to clean up inactive connections"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._remove_inactive_connections()
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")

    async def _remove_inactive_connections(self):
        """Remove connections that have been inactive for too long"""
        inactive_threshold = datetime.utcnow() - timedelta(minutes=30)
        inactive_users = []

        for user_id, metrics in self.connection_metrics.items():
            if metrics.last_activity < inactive_threshold:
                inactive_users.append(user_id)

        for user_id in inactive_users:
            logger.info(f"Removing inactive connection for user {user_id}")
            self.disconnect(user_id)

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        organization_id: str,
        user_name: str = None
    ):
        """Accept a new WebSocket connection with enhanced monitoring"""
        await websocket.accept()

        # Handle reconnection
        if user_id in self.active_connections:
            logger.info(f"User {user_id} reconnecting, closing old connection")
            old_connection = self.active_connections[user_id]
            try:
                await old_connection.close()
            except:
                pass

            # Increment reconnect count
            if user_id in self.connection_metrics:
                self.connection_metrics[user_id].reconnect_count += 1

        # Store connection
        self.active_connections[user_id] = websocket

        # Initialize/update connection metrics
        now = datetime.utcnow()
        self.connection_metrics[user_id] = ConnectionMetrics(
            connected_at=now,
            last_activity=now,
            reconnect_count=self.connection_metrics.get(user_id, ConnectionMetrics(now, now)).reconnect_count
        )

        # Store session metadata
        self.user_sessions[user_id] = {
            "user_id": user_id,
            "organization_id": organization_id,
            "user_name": user_name or f"User {user_id[:8]}",
            "connected_at": now,
            "last_activity": now,
            "current_document": None,
            "current_deal": None,
            "connection_id": str(uuid4())
        }

        # Update statistics
        self.total_connections += 1
        current_connections = len(self.active_connections)
        if current_connections > self.peak_concurrent_connections:
            self.peak_concurrent_connections = current_connections

        # Add to organization room
        if organization_id not in self.organization_rooms:
            self.organization_rooms[organization_id] = set()
        self.organization_rooms[organization_id].add(user_id)

        # Start cleanup task if not already started
        if not self._cleanup_started:
            self._start_cleanup_task()

        # Start heartbeat monitoring
        await self._start_heartbeat(user_id)

        # Send pending messages if any
        await self._send_pending_messages(user_id)

        # Send welcome message with connection info
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Connected to DealVerse OS real-time collaboration",
            "user_id": user_id,
            "connection_id": self.user_sessions[user_id]["connection_id"],
            "server_time": now.isoformat(),
            "features": {
                "heartbeat_enabled": True,
                "message_queuing": True,
                "rate_limiting": True
            }
        }, user_id)

        # Notify organization about new connection
        await self.broadcast_to_organization({
            "type": "user_connected",
            "user_id": user_id,
            "user_name": self.user_sessions[user_id]["user_name"],
            "timestamp": now.isoformat()
        }, organization_id, exclude_user=user_id)

        logger.info(f"User {user_id} connected to enhanced WebSocket (total: {current_connections})")
    
    async def _start_heartbeat(self, user_id: str):
        """Start heartbeat monitoring for a user"""
        # Cancel existing heartbeat task if any
        if user_id in self.heartbeat_tasks:
            self.heartbeat_tasks[user_id].cancel()

        # Start new heartbeat task
        self.heartbeat_tasks[user_id] = asyncio.create_task(self._heartbeat_monitor(user_id))

    async def _heartbeat_monitor(self, user_id: str):
        """Monitor connection health with heartbeat"""
        try:
            while user_id in self.active_connections:
                await asyncio.sleep(self.heartbeat_interval)

                # Send ping
                await self.send_personal_message({
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat()
                }, user_id)

                # Check if connection is still alive
                if user_id in self.connection_metrics:
                    last_activity = self.connection_metrics[user_id].last_activity
                    if datetime.utcnow() - last_activity > timedelta(seconds=self.heartbeat_interval * 3):
                        logger.warning(f"User {user_id} appears inactive, disconnecting")
                        self.disconnect(user_id)
                        break

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Heartbeat monitor error for user {user_id}: {str(e)}")

    async def _send_pending_messages(self, user_id: str):
        """Send any pending messages to a reconnected user"""
        if user_id in self.message_queues:
            pending_messages = self.message_queues[user_id].get_pending_messages()

            if pending_messages:
                logger.info(f"Sending {len(pending_messages)} pending messages to user {user_id}")

                for message in pending_messages:
                    await self.send_personal_message({
                        "type": "queued_message",
                        "original_message": message,
                        "queued_at": message.get("queued_at"),
                        "delivered_at": datetime.utcnow().isoformat()
                    }, user_id)

    def disconnect(self, user_id: str):
        """Remove a WebSocket connection with enhanced cleanup"""
        if user_id in self.active_connections:
            # Get user session info before removing
            session = self.user_sessions.get(user_id, {})
            organization_id = session.get("organization_id")
            user_name = session.get("user_name", f"User {user_id[:8]}")

            # Cancel heartbeat task
            if user_id in self.heartbeat_tasks:
                self.heartbeat_tasks[user_id].cancel()
                del self.heartbeat_tasks[user_id]

            # Remove from all rooms
            self._remove_user_from_all_rooms(user_id)

            # Remove connection and session
            del self.active_connections[user_id]
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]

            # Keep connection metrics for a while (for reconnection tracking)
            # They will be cleaned up by the cleanup task

            # Notify organization about disconnection
            if organization_id:
                asyncio.create_task(self.broadcast_to_organization({
                    "type": "user_disconnected",
                    "user_id": user_id,
                    "user_name": user_name,
                    "timestamp": datetime.utcnow().isoformat()
                }, organization_id))

            current_connections = len(self.active_connections)
            logger.info(f"User {user_id} disconnected from enhanced WebSocket (remaining: {current_connections})")
    
    def _remove_user_from_all_rooms(self, user_id: str):
        """Remove user from all rooms"""
        # Remove from document rooms
        for room_users in self.document_rooms.values():
            room_users.discard(user_id)
        
        # Remove from deal rooms
        for room_users in self.deal_rooms.values():
            room_users.discard(user_id)
        
        # Remove from organization rooms
        for room_users in self.organization_rooms.values():
            room_users.discard(user_id)
    
    async def send_personal_message(self, message: Dict[str, Any], user_id: str, queue_if_offline: bool = True):
        """Send a message to a specific user with enhanced reliability"""
        # Check rate limiting
        if not self.rate_limiters[user_id].is_allowed():
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False

        if user_id in self.active_connections:
            try:
                message_str = json.dumps(message)
                await self.active_connections[user_id].send_text(message_str)

                # Update metrics
                if user_id in self.connection_metrics:
                    metrics = self.connection_metrics[user_id]
                    metrics.last_activity = datetime.utcnow()
                    metrics.messages_sent += 1
                    metrics.bytes_sent += len(message_str.encode('utf-8'))

                # Update session last activity
                if user_id in self.user_sessions:
                    self.user_sessions[user_id]["last_activity"] = datetime.utcnow()

                # Update global statistics
                self.total_messages_sent += 1

                return True

            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {str(e)}")

                # Update error count
                if user_id in self.connection_metrics:
                    self.connection_metrics[user_id].error_count += 1

                # Queue message if connection failed and queuing is enabled
                if queue_if_offline:
                    self.message_queues[user_id].add_message(message)
                    logger.info(f"Message queued for offline user {user_id}")

                # Remove broken connection
                self.disconnect(user_id)
                return False
        else:
            # User is offline, queue message if enabled
            if queue_if_offline:
                self.message_queues[user_id].add_message(message)
                logger.info(f"Message queued for offline user {user_id}")
                return True

            return False
    
    async def join_document_room(self, user_id: str, document_id: str):
        """Add user to a document room for collaborative editing"""
        if document_id not in self.document_rooms:
            self.document_rooms[document_id] = set()
        
        self.document_rooms[document_id].add(user_id)
        
        # Update user session
        if user_id in self.user_sessions:
            self.user_sessions[user_id]["current_document"] = document_id
        
        # Notify other users in the document room
        await self.broadcast_to_document({
            "type": "user_joined_document",
            "user_id": user_id,
            "user_name": self.user_sessions.get(user_id, {}).get("user_name", f"User {user_id[:8]}"),
            "document_id": document_id,
            "timestamp": datetime.utcnow().isoformat()
        }, document_id, exclude_user=user_id)
        
        # Send current document collaborators to the joining user
        collaborators = []
        for collaborator_id in self.document_rooms[document_id]:
            if collaborator_id != user_id and collaborator_id in self.user_sessions:
                collaborators.append({
                    "user_id": collaborator_id,
                    "user_name": self.user_sessions[collaborator_id]["user_name"]
                })
        
        await self.send_personal_message({
            "type": "document_room_joined",
            "document_id": document_id,
            "collaborators": collaborators,
            "timestamp": datetime.utcnow().isoformat()
        }, user_id)
    
    async def leave_document_room(self, user_id: str, document_id: str):
        """Remove user from a document room"""
        if document_id in self.document_rooms:
            self.document_rooms[document_id].discard(user_id)
            
            # Clean up empty rooms
            if not self.document_rooms[document_id]:
                del self.document_rooms[document_id]
        
        # Update user session
        if user_id in self.user_sessions:
            self.user_sessions[user_id]["current_document"] = None
        
        # Notify other users in the document room
        await self.broadcast_to_document({
            "type": "user_left_document",
            "user_id": user_id,
            "user_name": self.user_sessions.get(user_id, {}).get("user_name", f"User {user_id[:8]}"),
            "document_id": document_id,
            "timestamp": datetime.utcnow().isoformat()
        }, document_id)
    
    async def broadcast_to_document(
        self,
        message: Dict[str, Any],
        document_id: str,
        exclude_user: str = None,
        priority: bool = False
    ):
        """Broadcast message to all users in a document room with enhanced delivery"""
        if document_id in self.document_rooms:
            # Add broadcast metadata
            enhanced_message = {
                **message,
                "broadcast_id": str(uuid4()),
                "broadcast_type": "document",
                "target_id": document_id,
                "broadcast_time": datetime.utcnow().isoformat()
            }

            # Store in message history
            self._add_to_message_history(f"document_{document_id}", enhanced_message)

            # Send to all users in parallel for better performance
            tasks = []
            for user_id in self.document_rooms[document_id]:
                if user_id != exclude_user:
                    task = asyncio.create_task(
                        self.send_personal_message(enhanced_message, user_id, queue_if_offline=not priority)
                    )
                    tasks.append(task)

            # Wait for all messages to be sent
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success_count = sum(1 for result in results if result is True)
                logger.debug(f"Document broadcast to {document_id}: {success_count}/{len(tasks)} delivered")

    async def broadcast_to_deal(
        self,
        message: Dict[str, Any],
        deal_id: str,
        exclude_user: str = None,
        priority: bool = False
    ):
        """Broadcast message to all users in a deal room with enhanced delivery"""
        if deal_id in self.deal_rooms:
            # Add broadcast metadata
            enhanced_message = {
                **message,
                "broadcast_id": str(uuid4()),
                "broadcast_type": "deal",
                "target_id": deal_id,
                "broadcast_time": datetime.utcnow().isoformat()
            }

            # Store in message history
            self._add_to_message_history(f"deal_{deal_id}", enhanced_message)

            # Send to all users in parallel
            tasks = []
            for user_id in self.deal_rooms[deal_id]:
                if user_id != exclude_user:
                    task = asyncio.create_task(
                        self.send_personal_message(enhanced_message, user_id, queue_if_offline=not priority)
                    )
                    tasks.append(task)

            # Wait for all messages to be sent
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success_count = sum(1 for result in results if result is True)
                logger.debug(f"Deal broadcast to {deal_id}: {success_count}/{len(tasks)} delivered")

    async def broadcast_to_organization(
        self,
        message: Dict[str, Any],
        organization_id: str,
        exclude_user: str = None,
        priority: bool = False
    ):
        """Broadcast message to all users in an organization with enhanced delivery"""
        if organization_id in self.organization_rooms:
            # Add broadcast metadata
            enhanced_message = {
                **message,
                "broadcast_id": str(uuid4()),
                "broadcast_type": "organization",
                "target_id": organization_id,
                "broadcast_time": datetime.utcnow().isoformat()
            }

            # Store in message history
            self._add_to_message_history(f"org_{organization_id}", enhanced_message)

            # Send to all users in parallel
            tasks = []
            for user_id in self.organization_rooms[organization_id]:
                if user_id != exclude_user:
                    task = asyncio.create_task(
                        self.send_personal_message(enhanced_message, user_id, queue_if_offline=not priority)
                    )
                    tasks.append(task)

            # Wait for all messages to be sent
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success_count = sum(1 for result in results if result is True)
                logger.debug(f"Organization broadcast to {organization_id}: {success_count}/{len(tasks)} delivered")
    
    async def notify_document_analysis_update(
        self, 
        document_id: str, 
        analysis_status: str, 
        progress: int = None,
        results: Dict[str, Any] = None
    ):
        """Notify users about document analysis progress"""
        message = {
            "type": "document_analysis_update",
            "document_id": document_id,
            "status": analysis_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if progress is not None:
            message["progress"] = progress
        
        if results:
            message["results"] = results
        
        await self.broadcast_to_document(message, document_id)
    
    async def notify_risk_assessment_update(
        self, 
        deal_id: str, 
        assessment_status: str, 
        risk_score: float = None,
        critical_issues: List[str] = None
    ):
        """Notify users about risk assessment updates"""
        message = {
            "type": "risk_assessment_update",
            "deal_id": deal_id,
            "status": assessment_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if risk_score is not None:
            message["risk_score"] = risk_score
        
        if critical_issues:
            message["critical_issues"] = critical_issues
        
        await self.broadcast_to_deal(message, deal_id)
    
    def get_active_users(self, organization_id: str = None) -> List[Dict[str, Any]]:
        """Get list of active users"""
        active_users = []
        
        for user_id, session in self.user_sessions.items():
            if organization_id is None or session.get("organization_id") == organization_id:
                active_users.append({
                    "user_id": user_id,
                    "user_name": session.get("user_name"),
                    "connected_at": session.get("connected_at").isoformat() if session.get("connected_at") else None,
                    "last_activity": session.get("last_activity").isoformat() if session.get("last_activity") else None,
                    "current_document": session.get("current_document"),
                    "current_deal": session.get("current_deal")
                })
        
        return active_users
    
    def _add_to_message_history(self, room_key: str, message: Dict[str, Any]):
        """Add message to room history with size limit"""
        if room_key not in self.message_history:
            self.message_history[room_key] = []

        self.message_history[room_key].append(message)

        # Keep only last 100 messages per room
        if len(self.message_history[room_key]) > 100:
            self.message_history[room_key] = self.message_history[room_key][-100:]

    def get_document_collaborators(self, document_id: str) -> List[Dict[str, Any]]:
        """Get list of users currently collaborating on a document with enhanced info"""
        collaborators = []

        if document_id in self.document_rooms:
            for user_id in self.document_rooms[document_id]:
                if user_id in self.user_sessions:
                    session = self.user_sessions[user_id]
                    metrics = self.connection_metrics.get(user_id)

                    collaborator_info = {
                        "user_id": user_id,
                        "user_name": session.get("user_name"),
                        "last_activity": session.get("last_activity").isoformat() if session.get("last_activity") else None,
                        "connected_at": session.get("connected_at").isoformat() if session.get("connected_at") else None,
                        "connection_id": session.get("connection_id"),
                        "is_active": user_id in self.active_connections
                    }

                    if metrics:
                        collaborator_info.update({
                            "messages_sent": metrics.messages_sent,
                            "messages_received": metrics.messages_received,
                            "reconnect_count": metrics.reconnect_count
                        })

                    collaborators.append(collaborator_info)

        return collaborators

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection statistics"""
        active_connections = len(self.active_connections)
        total_rooms = len(self.document_rooms) + len(self.deal_rooms) + len(self.organization_rooms)

        # Calculate average messages per connection
        total_user_messages = sum(
            metrics.messages_sent + metrics.messages_received
            for metrics in self.connection_metrics.values()
        )
        avg_messages = total_user_messages / max(active_connections, 1)

        # Get organization distribution
        org_distribution = {}
        for org_id, users in self.organization_rooms.items():
            org_distribution[org_id] = len(users)

        return {
            "active_connections": active_connections,
            "peak_concurrent_connections": self.peak_concurrent_connections,
            "total_connections_served": self.total_connections,
            "total_messages_sent": self.total_messages_sent,
            "total_messages_received": self.total_messages_received,
            "average_messages_per_connection": round(avg_messages, 2),
            "total_rooms": total_rooms,
            "document_rooms": len(self.document_rooms),
            "deal_rooms": len(self.deal_rooms),
            "organization_rooms": len(self.organization_rooms),
            "organization_distribution": org_distribution,
            "message_queues_active": len([q for q in self.message_queues.values() if q.messages]),
            "heartbeat_tasks_active": len(self.heartbeat_tasks),
            "server_uptime": datetime.utcnow().isoformat()
        }

    def get_user_connection_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed connection information for a specific user"""
        if user_id not in self.user_sessions:
            return None

        session = self.user_sessions[user_id]
        metrics = self.connection_metrics.get(user_id)

        info = {
            "user_id": user_id,
            "is_connected": user_id in self.active_connections,
            "session": session,
            "current_rooms": {
                "documents": [doc_id for doc_id, users in self.document_rooms.items() if user_id in users],
                "deals": [deal_id for deal_id, users in self.deal_rooms.items() if user_id in users],
                "organizations": [org_id for org_id, users in self.organization_rooms.items() if user_id in users]
            },
            "pending_messages": len(self.message_queues[user_id].messages) if user_id in self.message_queues else 0,
            "has_heartbeat": user_id in self.heartbeat_tasks
        }

        if metrics:
            info["metrics"] = {
                "connected_at": metrics.connected_at.isoformat(),
                "last_activity": metrics.last_activity.isoformat(),
                "messages_sent": metrics.messages_sent,
                "messages_received": metrics.messages_received,
                "bytes_sent": metrics.bytes_sent,
                "bytes_received": metrics.bytes_received,
                "reconnect_count": metrics.reconnect_count,
                "error_count": metrics.error_count
            }

        return info

    async def handle_message_received(self, user_id: str, message: Dict[str, Any]):
        """Handle incoming message with metrics tracking"""
        # Update metrics
        if user_id in self.connection_metrics:
            metrics = self.connection_metrics[user_id]
            metrics.last_activity = datetime.utcnow()
            metrics.messages_received += 1

            # Estimate message size
            message_size = len(json.dumps(message).encode('utf-8'))
            metrics.bytes_received += message_size

        # Update global statistics
        self.total_messages_received += 1

        # Update session last activity
        if user_id in self.user_sessions:
            self.user_sessions[user_id]["last_activity"] = datetime.utcnow()


# Global enhanced WebSocket manager instance
websocket_manager = EnhancedConnectionManager()
