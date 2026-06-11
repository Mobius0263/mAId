"""
Enhanced Files I/O Manager for AI Companion
Comprehensive file operations including advanced search, batch processing, and management
"""

import os
import shutil
import json
import csv
import hashlib
import mimetypes
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import zipfile
import tarfile
import tempfile
import threading
import time
import fnmatch
from dataclasses import dataclass
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Advanced file operations
try:
    import filetype
    HAS_FILETYPE = True
except ImportError:
    HAS_FILETYPE = False

try:
    import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False

try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

@dataclass
class FileInfo:
    """Comprehensive file information"""
    path: str
    name: str
    size: int
    modified: datetime
    created: datetime
    extension: str
    mime_type: str
    is_dir: bool
    permissions: str
    hash_md5: Optional[str] = None
    file_type: Optional[str] = None
    parent_dir: str = ""

class AdvancedFileManager:
    """Advanced file operations manager"""
    
    def __init__(self, workspace_path: str = "."):
        """Initialize file manager with workspace"""
        self.workspace = Path(workspace_path).resolve()
        self.operation_history = []
        self.bookmarks = {}
        self.recent_files = []
        self.file_cache = {}
        self.batch_operations = []
        
        # Create necessary directories
        self.temp_dir = self.workspace / "temp"
        self.backup_dir = self.workspace / "backups"
        self.trash_dir = self.workspace / ".trash"
        
        for dir_path in [self.temp_dir, self.backup_dir, self.trash_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print(f"[FileIO] Initialized with workspace: {self.workspace}")
        self._load_bookmarks()
    
    def _load_bookmarks(self):
        """Load bookmarks from file"""
        bookmarks_file = self.workspace / "file_bookmarks.json"
        if bookmarks_file.exists():
            try:
                with open(bookmarks_file, 'r') as f:
                    self.bookmarks = json.load(f)
            except Exception as e:
                print(f"[FileIO] Could not load bookmarks: {e}")
    
    def _save_bookmarks(self):
        """Save bookmarks to file"""
        bookmarks_file = self.workspace / "file_bookmarks.json"
        try:
            with open(bookmarks_file, 'w') as f:
                json.dump(self.bookmarks, f, indent=2)
        except Exception as e:
            print(f"[FileIO] Could not save bookmarks: {e}")
    
    def get_file_info(self, file_path: str, include_hash: bool = False) -> FileInfo:
        """Get comprehensive file information"""
        path = Path(file_path).resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = path.stat()
        
        # Basic info
        info = FileInfo(
            path=str(path),
            name=path.name,
            size=stat.st_size if not path.is_dir() else 0,
            modified=datetime.fromtimestamp(stat.st_mtime),
            created=datetime.fromtimestamp(stat.st_ctime),
            extension=path.suffix.lower(),
            mime_type=mimetypes.guess_type(str(path))[0] or "unknown",
            is_dir=path.is_dir(),
            permissions=oct(stat.st_mode)[-3:],
            parent_dir=str(path.parent)
        )
        
        # Enhanced file type detection
        if HAS_FILETYPE and not info.is_dir:
            try:
                detected = filetype.guess(str(path))
                if detected:
                    info.file_type = detected.extension
                    info.mime_type = detected.mime
            except:
                pass
        
        # Calculate hash if requested and file is not too large
        if include_hash and not info.is_dir and info.size < 100 * 1024 * 1024:  # 100MB limit
            info.hash_md5 = self._calculate_file_hash(str(path))
        
        return info
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def advanced_search(self, 
                       pattern: str = "*",
                       directory: str = None,
                       file_type: str = None,
                       size_range: Tuple[int, int] = None,
                       date_range: Tuple[datetime, datetime] = None,
                       content_search: str = None,
                       include_hidden: bool = False,
                       recursive: bool = True,
                       max_results: int = 1000) -> List[FileInfo]:
        """Advanced file search with multiple criteria"""
        
        search_dir = Path(directory) if directory else self.workspace
        if not search_dir.exists():
            return []
        
        results = []
        searched_count = 0
        
        def search_directory(dir_path: Path, depth: int = 0):
            nonlocal searched_count
            if searched_count >= max_results:
                return
            
            try:
                for item in dir_path.iterdir():
                    if searched_count >= max_results:
                        break
                    
                    # Skip hidden files if not requested
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    
                    try:
                        # Get file info
                        file_info = self.get_file_info(str(item))
                        searched_count += 1
                        
                        # Apply filters
                        if not self._matches_criteria(file_info, pattern, file_type, 
                                                    size_range, date_range, content_search):
                            if recursive and item.is_dir() and depth < 10:  # Limit recursion depth
                                search_directory(item, depth + 1)
                            continue
                        
                        results.append(file_info)
                        
                        # Recurse into directories
                        if recursive and item.is_dir() and depth < 10:
                            search_directory(item, depth + 1)
                    
                    except (PermissionError, OSError):
                        continue  # Skip inaccessible files
            
            except (PermissionError, OSError):
                pass  # Skip inaccessible directories
        
        search_directory(search_dir)
        return results
    
    def _matches_criteria(self, file_info: FileInfo, pattern: str, file_type: str,
                         size_range: Tuple[int, int], date_range: Tuple[datetime, datetime],
                         content_search: str) -> bool:
        """Check if file matches search criteria"""
        
        # Pattern matching (filename)
        if pattern and pattern != "*":
            if not fnmatch.fnmatch(file_info.name.lower(), pattern.lower()):
                return False
        
        # File type matching
        if file_type:
            if file_type.lower() not in [file_info.extension.lower(), 
                                       file_info.mime_type.lower(),
                                       (file_info.file_type or "").lower()]:
                return False
        
        # Size range
        if size_range and not file_info.is_dir:
            min_size, max_size = size_range
            if not (min_size <= file_info.size <= max_size):
                return False
        
        # Date range
        if date_range:
            start_date, end_date = date_range
            if not (start_date <= file_info.modified <= end_date):
                return False
        
        # Content search (for text files)
        if content_search and not file_info.is_dir:
            if not self._search_file_content(file_info.path, content_search):
                return False
        
        return True
    
    def _search_file_content(self, file_path: str, search_term: str) -> bool:
        """Search for text content in file"""
        try:
            # Only search text files and limit file size
            if Path(file_path).stat().st_size > 10 * 1024 * 1024:  # 10MB limit
                return False
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return search_term.lower() in content.lower()
        except:
            return False
    
    def batch_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple file operations in batch"""
        
        results = {
            "success": 0,
            "failed": 0,
            "operations": [],
            "errors": []
        }
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_op = {}
            
            for op in operations:
                op_type = op.get("type")
                
                if op_type == "copy":
                    future = executor.submit(self.copy_file, op["source"], op["destination"])
                elif op_type == "move":
                    future = executor.submit(self.move_file, op["source"], op["destination"])
                elif op_type == "delete":
                    future = executor.submit(self.delete_file, op["path"])
                elif op_type == "rename":
                    future = executor.submit(self.rename_file, op["path"], op["new_name"])
                elif op_type == "create_dir":
                    future = executor.submit(self.create_directory, op["path"])
                else:
                    results["errors"].append(f"Unknown operation: {op_type}")
                    results["failed"] += 1
                    continue
                
                future_to_op[future] = op
            
            # Process results
            for future in as_completed(future_to_op):
                op = future_to_op[future]
                try:
                    result = future.result()
                    if result.get("success", False):
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"{op['type']}: {result.get('error', 'Unknown error')}")
                    
                    results["operations"].append({
                        "operation": op,
                        "result": result
                    })
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"{op['type']}: {str(e)}")
        
        return results
    
    def copy_file(self, source: str, destination: str, 
                  preserve_metadata: bool = True) -> Dict[str, Any]:
        """Copy file or directory with options"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return {"success": False, "error": f"Source not found: {source}"}
            
            # Create destination directory if needed
            if dest_path.is_dir() or str(dest_path).endswith('/'):
                dest_path = dest_path / source_path.name
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path, 
                              copy_function=shutil.copy2 if preserve_metadata else shutil.copy)
            else:
                if preserve_metadata:
                    shutil.copy2(source_path, dest_path)
                else:
                    shutil.copy(source_path, dest_path)
            
            self._log_operation("copy", source, str(dest_path))
            return {"success": True, "destination": str(dest_path)}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Move file or directory"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return {"success": False, "error": f"Source not found: {source}"}
            
            # Create destination directory if needed
            if dest_path.is_dir() or str(dest_path).endswith('/'):
                dest_path = dest_path / source_path.name
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_path), str(dest_path))
            
            self._log_operation("move", source, str(dest_path))
            return {"success": True, "destination": str(dest_path)}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_file(self, file_path: str, use_trash: bool = True) -> Dict[str, Any]:
        """Delete file or directory with trash option"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            if use_trash:
                # Move to trash directory
                trash_name = f"{path.name}_{int(time.time())}"
                trash_path = self.trash_dir / trash_name
                shutil.move(str(path), str(trash_path))
                
                self._log_operation("trash", file_path, str(trash_path))
                return {"success": True, "message": f"Moved to trash: {trash_name}"}
            else:
                # Permanent deletion
                if HAS_SEND2TRASH:
                    send2trash.send2trash(str(path))
                elif path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                
                self._log_operation("delete", file_path)
                return {"success": True, "message": "Permanently deleted"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def rename_file(self, file_path: str, new_name: str) -> Dict[str, Any]:
        """Rename file or directory"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            new_path = path.parent / new_name
            
            if new_path.exists():
                return {"success": False, "error": f"File already exists: {new_name}"}
            
            path.rename(new_path)
            
            self._log_operation("rename", file_path, str(new_path))
            return {"success": True, "new_path": str(new_path)}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_directory(self, dir_path: str, parents: bool = True) -> Dict[str, Any]:
        """Create directory"""
        try:
            path = Path(dir_path)
            
            if path.exists():
                return {"success": False, "error": f"Directory already exists: {dir_path}"}
            
            path.mkdir(parents=parents, exist_ok=False)
            
            self._log_operation("create_dir", dir_path)
            return {"success": True, "path": str(path)}
        
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _resolve_common_location(self, location: str) -> Path:
        """Resolve common human-friendly locations to absolute paths."""
        if not location:
            return self.workspace

        location_lower = location.lower().strip()
        home = Path.home()

        common_locations = {
            "desktop": home / "Desktop",
            "documents": home / "Documents",
            "downloads": home / "Downloads",
            "workspace": self.workspace,
        }

        if location_lower in common_locations:
            return common_locations[location_lower]

        return Path(location).expanduser().resolve()

    def create_file(self, content: str, filename: str, location: str = "desktop", file_type: str = "txt") -> Dict[str, Any]:
        """Create a file with content (backward-compatible API used by orchestrator)."""
        try:
            target_dir = self._resolve_common_location(location)
            target_dir.mkdir(parents=True, exist_ok=True)

            safe_name = filename.strip().strip('"\'')
            if not safe_name:
                safe_name = "document"

            if "." in safe_name:
                safe_name = Path(safe_name).stem

            ext = (file_type or "txt").lower().lstrip(".")
            file_path = target_dir / f"{safe_name}.{ext}"

            if ext == "docx":
                if not HAS_DOCX:
                    return {
                        "success": False,
                        "error": "python-docx is not installed; cannot create .docx files"
                    }

                doc = DocxDocument()
                for line in (content or "").splitlines():
                    if line.strip():
                        doc.add_paragraph(line)
                if not (content or "").strip():
                    doc.add_paragraph(" ")
                doc.save(str(file_path))

            elif ext == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    try:
                        parsed = json.loads(content)
                        json.dump(parsed, f, indent=2, ensure_ascii=False)
                    except Exception:
                        json.dump({"content": content}, f, indent=2, ensure_ascii=False)

            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content or "")

            self._log_operation("create_file", str(file_path))
            return {
                "success": True,
                "file_path": str(file_path),
                "filename": file_path.name,
                "location": str(target_dir),
                "file_type": ext,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_files(self, directory: str, pattern: str = "*", file_type: str = None) -> Dict[str, Any]:
        """Search files (backward-compatible API used by orchestrator)."""
        try:
            results = self.advanced_search(
                pattern=pattern or "*",
                directory=directory,
                file_type=file_type,
                recursive=True,
                max_results=300,
            )

            files = []
            for item in results:
                if item.is_dir:
                    continue
                files.append({
                    "name": item.name,
                    "path": item.path,
                    "size": self._format_size(item.size),
                    "modified": item.modified.isoformat(),
                    "extension": item.extension,
                })

            return {
                "success": True,
                "directory": str(Path(directory).resolve()),
                "pattern": pattern,
                "file_type": file_type,
                "files": files,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "files": []}

    def list_directory(self, directory: str = None) -> Dict[str, Any]:
        """List directory contents (backward-compatible API used by orchestrator)."""
        try:
            target = Path(directory).expanduser().resolve() if directory else self.workspace
            if not target.exists() or not target.is_dir():
                return {"success": False, "error": f"Directory not found: {target}"}

            files = []
            directories = []
            for item in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                if item.is_dir():
                    directories.append(item.name)
                else:
                    item_size = item.stat().st_size if item.exists() else 0
                    files.append({
                        "name": item.name,
                        "path": str(item),
                        "size": self._format_size(item_size),
                    })

            return {
                "success": True,
                "directory": str(target),
                "directories": directories,
                "files": files,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "directories": [], "files": []}
    
    def compress_files(self, files: List[str], output_path: str, 
                      format: str = "zip") -> Dict[str, Any]:
        """Compress files into archive"""
        try:
            output_path = Path(output_path)
            
            if format.lower() == "zip":
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in files:
                        path = Path(file_path)
                        if path.exists():
                            if path.is_file():
                                zipf.write(path, path.name)
                            else:
                                for root, dirs, files_in_dir in os.walk(path):
                                    for file in files_in_dir:
                                        file_full_path = Path(root) / file
                                        arc_name = Path(root).relative_to(path.parent) / file
                                        zipf.write(file_full_path, arc_name)
            
            elif format.lower() in ["tar", "tar.gz", "tgz"]:
                mode = "w:gz" if format.lower() in ["tar.gz", "tgz"] else "w"
                with tarfile.open(output_path, mode) as tar:
                    for file_path in files:
                        path = Path(file_path)
                        if path.exists():
                            tar.add(path, path.name)
            
            else:
                return {"success": False, "error": f"Unsupported format: {format}"}
            
            self._log_operation("compress", str(files), str(output_path))
            return {"success": True, "archive": str(output_path), "size": output_path.stat().st_size}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_archive(self, archive_path: str, destination: str = None) -> Dict[str, Any]:
        """Extract archive file"""
        try:
            archive_path = Path(archive_path)
            
            if not archive_path.exists():
                return {"success": False, "error": f"Archive not found: {archive_path}"}
            
            if destination is None:
                destination = archive_path.parent / archive_path.stem
            else:
                destination = Path(destination)
            
            destination.mkdir(parents=True, exist_ok=True)
            
            if archive_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(destination)
                    extracted_files = zipf.namelist()
            
            elif archive_path.suffix.lower() in ['.tar', '.gz', '.tgz']:
                with tarfile.open(archive_path, 'r:*') as tar:
                    tar.extractall(destination)
                    extracted_files = tar.getnames()
            
            else:
                return {"success": False, "error": f"Unsupported archive format: {archive_path.suffix}"}
            
            self._log_operation("extract", str(archive_path), str(destination))
            return {
                "success": True,
                "destination": str(destination),
                "files_extracted": len(extracted_files)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def backup_file(self, file_path: str, backup_name: str = None) -> Dict[str, Any]:
        """Create backup of file"""
        try:
            source_path = Path(file_path)
            
            if not source_path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{source_path.stem}_backup_{timestamp}{source_path.suffix}"
            
            backup_path = self.backup_dir / backup_name
            
            if source_path.is_dir():
                shutil.copytree(source_path, backup_path)
            else:
                shutil.copy2(source_path, backup_path)
            
            self._log_operation("backup", file_path, str(backup_path))
            return {"success": True, "backup_path": str(backup_path)}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_directory_tree(self, directory: str = None, max_depth: int = 3,
                          include_files: bool = True) -> Dict[str, Any]:
        """Get directory tree structure"""
        root_path = Path(directory) if directory else self.workspace
        
        if not root_path.exists():
            return {"success": False, "error": f"Directory not found: {directory}"}
        
        def build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth > max_depth:
                return {"name": path.name, "type": "truncated"}
            
            tree_node = {
                "name": path.name,
                "path": str(path),
                "type": "directory" if path.is_dir() else "file",
                "size": 0,
                "children": []
            }
            
            if path.is_dir():
                try:
                    total_size = 0
                    for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                        if item.name.startswith('.'):
                            continue  # Skip hidden files
                        
                        if item.is_dir():
                            child_tree = build_tree(item, current_depth + 1)
                            tree_node["children"].append(child_tree)
                            total_size += child_tree.get("size", 0)
                        elif include_files:
                            file_size = item.stat().st_size
                            tree_node["children"].append({
                                "name": item.name,
                                "path": str(item),
                                "type": "file",
                                "size": file_size,
                                "extension": item.suffix.lower()
                            })
                            total_size += file_size
                    
                    tree_node["size"] = total_size
                except PermissionError:
                    tree_node["children"] = [{"name": "Permission denied", "type": "error"}]
            else:
                tree_node["size"] = path.stat().st_size
            
            return tree_node
        
        return {"success": True, "tree": build_tree(root_path)}
    
    def add_bookmark(self, name: str, path: str) -> Dict[str, Any]:
        """Add bookmark for quick access"""
        try:
            path = str(Path(path).resolve())
            self.bookmarks[name] = path
            self._save_bookmarks()
            return {"success": True, "message": f"Bookmark '{name}' added"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_bookmarks(self) -> Dict[str, str]:
        """Get all bookmarks"""
        return self.bookmarks.copy()
    
    def remove_bookmark(self, name: str) -> Dict[str, Any]:
        """Remove bookmark"""
        if name in self.bookmarks:
            del self.bookmarks[name]
            self._save_bookmarks()
            return {"success": True, "message": f"Bookmark '{name}' removed"}
        else:
            return {"success": False, "error": f"Bookmark '{name}' not found"}
    
    def get_operation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent file operations history"""
        return self.operation_history[-limit:]
    
    def _log_operation(self, operation: str, source: str, destination: str = None):
        """Log file operation"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "source": source,
            "destination": destination
        }
        self.operation_history.append(log_entry)
        
        # Keep only last 1000 operations
        if len(self.operation_history) > 1000:
            self.operation_history = self.operation_history[-1000:]
    
    def get_disk_usage(self, directory: str = None) -> Dict[str, Any]:
        """Get disk usage statistics"""
        try:
            path = Path(directory) if directory else self.workspace
            
            if not path.exists():
                return {"success": False, "error": f"Directory not found: {directory}"}
            
            total_size = 0
            file_count = 0
            dir_count = 0
            
            for root, dirs, files in os.walk(path):
                dir_count += len(dirs)
                for file in files:
                    try:
                        file_path = Path(root) / file
                        total_size += file_path.stat().st_size
                        file_count += 1
                    except (OSError, FileNotFoundError):
                        continue
            
            return {
                "success": True,
                "path": str(path),
                "total_size": total_size,
                "total_size_human": self._format_size(total_size),
                "file_count": file_count,
                "directory_count": dir_count
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

# Demo function
def demo_enhanced_file_io():
    """Demo enhanced file I/O capabilities"""
    print("📁 Enhanced Files I/O Demo")
    print("=" * 35)
    
    file_manager = AdvancedFileManager()
    
    # Create sample directory structure
    print("📂 Creating sample directory structure...")
    sample_dir = Path("sample_files")
    sample_dir.mkdir(exist_ok=True)
    
    # Create sample files
    files_to_create = [
        "sample_files/document.txt",
        "sample_files/image.jpg",
        "sample_files/data.csv",
        "sample_files/subfolder/nested.py"
    ]
    
    for file_path in files_to_create:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(f"Sample content for {Path(file_path).name}\n" * 10)
    
    print(f"   Created {len(files_to_create)} sample files")
    
    # Test file info
    print("\n📋 File Information:")
    for file_path in files_to_create[:2]:  # Test first 2 files
        try:
            info = file_manager.get_file_info(file_path, include_hash=True)
            print(f"   • {info.name}: {info.size} bytes, {info.extension}, {info.hash_md5[:8]}...")
        except Exception as e:
            print(f"   • Error with {file_path}: {e}")
    
    # Test advanced search
    print("\n🔍 Advanced Search:")
    search_results = file_manager.advanced_search(
        pattern="*.txt",
        directory="sample_files",
        recursive=True,
        max_results=10
    )
    print(f"   Found {len(search_results)} text files:")
    for result in search_results:
        print(f"     • {result.name} ({result.size} bytes)")
    
    # Test directory tree
    print("\n🌳 Directory Tree:")
    tree_result = file_manager.get_directory_tree("sample_files", max_depth=2)
    if tree_result["success"]:
        def print_tree(node, indent=0):
            prefix = "  " * indent
            size_str = f" ({file_manager._format_size(node['size'])})" if node.get('size', 0) > 0 else ""
            print(f"{prefix}• {node['name']}{size_str}")
            for child in node.get('children', []):
                print_tree(child, indent + 1)
        
        print_tree(tree_result["tree"])
    
    # Test compression
    print("\n🗜️  Testing compression...")
    compress_result = file_manager.compress_files(
        ["sample_files/document.txt", "sample_files/data.csv"],
        "sample_archive.zip"
    )
    if compress_result["success"]:
        print(f"   ✅ Created archive: {compress_result['archive']} ({file_manager._format_size(compress_result['size'])})")
    else:
        print(f"   ❌ Compression failed: {compress_result['error']}")
    
    # Test disk usage
    print("\n💾 Disk Usage:")
    usage_result = file_manager.get_disk_usage("sample_files")
    if usage_result["success"]:
        print(f"   Total size: {usage_result['total_size_human']}")
        print(f"   Files: {usage_result['file_count']}")
        print(f"   Directories: {usage_result['directory_count']}")
    
    # Test bookmarks
    print("\n🔖 Bookmarks:")
    file_manager.add_bookmark("samples", str(Path("sample_files").resolve()))
    bookmarks = file_manager.get_bookmarks()
    for name, path in bookmarks.items():
        print(f"   • {name}: {path}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    if sample_dir.exists():
        shutil.rmtree(sample_dir)
    if Path("sample_archive.zip").exists():
        Path("sample_archive.zip").unlink()
    print("   Sample files cleaned up")

if __name__ == "__main__":
    demo_enhanced_file_io()
