# Database Instructions

## Purpose & Overview

The database system provides a thread-safe, file-based NoSQL database for the blog system. It offers page-scoped data namespaces to prevent conflicts between different pages, while also supporting shared global data.

**Key Features:**
- Thread-safe operations with automatic locking
- Page-scoped data isolation (each page has its own namespace)
- JSON file storage for persistence
- Simple API similar to Firestore/MongoDB
- Automatic directory and file creation
- Support for both page-specific and global shared data

## Quick Start

```python
from shared.database import get_db

# Get database instance (singleton)
db = get_db()

# Store page-specific data
db.set_page_data('my-page', 'settings', {'theme': 'dark'})

# Retrieve page-specific data
settings = db.get_page_data('my-page', 'settings', {})

# Add to a collection (list)
db.append_to_page_collection('my-page', 'comments', {
    'user': 'john',
    'text': 'Great post!',
    'timestamp': datetime.now().isoformat()
})
```

## API Reference

### Core Functions

#### `get_db() -> Database`
Returns the singleton database instance. Always use this function to get the database.

#### Page-Scoped Data Operations

#### `get_page_data(page_slug: str, key: str, default=None) -> Any`
Retrieve data for a specific page.

**Parameters:**
- `page_slug`: The page identifier (e.g., 'my-blog-post')
- `key`: The data key/collection name
- `default`: Value returned if key doesn't exist

**Returns:** The stored data or default value

#### `set_page_data(page_slug: str, key: str, data: Any) -> bool`
Store data for a specific page.

**Parameters:**
- `page_slug`: The page identifier
- `key`: The data key/collection name
- `data`: The data to store (must be JSON serializable)

**Returns:** True if successful, False otherwise

#### `append_to_page_collection(page_slug: str, collection: str, item: Any) -> bool`
Add an item to a page-specific collection (treats data as a list).

**Parameters:**
- `page_slug`: The page identifier
- `collection`: The collection name
- `item`: The item to append (must be JSON serializable)

**Returns:** True if successful, False otherwise

#### `list_page_collections(page_slug: str) -> List[str]`
Get all collection names for a specific page.

**Parameters:**
- `page_slug`: The page identifier

**Returns:** List of collection/key names

#### Shared Data Operations

#### `get_shared_data(key: str, default=None) -> Any`
Retrieve global shared data.

**Parameters:**
- `key`: The data key
- `default`: Value returned if key doesn't exist

**Returns:** The stored data or default value

#### `set_shared_data(key: str, data: Any) -> bool`
Store global shared data.

**Parameters:**
- `key`: The data key
- `data`: The data to store (must be JSON serializable)

**Returns:** True if successful, False otherwise

#### Utility Functions

#### `list_pages() -> List[str]`
Get all page slugs that have stored data.

**Returns:** List of page slugs

## Common Patterns

### User Comments System

```python
from shared.database import get_db
from datetime import datetime

def add_comment(page_slug, user_name, comment_text):
    db = get_db()
    
    comment = {
        'id': datetime.now().timestamp(),
        'user': user_name,
        'text': comment_text,
        'timestamp': datetime.now().isoformat(),
        'likes': 0
    }
    
    success = db.append_to_page_collection(page_slug, 'comments', comment)
    return comment if success else None

def get_comments(page_slug):
    db = get_db()
    comments = db.get_page_data(page_slug, 'comments', [])
    
    # Sort by timestamp (newest first)
    comments.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return comments
```

### Page Analytics

```python
def track_page_view(page_slug):
    db = get_db()
    
    # Increment view count
    current_views = db.get_page_data(page_slug, 'views', 0)
    db.set_page_data(page_slug, 'views', current_views + 1)
    
    # Log view with timestamp
    view_log = {
        'timestamp': datetime.now().isoformat(),
        'ip': request.remote_addr if 'request' in globals() else 'unknown'
    }
    db.append_to_page_collection(page_slug, 'view_log', view_log)

def get_page_stats(page_slug):
    db = get_db()
    
    return {
        'views': db.get_page_data(page_slug, 'views', 0),
        'comments': len(db.get_page_data(page_slug, 'comments', [])),
        'last_updated': datetime.now().isoformat()
    }
```

### User Preferences

```python
def save_user_preference(page_slug, user_id, preference_key, value):
    db = get_db()
    
    # Get existing preferences
    preferences = db.get_page_data(page_slug, 'user_preferences', {})
    
    # Initialize user preferences if not exists
    if user_id not in preferences:
        preferences[user_id] = {}
    
    # Update preference
    preferences[user_id][preference_key] = value
    
    # Save back to database
    return db.set_page_data(page_slug, 'user_preferences', preferences)

def get_user_preferences(page_slug, user_id):
    db = get_db()
    preferences = db.get_page_data(page_slug, 'user_preferences', {})
    return preferences.get(user_id, {})
```

### Global Settings

```python
def get_site_config():
    db = get_db()
    return db.get_shared_data('site_config', {
        'title': 'My Blog',
        'description': 'A modular blog system',
        'theme': 'light'
    })

def update_site_config(updates):
    db = get_db()
    config = get_site_config()
    config.update(updates)
    return db.set_shared_data('site_config', config)
```

## Integration Guide

### In Page APIs

```python
"""
API endpoints for my-page
"""

from flask import Blueprint, jsonify, request
from shared.database import get_db
from datetime import datetime

bp = Blueprint('my_page', __name__, url_prefix='/api/my-page')

@bp.route('/data', methods=['GET', 'POST'])
def handle_data():
    db = get_db()
    
    if request.method == 'GET':
        # Get page-specific data
        data = db.get_page_data('my-page', 'user_data', [])
        return jsonify({'data': data, 'count': len(data)})
    
    elif request.method == 'POST':
        # Save new data
        new_entry = request.get_json()
        if not new_entry:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Add metadata
        new_entry['id'] = datetime.now().timestamp()
        new_entry['timestamp'] = datetime.now().isoformat()
        
        # Save to database
        success = db.append_to_page_collection('my-page', 'user_data', new_entry)
        
        if success:
            return jsonify({'success': True, 'entry': new_entry}), 201
        else:
            return jsonify({'error': 'Failed to save data'}), 500
```

### Error Handling

```python
def safe_database_operation(operation_func):
    """Decorator for safe database operations"""
    def wrapper(*args, **kwargs):
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            print(f"Database operation failed: {e}")
            return None
    return wrapper

@safe_database_operation
def get_user_data(page_slug, user_id):
    db = get_db()
    users = db.get_page_data(page_slug, 'users', {})
    return users.get(user_id)
```

## Best Practices

### Do's ✅

1. **Use page-scoped data** for page-specific information
2. **Use consistent naming** for collections (e.g., 'comments', 'user_data', 'settings')
3. **Add timestamps** to entries for chronological sorting
4. **Add unique IDs** to list items for easy reference
5. **Provide defaults** when getting data to avoid KeyError
6. **Use descriptive collection names** that indicate the data type

### Don'ts ❌

1. **Don't store non-JSON serializable data** (functions, complex objects)
2. **Don't use shared data for page-specific information** (causes conflicts)
3. **Don't forget error handling** when database operations might fail
4. **Don't store sensitive data** without proper encryption
5. **Don't create deeply nested structures** (keep it simple)

### Data Structure Guidelines

**Good Examples:**
```python
# Comments collection
{
    'id': 1234567890,
    'user': 'john_doe',
    'text': 'Great post!',
    'timestamp': '2025-01-15T10:30:00',
    'likes': 5
}

# User preferences
{
    'theme': 'dark',
    'notifications': True,
    'language': 'en'
}

# Page settings
{
    'allow_comments': True,
    'moderation_enabled': False,
    'max_comments': 100
}
```

**Avoid:**
```python
# Too nested
{
    'user': {
        'profile': {
            'settings': {
                'notifications': {
                    'email': True
                }
            }
        }
    }
}

# Non-JSON serializable
{
    'callback': lambda x: x + 1,  # Functions don't serialize
    'date': datetime.now()        # Use .isoformat() instead
}
```

### Performance Tips

1. **Batch operations** when possible instead of multiple individual calls
2. **Use appropriate data structures** (lists for collections, dicts for key-value data)
3. **Consider data size** - very large collections might need pagination
4. **Clean up old data** periodically to prevent files from growing too large

### Security Considerations

1. **Validate input data** before storing
2. **Sanitize user-generated content** 
3. **Don't store passwords** or sensitive information in plain text
4. **Use page-scoped data** to prevent unauthorized access between pages
5. **Consider rate limiting** for write operations in public APIs