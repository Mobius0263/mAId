"""
Chat History Management System
Manages multiple conversation sessions like browser tabs
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid


@dataclass
class ChatSession:
    """Individual chat session data"""
    id: str
    name: str
    created_at: str
    last_updated: str
    conversation_history: List[Dict[str, Any]]
    character_name: str = "Spectre"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create from dictionary"""
        return cls(**data)


class ChatHistoryManager:
    """Manages multiple chat sessions and history persistence"""
    
    def __init__(self, history_dir: str = None):
        """Initialize chat history manager"""
        if history_dir is None:
            history_dir = Path.home() / ".ai_companion" / "chat_history"
        
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        self.sessions: Dict[str, ChatSession] = {}
        self.current_session_id: Optional[str] = None
        
        self._load_sessions()
        
        # Create default session if none exist
        if not self.sessions:
            self.create_new_session("Welcome Chat")
    
    def _load_sessions(self):
        """Load all chat sessions from disk"""
        sessions_file = self.history_dir / "sessions.json"
        
        if sessions_file.exists():
            try:
                with open(sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                
                for session_data in sessions_data.get("sessions", []):
                    session = ChatSession.from_dict(session_data)
                    self.sessions[session.id] = session
                
                # Load current session ID
                self.current_session_id = sessions_data.get("current_session_id")
                
                # Validate current session exists
                if self.current_session_id not in self.sessions:
                    self.current_session_id = None
                    
            except Exception as e:
                print(f"[CHAT_HISTORY] Error loading sessions: {e}")
    
    def _save_sessions(self):
        """Save all chat sessions to disk"""
        sessions_file = self.history_dir / "sessions.json"
        
        try:
            sessions_data = {
                "current_session_id": self.current_session_id,
                "sessions": [session.to_dict() for session in self.sessions.values()]
            }
            
            with open(sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[CHAT_HISTORY] Error saving sessions: {e}")
    
    def create_new_session(self, name: str = None) -> str:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        
        if name is None:
            name = f"Chat {len(self.sessions) + 1}"
        
        session = ChatSession(
            id=session_id,
            name=name,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            conversation_history=[],
            character_name="Spectre"
        )
        
        self.sessions[session_id] = session
        self.current_session_id = session_id
        self._save_sessions()
        
        print(f"[CHAT_HISTORY] Created new session: {name} ({session_id})")
        return session_id
    
    def switch_session(self, session_id: str) -> bool:
        """Switch to a different chat session"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            self._save_sessions()
            print(f"[CHAT_HISTORY] Switched to session: {self.sessions[session_id].name}")
            return True
        else:
            print(f"[CHAT_HISTORY] Session not found: {session_id}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        if session_id not in self.sessions:
            return False
        
        session_name = self.sessions[session_id].name
        del self.sessions[session_id]
        
        # If we deleted the current session, switch to another or create new
        if self.current_session_id == session_id:
            if self.sessions:
                # Switch to the first available session
                self.current_session_id = list(self.sessions.keys())[0]
            else:
                # Create a new default session
                self.create_new_session("New Chat")
        
        self._save_sessions()
        print(f"[CHAT_HISTORY] Deleted session: {session_name}")
        return True
    
    def rename_session(self, session_id: str, new_name: str) -> bool:
        """Rename a chat session"""
        if session_id in self.sessions:
            self.sessions[session_id].name = new_name
            self.sessions[session_id].last_updated = datetime.now().isoformat()
            self._save_sessions()
            return True
        return False
    
    def get_current_session(self) -> Optional[ChatSession]:
        """Get the current active session"""
        if self.current_session_id and self.current_session_id in self.sessions:
            return self.sessions[self.current_session_id]
        return None
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a specific session by ID"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions with basic info"""
        sessions_info = []
        for session in self.sessions.values():
            sessions_info.append({
                "id": session.id,
                "name": session.name,
                "created_at": session.created_at,
                "last_updated": session.last_updated,
                "message_count": len(session.conversation_history),
                "character_name": session.character_name,
                "is_current": session.id == self.current_session_id
            })
        
        # Sort by last updated (most recent first)
        sessions_info.sort(key=lambda x: x["last_updated"], reverse=True)
        return sessions_info
    
    def update_current_session_history(self, conversation_history: List[Dict[str, Any]]):
        """Update the conversation history for the current session"""
        current_session = self.get_current_session()
        if current_session:
            current_session.conversation_history = conversation_history.copy()
            current_session.last_updated = datetime.now().isoformat()
            self._save_sessions()
    
    def load_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Load conversation history for a specific session"""
        session = self.get_session(session_id)
        if session:
            return session.conversation_history.copy()
        return []
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about chat sessions"""
        total_sessions = len(self.sessions)
        total_messages = sum(len(session.conversation_history) for session in self.sessions.values())
        
        if self.sessions:
            latest_session = max(self.sessions.values(), key=lambda s: s.last_updated)
            oldest_session = min(self.sessions.values(), key=lambda s: s.created_at)
        else:
            latest_session = oldest_session = None
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "latest_session": latest_session.name if latest_session else None,
            "oldest_session": oldest_session.name if oldest_session else None,
            "current_session": self.get_current_session().name if self.get_current_session() else None
        }


# Global chat history manager instance
_chat_history_manager = None

def get_chat_history_manager() -> ChatHistoryManager:
    """Get the global chat history manager instance"""
    global _chat_history_manager
    if _chat_history_manager is None:
        _chat_history_manager = ChatHistoryManager()
    return _chat_history_manager
