"""
Enhanced WebSocket endpoints for real-time collaboration
"""
import json
import logging
from typing import Any, Dict
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.db.database import get_db
from app.models.user import User
from app.services.websocket_manager import websocket_manager
from app.crud.crud_document import crud_document
from app.crud.crud_deal import crud_deal

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    organization_id: str = Query(...),
    user_name: str = Query(None)
):
    """
    Main WebSocket endpoint for real-time collaboration
    """
    try:
        # Connect user to WebSocket
        await websocket_manager.connect(websocket, user_id, organization_id, user_name)
        
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)

                # Track message received
                await websocket_manager.handle_message_received(user_id, message)

                # Handle different message types
                await handle_websocket_message(user_id, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, user_id)
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {str(e)}")
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "message": f"Message handling error: {str(e)}"
                }, user_id)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
    
    finally:
        # Disconnect user
        websocket_manager.disconnect(user_id)


async def handle_websocket_message(user_id: str, message: Dict[str, Any]):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    if message_type == "join_document":
        document_id = message.get("document_id")
        if document_id:
            await websocket_manager.join_document_room(user_id, document_id)
    
    elif message_type == "leave_document":
        document_id = message.get("document_id")
        if document_id:
            await websocket_manager.leave_document_room(user_id, document_id)
    
    elif message_type == "document_comment":
        await handle_document_comment(user_id, message)
    
    elif message_type == "document_annotation":
        await handle_document_annotation(user_id, message)
    
    elif message_type == "analysis_feedback":
        await handle_analysis_feedback(user_id, message)
    
    elif message_type == "typing_indicator":
        await handle_typing_indicator(user_id, message)
    
    elif message_type == "cursor_position":
        await handle_cursor_position(user_id, message)

    elif message_type == "financial_model_update":
        await handle_financial_model_update(user_id, message)

    elif message_type == "join_financial_model":
        await handle_join_financial_model(user_id, message)

    elif message_type == "leave_financial_model":
        await handle_leave_financial_model(user_id, message)

    elif message_type == "scenario_update":
        await handle_scenario_update(user_id, message)

    elif message_type == "user_presence_update":
        await handle_user_presence_update(user_id, message)

    elif message_type == "ping":
        # Respond to ping with pong
        await websocket_manager.send_personal_message({
            "type": "pong",
            "timestamp": message.get("timestamp")
        }, user_id)
    
    else:
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }, user_id)


async def handle_document_comment(user_id: str, message: Dict[str, Any]):
    """Handle document comment messages"""
    document_id = message.get("document_id")
    comment_text = message.get("comment")
    page_number = message.get("page_number", 1)
    position = message.get("position", {})
    
    if not document_id or not comment_text:
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": "Document ID and comment text are required"
        }, user_id)
        return
    
    # Get user session info
    session = websocket_manager.user_sessions.get(user_id, {})
    user_name = session.get("user_name", f"User {user_id[:8]}")
    
    # Broadcast comment to all document collaborators
    comment_message = {
        "type": "document_comment_added",
        "document_id": document_id,
        "comment_id": f"comment_{user_id}_{len(comment_text)}",  # Simple ID generation
        "user_id": user_id,
        "user_name": user_name,
        "comment": comment_text,
        "page_number": page_number,
        "position": position,
        "timestamp": message.get("timestamp")
    }
    
    await websocket_manager.broadcast_to_document(comment_message, document_id)


async def handle_document_annotation(user_id: str, message: Dict[str, Any]):
    """Handle document annotation messages"""
    document_id = message.get("document_id")
    annotation_type = message.get("annotation_type")  # highlight, underline, note, etc.
    content = message.get("content")
    position = message.get("position", {})
    
    if not document_id or not annotation_type:
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": "Document ID and annotation type are required"
        }, user_id)
        return
    
    # Get user session info
    session = websocket_manager.user_sessions.get(user_id, {})
    user_name = session.get("user_name", f"User {user_id[:8]}")
    
    # Broadcast annotation to all document collaborators
    annotation_message = {
        "type": "document_annotation_added",
        "document_id": document_id,
        "annotation_id": f"annotation_{user_id}_{annotation_type}",
        "user_id": user_id,
        "user_name": user_name,
        "annotation_type": annotation_type,
        "content": content,
        "position": position,
        "timestamp": message.get("timestamp")
    }
    
    await websocket_manager.broadcast_to_document(annotation_message, document_id, exclude_user=user_id)


async def handle_analysis_feedback(user_id: str, message: Dict[str, Any]):
    """Handle analysis feedback messages"""
    document_id = message.get("document_id")
    feedback_type = message.get("feedback_type")  # approve, reject, request_changes
    feedback_text = message.get("feedback")
    analysis_section = message.get("analysis_section")  # risk_assessment, compliance, etc.
    
    if not document_id or not feedback_type:
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": "Document ID and feedback type are required"
        }, user_id)
        return
    
    # Get user session info
    session = websocket_manager.user_sessions.get(user_id, {})
    user_name = session.get("user_name", f"User {user_id[:8]}")
    
    # Broadcast feedback to all document collaborators
    feedback_message = {
        "type": "analysis_feedback_added",
        "document_id": document_id,
        "feedback_id": f"feedback_{user_id}_{feedback_type}",
        "user_id": user_id,
        "user_name": user_name,
        "feedback_type": feedback_type,
        "feedback": feedback_text,
        "analysis_section": analysis_section,
        "timestamp": message.get("timestamp")
    }
    
    await websocket_manager.broadcast_to_document(feedback_message, document_id)


async def handle_typing_indicator(user_id: str, message: Dict[str, Any]):
    """Handle typing indicator messages"""
    document_id = message.get("document_id")
    is_typing = message.get("is_typing", False)
    
    if not document_id:
        return
    
    # Get user session info
    session = websocket_manager.user_sessions.get(user_id, {})
    user_name = session.get("user_name", f"User {user_id[:8]}")
    
    # Broadcast typing indicator to other collaborators
    typing_message = {
        "type": "typing_indicator",
        "document_id": document_id,
        "user_id": user_id,
        "user_name": user_name,
        "is_typing": is_typing,
        "timestamp": message.get("timestamp")
    }
    
    await websocket_manager.broadcast_to_document(typing_message, document_id, exclude_user=user_id)


async def handle_cursor_position(user_id: str, message: Dict[str, Any]):
    """Handle cursor position updates for collaborative editing"""
    document_id = message.get("document_id")
    position = message.get("position", {})
    
    if not document_id:
        return
    
    # Get user session info
    session = websocket_manager.user_sessions.get(user_id, {})
    user_name = session.get("user_name", f"User {user_id[:8]}")
    
    # Broadcast cursor position to other collaborators
    cursor_message = {
        "type": "cursor_position",
        "document_id": document_id,
        "user_id": user_id,
        "user_name": user_name,
        "position": position,
        "timestamp": message.get("timestamp")
    }
    
    await websocket_manager.broadcast_to_document(cursor_message, document_id, exclude_user=user_id)


async def handle_financial_model_update(user_id: str, message: Dict[str, Any]):
    """Handle real-time financial model updates"""
    model_id = message.get("model_id")
    update_data = message.get("update_data", {})
    update_type = message.get("update_type", "cell_update")  # cell_update, formula_update, structure_update

    if not model_id:
        return

    # Get user session info
    session = websocket_manager.user_sessions.get(user_id, {})
    user_name = session.get("user_name", f"User {user_id[:8]}")

    # Create update message
    update_message = {
        "type": "financial_model_update",
        "model_id": model_id,
        "user_id": user_id,
        "user_name": user_name,
        "update_type": update_type,
        "update_data": update_data,
        "timestamp": message.get("timestamp"),
        "version": message.get("version", 1)
    }

    # Broadcast to all users working on this model
    await websocket_manager.broadcast_to_deal(update_message, f"model_{model_id}", exclude_user=user_id)

    # Log the update for audit trail
    logger.info(f"Financial model update: {model_id} by {user_name} ({update_type})")


async def handle_join_financial_model(user_id: str, message: Dict[str, Any]):
    """Handle user joining a financial model for collaboration"""
    model_id = message.get("model_id")

    if not model_id:
        return

    # Add user to model room
    await websocket_manager.join_deal_room(user_id, f"model_{model_id}")

    # Get user session info
    session = websocket_manager.user_sessions.get(user_id, {})
    user_name = session.get("user_name", f"User {user_id[:8]}")

    # Notify other users
    join_message = {
        "type": "user_joined_model",
        "model_id": model_id,
        "user_id": user_id,
        "user_name": user_name,
        "timestamp": message.get("timestamp")
    }

    await websocket_manager.broadcast_to_deal(join_message, f"model_{model_id}", exclude_user=user_id)

    # Send current model state to the joining user
    # This would typically fetch the latest model data from the database
    welcome_message = {
        "type": "model_state",
        "model_id": model_id,
        "message": f"Joined financial model collaboration",
        "active_users": len(websocket_manager.deal_rooms.get(f"model_{model_id}", set())),
        "timestamp": message.get("timestamp")
    }

    await websocket_manager.send_personal_message(welcome_message, user_id)


async def handle_leave_financial_model(user_id: str, message: Dict[str, Any]):
    """Handle user leaving a financial model"""
    model_id = message.get("model_id")

    if not model_id:
        return

    # Remove user from model room
    await websocket_manager.leave_deal_room(user_id, f"model_{model_id}")

    # Get user session info
    session = websocket_manager.user_sessions.get(user_id, {})
    user_name = session.get("user_name", f"User {user_id[:8]}")

    # Notify other users
    leave_message = {
        "type": "user_left_model",
        "model_id": model_id,
        "user_id": user_id,
        "user_name": user_name,
        "timestamp": message.get("timestamp")
    }

    await websocket_manager.broadcast_to_deal(leave_message, f"model_{model_id}", exclude_user=user_id)


async def handle_scenario_update(user_id: str, message: Dict[str, Any]):
    """Handle financial model scenario updates"""
    model_id = message.get("model_id")
    scenario_data = message.get("scenario_data", {})
    scenario_name = message.get("scenario_name", "Default")

    if not model_id:
        return

    # Get user session info
    session = websocket_manager.user_sessions.get(user_id, {})
    user_name = session.get("user_name", f"User {user_id[:8]}")

    # Create scenario update message
    scenario_message = {
        "type": "scenario_update",
        "model_id": model_id,
        "user_id": user_id,
        "user_name": user_name,
        "scenario_name": scenario_name,
        "scenario_data": scenario_data,
        "timestamp": message.get("timestamp")
    }

    # Broadcast to all users working on this model
    await websocket_manager.broadcast_to_deal(scenario_message, f"model_{model_id}", exclude_user=user_id)

    logger.info(f"Scenario update: {model_id} scenario '{scenario_name}' by {user_name}")


async def handle_user_presence_update(user_id: str, message: Dict[str, Any]):
    """Handle user presence updates for real-time collaboration"""
    presence_data = {
        "user_id": user_id,
        "user_name": message.get("user_name", f"User {user_id[:8]}"),
        "avatar_url": message.get("avatar_url"),
        "status": message.get("status", "online"),
        "current_module": message.get("current_module"),
        "current_page": message.get("current_page"),
        "last_activity": message.get("last_activity", message.get("timestamp")),
        "cursor_position": message.get("cursor_position")
    }

    # Get user session info
    session = websocket_manager.user_sessions.get(user_id, {})
    organization_id = session.get("organization_id")

    if not organization_id:
        logger.warning(f"No organization_id found for user {user_id}")
        return

    # Update user session with presence data
    websocket_manager.user_sessions[user_id].update({
        "presence": presence_data,
        "last_presence_update": message.get("timestamp")
    })

    # Create presence update message
    presence_message = {
        "type": "user_presence_update",
        **presence_data,
        "timestamp": message.get("timestamp")
    }

    # Broadcast presence update to organization
    await websocket_manager.broadcast_to_organization(
        presence_message,
        organization_id,
        exclude_user=user_id
    )

    # If user is going offline, also send a leave message
    if presence_data["status"] == "offline":
        leave_message = {
            "type": "user_presence_left",
            **presence_data,
            "timestamp": message.get("timestamp")
        }
        await websocket_manager.broadcast_to_organization(
            leave_message,
            organization_id,
            exclude_user=user_id
        )

    logger.debug(f"Presence update: {user_id} is {presence_data['status']} in {presence_data['current_module']}")


@router.get("/active-users", response_model=Dict[str, Any])
def get_active_users(
    organization_id: str = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of currently active users in the organization
    """
    # Use current user's organization if not specified
    if not organization_id:
        organization_id = str(current_user.organization_id)
    
    # Check if user has access to this organization
    if str(current_user.organization_id) != organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    active_users = websocket_manager.get_active_users(organization_id)
    
    return {
        "organization_id": organization_id,
        "active_users_count": len(active_users),
        "active_users": active_users,
        "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
    }


@router.get("/document/{document_id}/collaborators", response_model=Dict[str, Any])
def get_document_collaborators(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of users currently collaborating on a document with enhanced info
    """
    # Check if document exists and user has access
    document = crud_document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    collaborators = websocket_manager.get_document_collaborators(str(document_id))

    return {
        "document_id": str(document_id),
        "collaborators_count": len(collaborators),
        "collaborators": collaborators,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/stats", response_model=Dict[str, Any])
def get_websocket_stats(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get comprehensive WebSocket connection statistics
    """
    # Only allow superusers or organization admins to view stats
    if not current_user.is_superuser:
        # For now, allow all authenticated users to see basic stats
        # In production, you might want to restrict this further
        pass

    stats = websocket_manager.get_connection_stats()

    return {
        "status": "success",
        "stats": stats,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/user/{user_id}/connection", response_model=Dict[str, Any])
def get_user_connection_info(
    user_id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed connection information for a specific user
    """
    # Users can only view their own connection info, unless they're superuser
    if str(current_user.id) != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    connection_info = websocket_manager.get_user_connection_info(user_id)

    if not connection_info:
        raise HTTPException(status_code=404, detail="User connection not found")

    return {
        "status": "success",
        "connection_info": connection_info,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/user/{user_id}/send-message", response_model=Dict[str, Any])
async def send_message_to_user(
    user_id: str,
    message: Dict[str, Any],
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Send a direct message to a specific user (admin function)
    """
    # Only superusers can send direct messages
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Add admin message metadata
    admin_message = {
        **message,
        "type": "admin_message",
        "from_admin": True,
        "admin_user_id": str(current_user.id),
        "admin_user_name": f"{current_user.first_name} {current_user.last_name}",
        "timestamp": datetime.utcnow().isoformat()
    }

    success = await websocket_manager.send_personal_message(admin_message, user_id)

    return {
        "status": "success" if success else "failed",
        "message_sent": success,
        "target_user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
