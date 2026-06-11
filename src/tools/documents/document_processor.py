"""
Advanced Document Processing Tool for AI Companion
Enhanced document reading, analysis, and processing capabilities
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import tempfile
import mimetypes

class DocumentProcessor:
    """Advanced document processing with multiple format support"""
    
    def __init__(self):
        """Initialize document processor with format support detection"""
        self.supported_formats = {}
        self._detect_format_support()
        print(f"[DOCS] Supported formats: {list(self.supported_formats.keys())}")
    
    def _detect_format_support(self):
        """Detect available document format support"""
        
        # PDF support
        try:
            import PyPDF2
            import pdfplumber
            self.supported_formats['pdf'] = {
                'reader': 'pdfplumber',
                'available': True,
                'description': 'PDF documents with text extraction'
            }
        except ImportError:
            try:
                import PyPDF2
                self.supported_formats['pdf'] = {
                    'reader': 'pypdf2',
                    'available': True,
                    'description': 'PDF documents (basic text extraction)'
                }
            except ImportError:
                self.supported_formats['pdf'] = {'available': False}
        
        # Word documents
        try:
            import python_docx
            self.supported_formats['docx'] = {
                'reader': 'python-docx',
                'available': True,
                'description': 'Microsoft Word documents'
            }
        except ImportError:
            self.supported_formats['docx'] = {'available': False}
        
        # Excel support
        try:
            import openpyxl
            import pandas as pd
            self.supported_formats['xlsx'] = {
                'reader': 'openpyxl',
                'available': True,
                'description': 'Excel spreadsheets'
            }
        except ImportError:
            self.supported_formats['xlsx'] = {'available': False}
        
        # CSV support
        try:
            import pandas as pd
            self.supported_formats['csv'] = {
                'reader': 'pandas',
                'available': True,
                'description': 'Comma-separated values'
            }
        except ImportError:
            self.supported_formats['csv'] = {'available': False}
        
        # PowerPoint support
        try:
            import python_pptx
            self.supported_formats['pptx'] = {
                'reader': 'python-pptx',
                'available': True,
                'description': 'PowerPoint presentations'
            }
        except ImportError:
            self.supported_formats['pptx'] = {'available': False}
        
        # Text files (always available)
        self.supported_formats['txt'] = {
            'reader': 'builtin',
            'available': True,
            'description': 'Plain text files'
        }
        
        # Markdown support
        try:
            import markdown
            self.supported_formats['md'] = {
                'reader': 'markdown',
                'available': True,
                'description': 'Markdown documents'
            }
        except ImportError:
            self.supported_formats['md'] = {
                'reader': 'builtin',
                'available': True,
                'description': 'Markdown as plain text'
            }
    
    def get_supported_formats(self) -> Dict[str, bool]:
        """Get dictionary of supported formats and their availability"""
        return {fmt: info['available'] for fmt, info in self.supported_formats.items()}
    
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """Analyze document structure and metadata"""
        
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {"success": False, "error": "File not found"}
            
            # Basic file info
            stat_info = path.stat()
            mime_type, _ = mimetypes.guess_type(str(path))
            
            analysis = {
                "success": True,
                "filename": path.name,
                "extension": path.suffix.lower(),
                "size_bytes": stat_info.st_size,
                "size_human": self._format_file_size(stat_info.st_size),
                "mime_type": mime_type,
                "last_modified": stat_info.st_mtime,
                "format_supported": path.suffix.lower().lstrip('.') in self.supported_formats
            }
            
            # Format-specific analysis
            file_ext = path.suffix.lower().lstrip('.')
            
            if file_ext == 'pdf':
                analysis.update(self._analyze_pdf(file_path))
            elif file_ext == 'docx':
                analysis.update(self._analyze_docx(file_path))
            elif file_ext in ['xlsx', 'xls']:
                analysis.update(self._analyze_excel(file_path))
            elif file_ext == 'csv':
                analysis.update(self._analyze_csv(file_path))
            elif file_ext == 'pptx':
                analysis.update(self._analyze_powerpoint(file_path))
            elif file_ext in ['txt', 'md']:
                analysis.update(self._analyze_text(file_path))
            
            return analysis
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Document analysis failed: {str(e)}"
            }
    
    def extract_text(self, file_path: str, max_length: int = 50000) -> Dict[str, Any]:
        """Extract text content from document"""
        
        try:
            path = Path(file_path)
            file_ext = path.suffix.lower().lstrip('.')
            
            if file_ext not in self.supported_formats:
                return {
                    "success": False,
                    "error": f"Unsupported format: {file_ext}",
                    "supported_formats": list(self.supported_formats.keys())
                }
            
            if not self.supported_formats[file_ext]['available']:
                return {
                    "success": False,
                    "error": f"Format {file_ext} not available. Install required libraries.",
                    "format_info": self.supported_formats[file_ext]
                }
            
            # Extract based on format
            if file_ext == 'pdf':
                content = self._extract_pdf_text(file_path)
            elif file_ext == 'docx':
                content = self._extract_docx_text(file_path)
            elif file_ext in ['xlsx', 'xls']:
                content = self._extract_excel_text(file_path)
            elif file_ext == 'csv':
                content = self._extract_csv_text(file_path)
            elif file_ext == 'pptx':
                content = self._extract_powerpoint_text(file_path)
            elif file_ext in ['txt', 'md']:
                content = self._extract_text_file(file_path)
            else:
                content = ""
            
            # Limit content length
            if len(content) > max_length:
                content = content[:max_length] + "\n... [Content truncated]"
            
            return {
                "success": True,
                "text": content,
                "length": len(content),
                "format": file_ext,
                "truncated": len(content) >= max_length
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Text extraction failed: {str(e)}"
            }
    
    def summarize_document(self, file_path: str, max_sentences: int = 5) -> Dict[str, Any]:
        """Create a summary of the document content"""
        
        # First extract text
        text_result = self.extract_text(file_path, max_length=20000)
        
        if not text_result["success"]:
            return text_result
        
        text = text_result["text"]
        
        # Simple extractive summarization
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= max_sentences:
            summary = text
        else:
            # Score sentences by position and length
            scored_sentences = []
            for i, sentence in enumerate(sentences):
                score = 0
                
                # Position score (beginning and end are important)
                if i < len(sentences) * 0.3:
                    score += 2
                elif i > len(sentences) * 0.7:
                    score += 1
                
                # Length score (not too short, not too long)
                if 20 < len(sentence) < 150:
                    score += 1
                
                scored_sentences.append((score, sentence))
            
            # Sort by score and take top sentences
            scored_sentences.sort(key=lambda x: x[0], reverse=True)
            top_sentences = [sent for _, sent in scored_sentences[:max_sentences]]
            summary = ' '.join(top_sentences)
        
        return {
            "success": True,
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": round(len(summary) / len(text), 3),
            "sentences_used": min(len(sentences), max_sentences)
        }
    
    def search_in_document(self, file_path: str, search_term: str, context_chars: int = 200) -> Dict[str, Any]:
        """Search for specific terms in document"""
        
        text_result = self.extract_text(file_path)
        
        if not text_result["success"]:
            return text_result
        
        text = text_result["text"].lower()
        search_term_lower = search_term.lower()
        
        # Find all occurrences
        matches = []
        start = 0
        
        while True:
            pos = text.find(search_term_lower, start)
            if pos == -1:
                break
            
            # Extract context around match
            context_start = max(0, pos - context_chars // 2)
            context_end = min(len(text), pos + len(search_term) + context_chars // 2)
            context = text[context_start:context_end]
            
            matches.append({
                "position": pos,
                "context": context,
                "line_number": text[:pos].count('\n') + 1
            })
            
            start = pos + 1
        
        return {
            "success": True,
            "search_term": search_term,
            "matches_found": len(matches),
            "matches": matches[:10],  # Limit to 10 matches
            "total_matches": len(matches)
        }
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    # Format-specific extraction methods
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            if self.supported_formats['pdf']['reader'] == 'pdfplumber':
                import pdfplumber
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                return text
            else:
                import PyPDF2
                text = ""
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"PDF extraction error: {str(e)}"
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            import docx
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"DOCX extraction error: {str(e)}"
    
    def _extract_excel_text(self, file_path: str) -> str:
        """Extract text from Excel file"""
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            return df.to_string()
        except Exception as e:
            return f"Excel extraction error: {str(e)}"
    
    def _extract_csv_text(self, file_path: str) -> str:
        """Extract text from CSV file"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            return df.to_string()
        except Exception as e:
            return f"CSV extraction error: {str(e)}"
    
    def _extract_powerpoint_text(self, file_path: str) -> str:
        """Extract text from PowerPoint"""
        try:
            from pptx import Presentation
            prs = Presentation(file_path)
            text = ""
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
            return text
        except Exception as e:
            return f"PowerPoint extraction error: {str(e)}"
    
    def _extract_text_file(self, file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"Text file extraction error: {str(e)}"
    
    # Format-specific analysis methods
    def _analyze_pdf(self, file_path: str) -> Dict[str, Any]:
        """Analyze PDF document"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return {
                    "pages": len(pdf_reader.pages),
                    "metadata": pdf_reader.metadata or {},
                    "encrypted": pdf_reader.is_encrypted
                }
        except:
            return {"analysis_error": "PDF analysis failed"}
    
    def _analyze_docx(self, file_path: str) -> Dict[str, Any]:
        """Analyze Word document"""
        try:
            import docx
            doc = docx.Document(file_path)
            return {
                "paragraphs": len(doc.paragraphs),
                "tables": len(doc.tables),
                "sections": len(doc.sections)
            }
        except:
            return {"analysis_error": "DOCX analysis failed"}
    
    def _analyze_excel(self, file_path: str) -> Dict[str, Any]:
        """Analyze Excel file"""
        try:
            import pandas as pd
            excel_file = pd.ExcelFile(file_path)
            return {
                "sheets": len(excel_file.sheet_names),
                "sheet_names": excel_file.sheet_names
            }
        except:
            return {"analysis_error": "Excel analysis failed"}
    
    def _analyze_csv(self, file_path: str) -> Dict[str, Any]:
        """Analyze CSV file"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path, nrows=1)  # Just read first row
            return {
                "columns": len(df.columns),
                "column_names": list(df.columns)
            }
        except:
            return {"analysis_error": "CSV analysis failed"}
    
    def _analyze_powerpoint(self, file_path: str) -> Dict[str, Any]:
        """Analyze PowerPoint file"""
        try:
            from pptx import Presentation
            prs = Presentation(file_path)
            return {
                "slides": len(prs.slides)
            }
        except:
            return {"analysis_error": "PowerPoint analysis failed"}
    
    def _analyze_text(self, file_path: str) -> Dict[str, Any]:
        """Analyze text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return {
                "characters": len(content),
                "lines": content.count('\n') + 1,
                "words": len(content.split())
            }
        except:
            return {"analysis_error": "Text analysis failed"}

# Demo function
def demo_document_processing():
    """Demo document processing capabilities"""
    print("📄 Document Processing Demo")
    print("=" * 30)
    
    processor = DocumentProcessor()
    
    # Show supported formats
    print("Supported formats:")
    for fmt, available in processor.get_supported_formats().items():
        status = "✅" if available else "❌"
        print(f"  {status} .{fmt}")
    
    print("\n📝 To test with real documents:")
    print("  processor.extract_text('path/to/document.pdf')")
    print("  processor.summarize_document('path/to/document.docx')")
    print("  processor.search_in_document('path/to/file.txt', 'search term')")

if __name__ == "__main__":
    demo_document_processing()
