#!/usr/bin/env python3
"""
Enhanced WebSocket Infrastructure Test Suite
Tests the optimized WebSocket manager with scalability and reliability features
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

# Import the enhanced WebSocket manager
from app.services.websocket_manager import (
    EnhancedConnectionManager, 
    ConnectionMetrics, 
    MessageQueue, 
    RateLimiter
)


class MockWebSocket:
    """Mock WebSocket for testing"""
    def __init__(self):
        self.messages_sent = []
        self.closed = False
        
    async def accept(self):
        pass
        
    async def send_text(self, message: str):
        if self.closed:
            raise Exception("WebSocket closed")
        self.messages_sent.append(message)
        
    async def close(self):
        self.closed = True


async def test_connection_metrics():
    """Test connection metrics tracking"""
    print("🧪 Testing Connection Metrics...")
    
    now = datetime.utcnow()
    metrics = ConnectionMetrics(connected_at=now, last_activity=now)
    
    # Test initial state
    assert metrics.messages_sent == 0
    assert metrics.messages_received == 0
    assert metrics.reconnect_count == 0
    assert metrics.error_count == 0
    
    # Test metric updates
    metrics.messages_sent += 5
    metrics.bytes_sent += 1024
    assert metrics.messages_sent == 5
    assert metrics.bytes_sent == 1024
    
    print("✅ Connection metrics working correctly")


async def test_message_queue():
    """Test message queuing functionality"""
    print("🧪 Testing Message Queue...")
    
    queue = MessageQueue(max_size=3)
    
    # Test adding messages
    message1 = {"type": "test", "content": "message1"}
    message2 = {"type": "test", "content": "message2"}
    message3 = {"type": "test", "content": "message3"}
    message4 = {"type": "test", "content": "message4"}
    
    assert queue.add_message(message1) == True
    assert queue.add_message(message2) == True
    assert queue.add_message(message3) == True
    assert len(queue.messages) == 3
    
    # Test queue overflow (should remove oldest)
    assert queue.add_message(message4) == True
    assert len(queue.messages) == 3
    
    # Test getting pending messages
    pending = queue.get_pending_messages()
    assert len(pending) == 3
    assert len(queue.messages) == 0  # Should be cleared
    
    # Verify message structure
    assert all("queued_at" in msg for msg in pending)
    assert all("message_id" in msg for msg in pending)
    
    print("✅ Message queue working correctly")


async def test_rate_limiter():
    """Test rate limiting functionality"""
    print("🧪 Testing Rate Limiter...")
    
    limiter = RateLimiter(max_messages=3, time_window=1)
    
    # Test normal operation
    assert limiter.is_allowed() == True
    assert limiter.is_allowed() == True
    assert limiter.is_allowed() == True
    
    # Test rate limit exceeded
    assert limiter.is_allowed() == False
    
    # Wait for time window to reset
    await asyncio.sleep(1.1)
    assert limiter.is_allowed() == True
    
    print("✅ Rate limiter working correctly")


async def test_enhanced_connection_manager():
    """Test enhanced connection manager functionality"""
    print("🧪 Testing Enhanced Connection Manager...")
    
    manager = EnhancedConnectionManager()
    
    # Test connection
    mock_ws = MockWebSocket()
    user_id = "test_user_123"
    org_id = "test_org_456"
    
    await manager.connect(mock_ws, user_id, org_id, "Test User")
    
    # Verify connection established
    assert user_id in manager.active_connections
    assert user_id in manager.user_sessions
    assert user_id in manager.connection_metrics
    assert org_id in manager.organization_rooms
    assert user_id in manager.organization_rooms[org_id]
    
    # Test message sending with metrics
    test_message = {"type": "test", "content": "Hello World"}
    success = await manager.send_personal_message(test_message, user_id)
    
    assert success == True
    assert len(mock_ws.messages_sent) >= 1  # Welcome message + test message
    assert manager.connection_metrics[user_id].messages_sent > 0
    
    # Test message received tracking
    await manager.handle_message_received(user_id, test_message)
    assert manager.connection_metrics[user_id].messages_received == 1
    
    # Test document room functionality
    doc_id = "test_doc_789"
    await manager.join_document_room(user_id, doc_id)
    
    assert doc_id in manager.document_rooms
    assert user_id in manager.document_rooms[doc_id]
    
    # Test broadcasting
    broadcast_message = {"type": "broadcast", "content": "Broadcast test"}
    await manager.broadcast_to_document(broadcast_message, doc_id)
    
    # Should have received the broadcast
    assert len(mock_ws.messages_sent) > 2
    
    # Test connection stats
    stats = manager.get_connection_stats()
    assert stats["active_connections"] == 1
    assert stats["total_connections_served"] == 1
    assert stats["document_rooms"] == 1
    assert stats["organization_rooms"] == 1
    
    # Test user connection info
    user_info = manager.get_user_connection_info(user_id)
    assert user_info is not None
    assert user_info["user_id"] == user_id
    assert user_info["is_connected"] == True
    assert len(user_info["current_rooms"]["documents"]) == 1
    
    # Test disconnection
    manager.disconnect(user_id)
    assert user_id not in manager.active_connections
    assert user_id not in manager.user_sessions
    
    print("✅ Enhanced connection manager working correctly")


async def test_offline_message_queuing():
    """Test offline message queuing"""
    print("🧪 Testing Offline Message Queuing...")
    
    manager = EnhancedConnectionManager()
    user_id = "offline_user_123"
    
    # Send message to offline user
    test_message = {"type": "test", "content": "Offline message"}
    success = await manager.send_personal_message(test_message, user_id, queue_if_offline=True)
    
    assert success == True
    assert len(manager.message_queues[user_id].messages) == 1
    
    # Connect user and verify pending messages are sent
    mock_ws = MockWebSocket()
    await manager.connect(mock_ws, user_id, "test_org", "Offline User")
    
    # Should have sent welcome message and queued message
    assert len(mock_ws.messages_sent) >= 2
    
    # Verify queue is cleared
    assert len(manager.message_queues[user_id].messages) == 0
    
    print("✅ Offline message queuing working correctly")


async def test_rate_limiting_integration():
    """Test rate limiting integration"""
    print("🧪 Testing Rate Limiting Integration...")
    
    manager = EnhancedConnectionManager()
    mock_ws = MockWebSocket()
    user_id = "rate_test_user"
    
    await manager.connect(mock_ws, user_id, "test_org", "Rate Test User")
    
    # Send messages rapidly to trigger rate limit
    initial_count = len(mock_ws.messages_sent)
    
    # Send many messages quickly
    for i in range(150):  # Exceed default rate limit of 100/minute
        await manager.send_personal_message({"type": "spam", "number": i}, user_id)
    
    # Should have been rate limited
    final_count = len(mock_ws.messages_sent)
    messages_sent = final_count - initial_count
    
    # Should be less than 150 due to rate limiting
    assert messages_sent < 150
    print(f"   Rate limiting active: {messages_sent}/150 messages sent")
    
    print("✅ Rate limiting integration working correctly")


async def test_performance_monitoring():
    """Test performance monitoring features"""
    print("🧪 Testing Performance Monitoring...")
    
    manager = EnhancedConnectionManager()
    
    # Connect multiple users
    users = []
    for i in range(5):
        user_id = f"perf_user_{i}"
        mock_ws = MockWebSocket()
        await manager.connect(mock_ws, user_id, "perf_org", f"User {i}")
        users.append((user_id, mock_ws))
    
    # Send messages to generate metrics
    for user_id, mock_ws in users:
        for j in range(10):
            await manager.send_personal_message({"type": "perf_test", "msg": j}, user_id)
            await manager.handle_message_received(user_id, {"type": "response", "msg": j})
    
    # Check performance stats
    stats = manager.get_connection_stats()
    assert stats["active_connections"] == 5
    assert stats["total_messages_sent"] > 50  # 5 users * 10 messages + welcome messages
    assert stats["total_messages_received"] == 50  # 5 users * 10 messages
    assert stats["peak_concurrent_connections"] == 5
    
    # Test individual user metrics
    user_info = manager.get_user_connection_info(users[0][0])
    assert user_info["metrics"]["messages_sent"] >= 10
    assert user_info["metrics"]["messages_received"] == 10
    
    print("✅ Performance monitoring working correctly")


async def run_all_tests():
    """Run all enhanced WebSocket tests"""
    print("🚀 Starting Enhanced WebSocket Infrastructure Tests\n")
    
    try:
        await test_connection_metrics()
        await test_message_queue()
        await test_rate_limiter()
        await test_enhanced_connection_manager()
        await test_offline_message_queuing()
        await test_rate_limiting_integration()
        await test_performance_monitoring()
        
        print("\n🎉 ALL ENHANCED WEBSOCKET TESTS PASSED! 🎯")
        print("✅ Enhanced WebSocket infrastructure is ready for production!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
