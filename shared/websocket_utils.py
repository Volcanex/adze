"""
WebSocket utilities for real-time features and game development.
Provides common patterns and helpers for WebSocket integration.
"""

from flask_socketio import emit, join_room, leave_room, disconnect
from datetime import datetime
import uuid
import json


class WebSocketRoom:
    """
    Base class for managing WebSocket rooms (lobbies, game sessions, etc.)
    """
    
    def __init__(self, room_id=None, max_players=2):
        self.room_id = room_id or str(uuid.uuid4())
        self.max_players = max_players
        self.players = {}
        self.created_at = datetime.now()
        self.status = 'waiting'  # waiting, active, finished
        self.data = {}
    
    def add_player(self, player_id, player_data=None):
        """Add a player to the room"""
        if len(self.players) >= self.max_players:
            return False, "Room is full"
        
        if player_id in self.players:
            return False, "Player already in room"
        
        self.players[player_id] = {
            'id': player_id,
            'joined_at': datetime.now().isoformat(),
            'data': player_data or {}
        }
        
        return True, "Player added successfully"
    
    def remove_player(self, player_id):
        """Remove a player from the room"""
        if player_id in self.players:
            del self.players[player_id]
            return True
        return False
    
    def get_player_count(self):
        """Get current number of players"""
        return len(self.players)
    
    def is_full(self):
        """Check if room is at capacity"""
        return len(self.players) >= self.max_players
    
    def to_dict(self):
        """Convert room to dictionary for JSON serialization"""
        return {
            'room_id': self.room_id,
            'max_players': self.max_players,
            'current_players': len(self.players),
            'players': list(self.players.keys()),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'data': self.data
        }


class WebSocketRoomManager:
    """
    Manages multiple WebSocket rooms for a page/namespace
    """
    
    def __init__(self):
        self.rooms = {}
    
    def create_room(self, room_id=None, max_players=2):
        """Create a new room"""
        room = WebSocketRoom(room_id, max_players)
        self.rooms[room.room_id] = room
        return room
    
    def get_room(self, room_id):
        """Get a room by ID"""
        return self.rooms.get(room_id)
    
    def find_available_room(self, max_players=2):
        """Find an available room with space"""
        for room in self.rooms.values():
            if room.status == 'waiting' and not room.is_full() and room.max_players == max_players:
                return room
        return None
    
    def remove_room(self, room_id):
        """Remove a room"""
        if room_id in self.rooms:
            del self.rooms[room_id]
            return True
        return False
    
    def cleanup_empty_rooms(self):
        """Remove rooms with no players"""
        empty_rooms = [
            room_id for room_id, room in self.rooms.items() 
            if len(room.players) == 0
        ]
        for room_id in empty_rooms:
            del self.rooms[room_id]
        return len(empty_rooms)
    
    def get_stats(self):
        """Get room manager statistics"""
        return {
            'total_rooms': len(self.rooms),
            'waiting_rooms': len([r for r in self.rooms.values() if r.status == 'waiting']),
            'active_rooms': len([r for r in self.rooms.values() if r.status == 'active']),
            'total_players': sum(len(r.players) for r in self.rooms.values())
        }


def websocket_error_handler(error_message, emit_to_sender=True):
    """
    Standard error handler for WebSocket events
    """
    error_data = {
        'error': True,
        'message': error_message,
        'timestamp': datetime.now().isoformat()
    }
    
    if emit_to_sender:
        emit('error', error_data)
    
    return error_data


def websocket_success_response(data, message="Success"):
    """
    Standard success response for WebSocket events
    """
    return {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }


def broadcast_to_room(room_id, event, data, include_sender=True, namespace=None):
    """
    Helper function to broadcast to all players in a room
    """
    emit(event, data, room=room_id, include_self=include_sender, namespace=namespace)


def validate_websocket_data(data, required_fields):
    """
    Validate incoming WebSocket data
    """
    if not data:
        return False, "No data provided"
    
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, "Valid"


class P2PConnectionHelper:
    """
    Helper class for WebRTC P2P connection setup
    """
    
    @staticmethod
    def handle_webrtc_offer(room_manager, room_id, sender_id, offer_data):
        """
        Handle WebRTC offer from a peer
        """
        room = room_manager.get_room(room_id)
        if not room:
            return websocket_error_handler("Room not found")
        
        if sender_id not in room.players:
            return websocket_error_handler("Player not in room")
        
        # Forward offer to other players in the room
        for player_id in room.players:
            if player_id != sender_id:
                emit('webrtc_offer', {
                    'from': sender_id,
                    'offer': offer_data
                }, room=player_id)
        
        return websocket_success_response({}, "Offer forwarded")
    
    @staticmethod
    def handle_webrtc_answer(room_manager, room_id, sender_id, answer_data):
        """
        Handle WebRTC answer from a peer
        """
        room = room_manager.get_room(room_id)
        if not room:
            return websocket_error_handler("Room not found")
        
        if sender_id not in room.players:
            return websocket_error_handler("Player not in room")
        
        # Forward answer to other players in the room
        for player_id in room.players:
            if player_id != sender_id:
                emit('webrtc_answer', {
                    'from': sender_id,
                    'answer': answer_data
                }, room=player_id)
        
        return websocket_success_response({}, "Answer forwarded")
    
    @staticmethod
    def handle_ice_candidate(room_manager, room_id, sender_id, candidate_data):
        """
        Handle ICE candidate from a peer
        """
        room = room_manager.get_room(room_id)
        if not room:
            return websocket_error_handler("Room not found")
        
        if sender_id not in room.players:
            return websocket_error_handler("Player not in room")
        
        # Forward ICE candidate to other players in the room
        for player_id in room.players:
            if player_id != sender_id:
                emit('ice_candidate', {
                    'from': sender_id,
                    'candidate': candidate_data
                }, room=player_id)
        
        return websocket_success_response({}, "ICE candidate forwarded")


# Example usage patterns for common WebSocket scenarios

def create_basic_websocket_handlers(socketio, namespace, room_manager=None):
    """
    Create basic WebSocket handlers for a page namespace
    
    Usage:
    def register_websocket_handlers(socketio):
        room_manager = WebSocketRoomManager()
        create_basic_websocket_handlers(socketio, '/my-game', room_manager)
    """
    
    if room_manager is None:
        room_manager = WebSocketRoomManager()
    
    @socketio.on('connect', namespace=namespace)
    def on_connect():
        emit('connected', websocket_success_response({
            'namespace': namespace,
            'session_id': request.sid
        }, "Connected to WebSocket"))
    
    @socketio.on('disconnect', namespace=namespace)
    def on_disconnect():
        # Clean up any rooms the user was in
        # This would need to be customized based on how you track user-room relationships
        room_manager.cleanup_empty_rooms()
    
    @socketio.on('join_room', namespace=namespace)
    def on_join_room(data):
        valid, message = validate_websocket_data(data, ['player_id'])
        if not valid:
            return websocket_error_handler(message)
        
        player_id = data['player_id']
        
        # Try to find an available room or create a new one
        room = room_manager.find_available_room()
        if not room:
            room = room_manager.create_room()
        
        success, message = room.add_player(player_id, data.get('player_data'))
        if not success:
            return websocket_error_handler(message)
        
        join_room(room.room_id)
        
        # Notify all players in the room
        broadcast_to_room(room.room_id, 'player_joined', {
            'player_id': player_id,
            'room': room.to_dict()
        }, namespace=namespace)
        
        emit('joined_room', websocket_success_response(room.to_dict()))
    
    return room_manager