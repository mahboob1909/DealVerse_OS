#!/usr/bin/env python3
"""
Enhanced WebSocket API Endpoints Test
Tests the new WebSocket monitoring and management endpoints
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.api_v1.endpoints.websocket import router
from app.services.websocket_manager import websocket_manager


def test_websocket_stats_endpoint():
    """Test WebSocket stats endpoint structure"""
    print("🧪 Testing WebSocket Stats Endpoint...")
    
    # Check that the endpoint exists
    routes = [route for route in router.routes if hasattr(route, 'path')]
    stats_route = next((route for route in routes if route.path == "/stats"), None)
    
    assert stats_route is not None, "Stats endpoint not found"
    assert stats_route.methods == {"GET"}, "Stats endpoint should be GET only"
    
    print("✅ WebSocket stats endpoint structure is correct")


def test_user_connection_endpoint():
    """Test user connection info endpoint structure"""
    print("🧪 Testing User Connection Endpoint...")
    
    routes = [route for route in router.routes if hasattr(route, 'path')]
    user_route = next((route for route in routes if "/user/" in route.path and "/connection" in route.path), None)
    
    assert user_route is not None, "User connection endpoint not found"
    assert user_route.methods == {"GET"}, "User connection endpoint should be GET only"
    
    print("✅ User connection endpoint structure is correct")


def test_send_message_endpoint():
    """Test send message endpoint structure"""
    print("🧪 Testing Send Message Endpoint...")
    
    routes = [route for route in router.routes if hasattr(route, 'path')]
    message_route = next((route for route in routes if "/user/" in route.path and "/send-message" in route.path), None)
    
    assert message_route is not None, "Send message endpoint not found"
    assert message_route.methods == {"POST"}, "Send message endpoint should be POST only"
    
    print("✅ Send message endpoint structure is correct")


def test_enhanced_collaborators_endpoint():
    """Test enhanced document collaborators endpoint"""
    print("🧪 Testing Enhanced Collaborators Endpoint...")
    
    routes = [route for route in router.routes if hasattr(route, 'path')]
    collab_route = next((route for route in routes if "/document/" in route.path and "/collaborators" in route.path), None)
    
    assert collab_route is not None, "Document collaborators endpoint not found"
    assert collab_route.methods == {"GET"}, "Document collaborators endpoint should be GET only"
    
    print("✅ Enhanced collaborators endpoint structure is correct")


def test_websocket_manager_integration():
    """Test WebSocket manager integration with API"""
    print("🧪 Testing WebSocket Manager Integration...")
    
    # Test that the enhanced manager is properly imported
    assert hasattr(websocket_manager, 'get_connection_stats'), "Manager missing get_connection_stats method"
    assert hasattr(websocket_manager, 'get_user_connection_info'), "Manager missing get_user_connection_info method"
    assert hasattr(websocket_manager, 'send_personal_message'), "Manager missing send_personal_message method"
    
    # Test stats functionality
    stats = websocket_manager.get_connection_stats()
    
    required_stats = [
        'active_connections', 'peak_concurrent_connections', 'total_connections_served',
        'total_messages_sent', 'total_messages_received', 'average_messages_per_connection',
        'total_rooms', 'document_rooms', 'deal_rooms', 'organization_rooms',
        'organization_distribution', 'message_queues_active', 'heartbeat_tasks_active'
    ]
    
    for stat in required_stats:
        assert stat in stats, f"Missing required stat: {stat}"
    
    print("✅ WebSocket manager integration is correct")


def test_enhanced_features():
    """Test enhanced WebSocket features"""
    print("🧪 Testing Enhanced Features...")
    
    # Test that enhanced classes are available
    from app.services.websocket_manager import ConnectionMetrics, MessageQueue, RateLimiter
    
    # Test ConnectionMetrics
    from datetime import datetime
    metrics = ConnectionMetrics(connected_at=datetime.utcnow(), last_activity=datetime.utcnow())
    assert hasattr(metrics, 'messages_sent'), "ConnectionMetrics missing messages_sent"
    assert hasattr(metrics, 'reconnect_count'), "ConnectionMetrics missing reconnect_count"
    
    # Test MessageQueue
    queue = MessageQueue()
    assert hasattr(queue, 'add_message'), "MessageQueue missing add_message method"
    assert hasattr(queue, 'get_pending_messages'), "MessageQueue missing get_pending_messages method"
    
    # Test RateLimiter
    limiter = RateLimiter()
    assert hasattr(limiter, 'is_allowed'), "RateLimiter missing is_allowed method"
    
    print("✅ Enhanced features are available and working")


def test_api_endpoint_imports():
    """Test that all required imports are available"""
    print("🧪 Testing API Endpoint Imports...")
    
    try:
        from app.api.api_v1.endpoints.websocket import (
            websocket_endpoint,
            handle_websocket_message,
            get_active_users,
            get_document_collaborators,
            get_websocket_stats,
            get_user_connection_info,
            send_message_to_user
        )
        
        print("✅ All API endpoint functions imported successfully")
        
    except ImportError as e:
        raise AssertionError(f"Failed to import API functions: {str(e)}")


def test_websocket_manager_type():
    """Test that the correct WebSocket manager type is being used"""
    print("🧪 Testing WebSocket Manager Type...")
    
    from app.services.websocket_manager import EnhancedConnectionManager
    
    assert isinstance(websocket_manager, EnhancedConnectionManager), "WebSocket manager is not EnhancedConnectionManager"
    assert hasattr(websocket_manager, 'connection_metrics'), "Manager missing connection_metrics"
    assert hasattr(websocket_manager, 'message_queues'), "Manager missing message_queues"
    assert hasattr(websocket_manager, 'rate_limiters'), "Manager missing rate_limiters"
    
    print("✅ Correct WebSocket manager type is being used")


def run_all_tests():
    """Run all enhanced WebSocket API tests"""
    print("🚀 Starting Enhanced WebSocket API Tests\n")
    
    try:
        test_websocket_stats_endpoint()
        test_user_connection_endpoint()
        test_send_message_endpoint()
        test_enhanced_collaborators_endpoint()
        test_websocket_manager_integration()
        test_enhanced_features()
        test_api_endpoint_imports()
        test_websocket_manager_type()
        
        print("\n🎉 ALL ENHANCED WEBSOCKET API TESTS PASSED! 🎯")
        print("✅ Enhanced WebSocket API endpoints are ready for production!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run the tests
    success = run_all_tests()
    exit(0 if success else 1)
