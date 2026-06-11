"""
Conversation Memory Manager for AI Companion
Handles persistent conversation history across sessions
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import sqlite3


class ConversationMemoryManager:
    """Manages conversation memory with persistent storage"""
    
    def __init__(self, data_dir: str = None):
        """Initialize the memory manager"""
        if data_dir is None:
            data_dir = Path.home() / ".ai_companion" / "memory"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / "conversations.db"
        self.max_memory_days = 30  # Keep conversations for 30 days
        self.max_context_messages = 20  # Keep last 20 messages as context
        
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database for conversation storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                session_id TEXT,
                metadata TEXT
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                context_summary TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_current_session_id(self) -> str:
        """Get or create current session ID"""
        # Use date-based session IDs for simplicity
        return datetime.now().strftime("%Y%m%d")
    
    def save_conversation_turn(self, user_message: str, ai_response: str, metadata: Dict[str, Any] = None):
        """Save a conversation turn to persistent storage"""
        try:
            session_id = self.get_current_session_id()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert conversation turn
            cursor.execute('''
                INSERT INTO conversations (user_message, ai_response, session_id, metadata)
                VALUES (?, ?, ?, ?)
            ''', (user_message, ai_response, session_id, json.dumps(metadata or {})))
            
            # Update session last activity
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (id, last_activity)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            
            print(f"[MEMORY] Saved conversation turn for session {session_id}")
            
        except Exception as e:
            print(f"[MEMORY] Error saving conversation: {e}")
    
    def get_conversation_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get recent conversation history for context"""
        if limit is None:
            limit = self.max_context_messages
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent conversations from current and recent sessions
            cutoff_date = datetime.now() - timedelta(days=7)  # Last 7 days
            
            cursor.execute('''
                SELECT user_message, ai_response, timestamp, metadata
                FROM conversations
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (cutoff_date, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to conversation format (reverse to get chronological order)
            history = []
            for row in reversed(rows):
                user_msg, ai_response, timestamp, metadata_json = row
                
                # Add user message
                history.append({
                    "role": "user",
                    "content": user_msg,
                    "timestamp": timestamp
                })
                
                # Add AI response
                history.append({
                    "role": "assistant", 
                    "content": ai_response,
                    "timestamp": timestamp
                })
            
            print(f"[MEMORY] Retrieved {len(history)} messages from conversation history")
            return history
            
        except Exception as e:
            print(f"[MEMORY] Error retrieving conversation history: {e}")
            return []
    
    def get_conversation_summary(self, days: int = 7) -> str:
        """Get a summary of recent conversations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT user_message, ai_response
                FROM conversations
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (cutoff_date,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return "No recent conversation history."
            
            # Create a simple summary
            topics = []
            for user_msg, ai_response in rows:
                # Extract key topics (simple keyword extraction)
                words = user_msg.lower().split()
                key_words = [w for w in words if len(w) > 4 and w not in ['about', 'could', 'would', 'should', 'please']]
                topics.extend(key_words[:2])  # Take first 2 meaningful words
            
            # Get unique topics
            unique_topics = list(set(topics))[:5]  # Top 5 topics
            
            if unique_topics:
                return f"Recent conversation topics: {', '.join(unique_topics)}"
            else:
                return "Recent general conversation."
                
        except Exception as e:
            print(f"[MEMORY] Error getting conversation summary: {e}")
            return "Unable to retrieve conversation summary."
    
    def clean_old_conversations(self):
        """Clean up old conversations beyond retention period"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=self.max_memory_days)
            
            cursor.execute('''
                DELETE FROM conversations
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            
            # Clean up empty sessions
            cursor.execute('''
                DELETE FROM sessions
                WHERE id NOT IN (SELECT DISTINCT session_id FROM conversations)
            ''')
            
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                print(f"[MEMORY] Cleaned up {deleted_count} old conversation entries")
                
        except Exception as e:
            print(f"[MEMORY] Error cleaning old conversations: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about conversation memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total conversations
            cursor.execute('SELECT COUNT(*) FROM conversations')
            total_conversations = cursor.fetchone()[0]
            
            # Recent conversations (last 7 days)
            cutoff_date = datetime.now() - timedelta(days=7)
            cursor.execute('SELECT COUNT(*) FROM conversations WHERE timestamp > ?', (cutoff_date,))
            recent_conversations = cursor.fetchone()[0]
            
            # Active sessions
            cursor.execute('SELECT COUNT(*) FROM sessions')
            total_sessions = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_conversations": total_conversations,
                "recent_conversations": recent_conversations,
                "total_sessions": total_sessions,
                "memory_enabled": True
            }
            
        except Exception as e:
            print(f"[MEMORY] Error getting memory stats: {e}")
            return {
                "total_conversations": 0,
                "recent_conversations": 0, 
                "total_sessions": 0,
                "memory_enabled": False,
                "error": str(e)
            }


# Global memory manager instance
_memory_manager = None

def get_memory_manager() -> ConversationMemoryManager:
    """Get the global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = ConversationMemoryManager()
    return _memory_manager
