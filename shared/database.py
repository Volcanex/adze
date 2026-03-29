"""
Simple NoSQL database implementation using JSON files.
Mimics Firestore-like structure with page-scoped collections.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading

class SimpleNoSQLDB:
    """
    File-based NoSQL database with page-scoped data storage.
    Data structure: data/{page_slug}/{collection_name}.json
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
    
    def _get_page_dir(self, page_slug: str) -> Path:
        """Get the directory for a specific page's data"""
        page_dir = self.data_dir / page_slug
        page_dir.mkdir(exist_ok=True)
        return page_dir
    
    def _get_collection_file(self, page_slug: str, collection: str) -> Path:
        """Get the file path for a specific collection within a page"""
        return self._get_page_dir(page_slug) / f"{collection}.json"
    
    def _read_collection(self, page_slug: str, collection: str) -> Any:
        """Read data from a collection file"""
        file_path = self._get_collection_file(page_slug, collection)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _write_collection(self, page_slug: str, collection: str, data: Any) -> bool:
        """Write data to a collection file"""
        file_path = self._get_collection_file(page_slug, collection)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, TypeError):
            return False
    
    def get_page_data(self, page_slug: str, collection: str, default: Any = None) -> Any:
        """
        Get data from a page's collection.
        
        Args:
            page_slug: The page identifier (e.g., 'first-post')
            collection: The collection name (e.g., 'comments', 'metadata')
            default: Default value if data doesn't exist
        
        Returns:
            The stored data or default value
        """
        with self._lock:
            data = self._read_collection(page_slug, collection)
            return data if data is not None else default
    
    def set_page_data(self, page_slug: str, collection: str, data: Any) -> bool:
        """
        Set data for a page's collection.
        
        Args:
            page_slug: The page identifier
            collection: The collection name
            data: The data to store
        
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            return self._write_collection(page_slug, collection, data)
    
    def append_to_page_collection(self, page_slug: str, collection: str, item: Any) -> bool:
        """
        Append an item to a page's collection (treating collection as a list).
        
        Args:
            page_slug: The page identifier
            collection: The collection name
            item: The item to append
        
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            current_data = self._read_collection(page_slug, collection)
            if current_data is None:
                current_data = []
            elif not isinstance(current_data, list):
                # If it's not a list, make it one
                current_data = [current_data]
            
            current_data.append(item)
            return self._write_collection(page_slug, collection, current_data)
    
    def delete_page_data(self, page_slug: str, collection: str) -> bool:
        """
        Delete a collection from a page.
        
        Args:
            page_slug: The page identifier
            collection: The collection name
        
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            file_path = self._get_collection_file(page_slug, collection)
            try:
                if file_path.exists():
                    file_path.unlink()
                return True
            except IOError:
                return False
    
    def list_page_collections(self, page_slug: str) -> List[str]:
        """
        List all collections for a page.
        
        Args:
            page_slug: The page identifier
        
        Returns:
            List of collection names
        """
        page_dir = self._get_page_dir(page_slug)
        collections = []
        
        for file_path in page_dir.glob("*.json"):
            collections.append(file_path.stem)
        
        return collections
    
    def list_pages(self) -> List[str]:
        """
        List all pages that have data.
        
        Returns:
            List of page slugs
        """
        pages = []
        
        for page_dir in self.data_dir.iterdir():
            if page_dir.is_dir():
                pages.append(page_dir.name)
        
        return pages
    
    def get_shared_data(self, collection: str, default: Any = None) -> Any:
        """
        Get shared data (not tied to any specific page).
        
        Args:
            collection: The collection name
            default: Default value if data doesn't exist
        
        Returns:
            The stored data or default value
        """
        return self.get_page_data('shared', collection, default)
    
    def set_shared_data(self, collection: str, data: Any) -> bool:
        """
        Set shared data (not tied to any specific page).
        
        Args:
            collection: The collection name
            data: The data to store
        
        Returns:
            True if successful, False otherwise
        """
        return self.set_page_data('shared', collection, data)

# Global database instance
_db_instance = None

def get_db() -> SimpleNoSQLDB:
    """Get the global database instance (singleton pattern)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SimpleNoSQLDB()
    return _db_instance