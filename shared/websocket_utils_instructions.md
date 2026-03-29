# WebSocket Utils Instructions

## Purpose & Overview

The `websocket_utils.py` module provides utilities for real-time features, multiplayer games, and live interactions using WebSockets. It includes room management, P2P connection helpers, and common patterns for WebSocket development.

**Key Features:**
- Room/lobby management system for multiplayer scenarios
- WebRTC P2P connection coordination helpers  
- Standard error handling and response formatting
- Input validation and broadcasting utilities
- Ready-to-use patterns for common WebSocket use cases

**When to Use:**
- Building real-time multiplayer games
- Creating live chat or comment systems
- Implementing collaborative tools
- Setting up P2P connections with server coordination
- Any feature requiring real-time bidirectional communication

## Quick Start

```python
from shared.websocket_utils import WebSocketRoomManager, websocket_success_response
from flask_socketio import emit

# Initialize room manager for your page
room_manager = WebSocketRoomManager()

def register_websocket_handlers(socketio):
    
    @socketio.on('connect', namespace='/my-game')
    def on_connect():
        emit('connected', websocket_success_response({
            'message': 'Welcome to my game!'
        }))
    
    @socketio.on('find_match', namespace='/my-game')
    def find_match(data):
        player_id = data.get('player_id')
        
        # Find or create a room
        room = room_manager.find_available_room(max_players=2)
        if not room:
            room = room_manager.create_room(max_players=2)
        
        # Add player and notify
        room.add_player(player_id)
        emit('match_found', websocket_success_response(room.to_dict()))
```

## API Reference

### WebSocketRoom Class

Represents a single room/lobby where players can join.

#### `__init__(room_id=None, max_players=2)`
Create a new room.

**Parameters:**
- `room_id`: Optional custom room ID (generates UUID if None)
- `max_players`: Maximum number of players allowed (default: 2)

#### `add_player(player_id: str, player_data=None) -> Tuple[bool, str]`
Add a player to the room.

**Parameters:**
- `player_id`: Unique identifier for the player
- `player_data`: Optional dictionary of player information

**Returns:** `(success: bool, message: str)`

#### `remove_player(player_id: str) -> bool`
Remove a player from the room.

**Returns:** True if player was removed, False if not found

#### `get_player_count() -> int`
Get current number of players in the room.

#### `is_full() -> bool`
Check if room is at maximum capacity.

#### `to_dict() -> dict`
Convert room to dictionary for JSON serialization.

**Room Attributes:**
- `room_id`: Unique room identifier
- `max_players`: Maximum player capacity
- `players`: Dictionary of player data
- `status`: Current room status ('waiting', 'active', 'finished')
- `created_at`: Room creation timestamp
- `data`: Custom room data dictionary

### WebSocketRoomManager Class

Manages multiple rooms for a page/namespace.

#### `create_room(room_id=None, max_players=2) -> WebSocketRoom`
Create and register a new room.

#### `get_room(room_id: str) -> WebSocketRoom | None`
Get a room by its ID.

#### `find_available_room(max_players=2) -> WebSocketRoom | None`
Find a waiting room with available space.

#### `remove_room(room_id: str) -> bool`
Remove a room from management.

#### `cleanup_empty_rooms() -> int`
Remove all rooms with no players. Returns number of rooms removed.

#### `get_stats() -> dict`
Get statistics about managed rooms.

**Returns:**
```python
{
    'total_rooms': int,
    'waiting_rooms': int,
    'active_rooms': int,
    'total_players': int
}
```

### Helper Functions

#### `websocket_error_handler(error_message: str, emit_to_sender=True) -> dict`
Standard error response formatting.

#### `websocket_success_response(data: any, message="Success") -> dict`
Standard success response formatting.

#### `broadcast_to_room(room_id: str, event: str, data: dict, include_sender=True, namespace=None)`
Broadcast event to all players in a room.

#### `validate_websocket_data(data: dict, required_fields: List[str]) -> Tuple[bool, str]`
Validate incoming WebSocket data for required fields.

### P2PConnectionHelper Class

Static methods for WebRTC P2P connection setup.

#### `handle_webrtc_offer(room_manager, room_id, sender_id, offer_data)`
Forward WebRTC offer between peers in a room.

#### `handle_webrtc_answer(room_manager, room_id, sender_id, answer_data)`
Forward WebRTC answer between peers in a room.

#### `handle_ice_candidate(room_manager, room_id, sender_id, candidate_data)`
Forward ICE candidate between peers in a room.

## Common Patterns

### Basic Multiplayer Game Lobby

```python
from shared.websocket_utils import WebSocketRoomManager, websocket_success_response
from flask_socketio import emit, join_room, leave_room

room_manager = WebSocketRoomManager()

def register_websocket_handlers(socketio):
    
    @socketio.on('join_lobby', namespace='/my-game')
    def join_lobby(data):
        player_id = data.get('player_id')
        
        # Join the general lobby room
        join_room('lobby')
        
        # Send lobby statistics
        stats = room_manager.get_stats()
        emit('lobby_joined', websocket_success_response(stats))
    
    @socketio.on('find_match', namespace='/my-game')
    def find_match(data):
        player_id = data.get('player_id')
        player_name = data.get('player_name', 'Anonymous')
        
        # Try to find available room
        room = room_manager.find_available_room(max_players=2)
        if not room:
            room = room_manager.create_room(max_players=2)
        
        # Add player to room
        success, message = room.add_player(player_id, {
            'name': player_name,
            'joined_at': datetime.now().isoformat()
        })
        
        if not success:
            emit('error', {'message': message})
            return
        
        # Join the room
        join_room(room.room_id)
        leave_room('lobby')
        
        # Notify all players in room
        emit('player_joined', {
            'player_id': player_id,
            'player_name': player_name,
            'room': room.to_dict()
        }, room=room.room_id)
        
        # Start game if room is full
        if room.is_full():
            room.status = 'active'
            emit('game_start', room.to_dict(), room=room.room_id)
```

### P2P Game with WebRTC

```python
from shared.websocket_utils import P2PConnectionHelper

def register_websocket_handlers(socketio):
    
    @socketio.on('webrtc_offer', namespace='/my-game')
    def handle_offer(data):
        result = P2PConnectionHelper.handle_webrtc_offer(
            room_manager,
            data['room_id'],
            data['sender_id'], 
            data['offer']
        )
        if 'error' in result:
            emit('error', result)
    
    @socketio.on('webrtc_answer', namespace='/my-game')
    def handle_answer(data):
        P2PConnectionHelper.handle_webrtc_answer(
            room_manager,
            data['room_id'],
            data['sender_id'],
            data['answer']
        )
    
    @socketio.on('ice_candidate', namespace='/my-game')
    def handle_ice_candidate(data):
        P2PConnectionHelper.handle_ice_candidate(
            room_manager,
            data['room_id'],
            data['sender_id'],
            data['candidate']
        )
```

### Live Chat System

```python
from shared.database import get_db
from shared.websocket_utils import validate_websocket_data, websocket_error_handler

def register_websocket_handlers(socketio):
    
    @socketio.on('join_chat', namespace='/my-blog-post')
    def join_chat(data):
        room_name = 'chat_room'
        join_room(room_name)
        
        # Get recent messages
        db = get_db()
        messages = db.get_page_data('my-blog-post', 'chat_messages', [])
        recent_messages = messages[-20:] if messages else []
        
        emit('chat_joined', websocket_success_response({
            'recent_messages': recent_messages,
            'room': room_name
        }))
    
    @socketio.on('send_message', namespace='/my-blog-post')
    def send_message(data):
        # Validate input
        valid, message = validate_websocket_data(data, ['user', 'text'])
        if not valid:
            return websocket_error_handler(message)
        
        # Create message object
        message_obj = {
            'id': datetime.now().timestamp(),
            'user': data['user'],
            'text': data['text'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to database
        db = get_db()
        db.append_to_page_collection('my-blog-post', 'chat_messages', message_obj)
        
        # Broadcast to all users in chat
        emit('new_message', message_obj, room='chat_room')
```

### Live Data Dashboard

```python
def register_websocket_handlers(socketio):
    
    @socketio.on('subscribe_updates', namespace='/dashboard')
    def subscribe_updates(data):
        join_room('live_updates')
        
        # Send current data
        db = get_db()
        current_data = db.get_page_data('dashboard', 'metrics', {})
        emit('current_data', websocket_success_response(current_data))
    
    @socketio.on('unsubscribe_updates', namespace='/dashboard')
    def unsubscribe_updates():
        leave_room('live_updates')

# In your regular API endpoint that updates data:
@bp.route('/update-metrics', methods=['POST'])
def update_metrics():
    # Update database
    db = get_db()
    new_metrics = request.get_json()
    db.set_page_data('dashboard', 'metrics', new_metrics)
    
    # Notify WebSocket subscribers
    from flask import current_app
    socketio = current_app.extensions['socketio']
    socketio.emit('data_updated', new_metrics, 
                  room='live_updates', namespace='/dashboard')
    
    return jsonify({'success': True})
```

## Integration Guide

### Page API Integration

```python
"""
API endpoints for my-realtime-page
"""

from flask import Blueprint, jsonify, request
from flask_socketio import emit
from shared.websocket_utils import WebSocketRoomManager, websocket_success_response
from shared.database import get_db

bp = Blueprint('my_realtime_page', __name__, url_prefix='/api/my-realtime-page')
room_manager = WebSocketRoomManager()

# Regular HTTP API endpoints
@bp.route('/stats')
def get_stats():
    return jsonify(room_manager.get_stats())

# WebSocket handlers
def register_websocket_handlers(socketio):
    
    @socketio.on('connect', namespace='/my-realtime-page')
    def on_connect():
        emit('connected', websocket_success_response({
            'message': 'Connected to realtime page',
            'server_time': datetime.now().isoformat()
        }))
    
    @socketio.on('disconnect', namespace='/my-realtime-page') 
    def on_disconnect():
        # Cleanup
        room_manager.cleanup_empty_rooms()
        print(f"Client disconnected, {room_manager.get_stats()['total_players']} players remaining")
```

### Frontend Integration

```html
<script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
<script>
// Connect to WebSocket namespace
const socket = io('/my-game');

socket.on('connected', (data) => {
    console.log('Connected:', data);
    showStatus('Connected to game server');
});

socket.on('player_joined', (data) => {
    console.log('Player joined:', data);
    updatePlayerList(data.room.players);
});

socket.on('game_start', (data) => {
    console.log('Game starting:', data);
    initializeGame(data.room);
});

// Game actions
function findMatch() {
    socket.emit('find_match', {
        player_id: generatePlayerId(),
        player_name: document.getElementById('playerName').value
    });
}

function sendGameMove(moveData) {
    socket.emit('game_move', {
        room_id: currentRoomId,
        player_id: myPlayerId,
        move: moveData
    });
}
</script>
```

## Best Practices

### Do's ✅

1. **Use page-specific namespaces** (e.g., `/my-game`, `/chat-room`)
2. **Clean up on disconnect** - remove players from rooms, cleanup resources
3. **Validate all incoming data** using `validate_websocket_data()`
4. **Use room management** for multiplayer scenarios
5. **Provide meaningful error messages** with `websocket_error_handler()`
6. **Use consistent event naming** across your application
7. **Handle connection failures gracefully** on the frontend
8. **Limit room sizes** appropriately for your use case

### Don'ts ❌

1. **Don't forget to handle disconnections** - clean up player state
2. **Don't trust client data** - always validate on the server
3. **Don't create unlimited rooms** - implement cleanup mechanisms
4. **Don't send large payloads** through WebSocket - use HTTP for big data
5. **Don't use WebSocket for everything** - HTTP is better for simple request/response
6. **Don't forget error handling** on both client and server
7. **Don't hardcode room IDs** - use the room manager system

### Performance Tips

1. **Use rooms efficiently** - join/leave rooms as needed, don't stay in unused rooms
2. **Broadcast sparingly** - only send updates when necessary
3. **Cleanup regularly** - use `cleanup_empty_rooms()` periodically
4. **Validate early** - reject invalid requests before processing
5. **Consider rate limiting** for high-frequency events
6. **Use P2P for game data** - keep server coordination minimal

### Security Considerations

1. **Validate player identity** - ensure players are who they claim to be
2. **Sanitize user input** - never trust data from clients
3. **Rate limit connections** - prevent spam and abuse
4. **Use authentication** for sensitive operations
5. **Don't expose internal room data** - filter what gets sent to clients
6. **Log suspicious activity** - monitor for unusual patterns

### Error Handling Patterns

```python
# Always validate input
@socketio.on('my_event', namespace='/my-page')
def handle_event(data):
    valid, message = validate_websocket_data(data, ['required_field'])
    if not valid:
        return websocket_error_handler(message)
    
    try:
        # Process event
        result = process_event(data)
        emit('event_result', websocket_success_response(result))
    except Exception as e:
        emit('error', websocket_error_handler(f"Processing failed: {str(e)}"))

# Handle room operations safely
def safe_room_operation(room_id, player_id, operation):
    room = room_manager.get_room(room_id)
    if not room:
        return websocket_error_handler("Room not found")
    
    if player_id not in room.players:
        return websocket_error_handler("Player not in room")
    
    try:
        return operation(room, player_id)
    except Exception as e:
        return websocket_error_handler(f"Operation failed: {str(e)}")
```