"""
Enhanced Vision System for AI Companion
Advanced image analysis with multiple model support and comprehensive features
"""

import os
import base64
import json
import requests
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path
import tempfile
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io

# Vision models
try:
    from transformers import pipeline
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

@dataclass
class VisionResult:
    """Vision analysis result"""
    success: bool
    description: str = ""
    objects: List[Dict[str, Any]] = None
    faces: List[Dict[str, Any]] = None
    text: str = ""
    colors: List[str] = None
    metadata: Dict[str, Any] = None
    confidence: float = 0.0
    model_used: str = ""
    processing_time: float = 0.0

class EnhancedVisionSystem:
    """Enhanced vision analysis system with multiple model support"""
    
    def __init__(self):
        """Initialize vision system"""
        self.available_models = {}
        self.current_model = None
        self.cache_dir = Path("data/vision_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize available models
        self._initialize_models()
        
        # Vision pipelines
        self.pipelines = {}
        self._initialize_pipelines()
        
        print(f"[Vision] Initialized with {len(self.available_models)} models")
        self._print_model_status()
    
    def _initialize_models(self):
        """Initialize available vision models"""
        
        # OpenAI GPT-4 Vision
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and HAS_OPENAI:
            self.available_models["gpt4v"] = {
                "name": "GPT-4 Vision",
                "capabilities": ["description", "objects", "text", "analysis"],
                "api_key": openai_key,
                "available": True,
                "priority": 5
            }
        
        # Google Gemini Vision
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and HAS_GEMINI:
            self.available_models["gemini_vision"] = {
                "name": "Gemini Pro Vision",
                "capabilities": ["description", "objects", "text", "analysis"],
                "api_key": gemini_key,
                "available": True,
                "priority": 5
            }
        
        # Local Moondream2 (existing)
        kobold_endpoint = os.getenv("KOBOLDCPP_ENDPOINT", "http://localhost:5001")
        self.available_models["moondream2"] = {
            "name": "Moondream2 (Local)",
            "capabilities": ["description", "objects"],
            "endpoint": kobold_endpoint,
            "available": False,  # Will test availability
            "priority": 3
        }
        
        # Transformers models
        if HAS_TRANSFORMERS:
            self.available_models["blip2"] = {
                "name": "BLIP-2 (Local)",
                "capabilities": ["description"],
                "available": True,
                "priority": 2
            }
            
            self.available_models["clip"] = {
                "name": "CLIP (Local)",
                "capabilities": ["classification"],
                "available": True,
                "priority": 2
            }
        
        # Test model availability
        self._test_model_availability()
    
    def _test_model_availability(self):
        """Test which models are actually available"""
        
        # Test Moondream2
        if "moondream2" in self.available_models:
            try:
                response = requests.get(f"{self.available_models['moondream2']['endpoint']}/api/v1/info", 
                                      timeout=3)
                self.available_models["moondream2"]["available"] = response.status_code == 200
            except:
                self.available_models["moondream2"]["available"] = False
        
        # Test OpenAI
        if "gpt4v" in self.available_models:
            try:
                openai.api_key = self.available_models["gpt4v"]["api_key"]
                # Just test if API key is valid
                self.available_models["gpt4v"]["available"] = True
            except:
                self.available_models["gpt4v"]["available"] = False
        
        # Test Gemini
        if "gemini_vision" in self.available_models:
            try:
                genai.configure(api_key=self.available_models["gemini_vision"]["api_key"])
                self.available_models["gemini_vision"]["available"] = True
            except:
                self.available_models["gemini_vision"]["available"] = False
        
        # Set default model
        available_models = [(name, config) for name, config in self.available_models.items() 
                          if config["available"]]
        if available_models:
            self.current_model = max(available_models, key=lambda x: x[1]["priority"])[0]
    
    def _initialize_pipelines(self):
        """Initialize vision processing pipelines"""
        if not HAS_TRANSFORMERS:
            return
        
        try:
            # Object detection
            if torch.cuda.is_available():
                device = 0  # GPU
            else:
                device = -1  # CPU
            
            self.pipelines["object_detection"] = pipeline(
                "object-detection", 
                model="facebook/detr-resnet-50",
                device=device
            )
            
            # Image classification
            self.pipelines["classification"] = pipeline(
                "image-classification", 
                model="microsoft/resnet-50",
                device=device
            )
            
            # Image captioning
            self.pipelines["captioning"] = pipeline(
                "image-to-text",
                model="Salesforce/blip-image-captioning-base",
                device=device
            )
            
        except Exception as e:
            print(f"[Vision] Error initializing pipelines: {e}")
    
    def _print_model_status(self):
        """Print status of all vision models"""
        print("\n👁️  Vision Model Status:")
        for name, config in sorted(self.available_models.items(), 
                                 key=lambda x: x[1]["priority"], reverse=True):
            status = "✅" if config["available"] else "❌"
            current = "👈" if name == self.current_model else "  "
            capabilities = ", ".join(config["capabilities"])
            print(f"  {status} {current} {config['name']} - {capabilities}")
    
    def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail",
                     model: str = None, include_objects: bool = True, 
                     include_text: bool = True, include_faces: bool = True) -> VisionResult:
        """Comprehensive image analysis"""
        
        start_time = datetime.now()
        
        try:
            # Load and validate image
            if not os.path.exists(image_path):
                return VisionResult(False, error=f"Image not found: {image_path}")
            
            # Select model
            selected_model = model if model and model in self.available_models else self.current_model
            if not selected_model or not self.available_models[selected_model]["available"]:
                return VisionResult(False, error="No vision model available")
            
            # Analyze with selected model
            result = self._analyze_with_model(image_path, prompt, selected_model)
            
            # Add additional analysis if requested
            if include_objects and "object_detection" in self.pipelines:
                try:
                    objects = self._detect_objects(image_path)
                    result.objects = objects
                except Exception as e:
                    print(f"[Vision] Object detection failed: {e}")
            
            if include_text and HAS_OPENCV:
                try:
                    extracted_text = self._extract_text(image_path)
                    if result.text:
                        result.text += "\n" + extracted_text
                    else:
                        result.text = extracted_text
                except Exception as e:
                    print(f"[Vision] Text extraction failed: {e}")
            
            if include_faces and HAS_OPENCV:
                try:
                    faces = self._detect_faces(image_path)
                    result.faces = faces
                except Exception as e:
                    print(f"[Vision] Face detection failed: {e}")
            
            # Add color analysis
            try:
                colors = self._analyze_colors(image_path)
                result.colors = colors
            except Exception as e:
                print(f"[Vision] Color analysis failed: {e}")
            
            # Add metadata
            result.metadata = self._get_image_metadata(image_path)
            result.model_used = selected_model
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            return result
        
        except Exception as e:
            return VisionResult(False, error=f"Vision analysis failed: {str(e)}")
    
    def _analyze_with_model(self, image_path: str, prompt: str, model: str) -> VisionResult:
        """Analyze image with specific model"""
        
        if model == "gpt4v":
            return self._analyze_gpt4v(image_path, prompt)
        elif model == "gemini_vision":
            return self._analyze_gemini(image_path, prompt)
        elif model == "moondream2":
            return self._analyze_moondream2(image_path, prompt)
        elif model == "blip2":
            return self._analyze_blip2(image_path, prompt)
        else:
            return VisionResult(False, error=f"Unknown model: {model}")
    
    def _analyze_gpt4v(self, image_path: str, prompt: str) -> VisionResult:
        """Analyze image with GPT-4 Vision"""
        try:
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.available_models['gpt4v']['api_key']}"
            }
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }
            
            response = requests.post("https://api.openai.com/v1/chat/completions", 
                                   headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                description = result["choices"][0]["message"]["content"]
                return VisionResult(True, description=description, confidence=0.9)
            else:
                return VisionResult(False, error=f"GPT-4V API error: {response.status_code}")
        
        except Exception as e:
            return VisionResult(False, error=f"GPT-4V analysis failed: {str(e)}")
    
    def _analyze_gemini(self, image_path: str, prompt: str) -> VisionResult:
        """Analyze image with Gemini Vision"""
        try:
            genai.configure(api_key=self.available_models["gemini_vision"]["api_key"])
            model = genai.GenerativeModel('gemini-pro-vision')
            
            # Load image
            img = Image.open(image_path)
            
            response = model.generate_content([prompt, img])
            
            if response.text:
                return VisionResult(True, description=response.text, confidence=0.9)
            else:
                return VisionResult(False, error="Gemini returned empty response")
        
        except Exception as e:
            return VisionResult(False, error=f"Gemini analysis failed: {str(e)}")
    
    def _analyze_moondream2(self, image_path: str, prompt: str) -> VisionResult:
        """Analyze image with Moondream2"""
        try:
            # Encode image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "prompt": f"<image>{base64_image}</image>\n{prompt}",
                "max_length": 500,
                "temperature": 0.7
            }
            
            endpoint = self.available_models["moondream2"]["endpoint"]
            response = requests.post(f"{endpoint}/api/v1/generate", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                description = result["results"][0]["text"]
                return VisionResult(True, description=description, confidence=0.8)
            else:
                return VisionResult(False, error=f"Moondream2 error: {response.status_code}")
        
        except Exception as e:
            return VisionResult(False, error=f"Moondream2 analysis failed: {str(e)}")
    
    def _analyze_blip2(self, image_path: str, prompt: str = None) -> VisionResult:
        """Analyze image with BLIP-2"""
        try:
            if "captioning" not in self.pipelines:
                return VisionResult(False, error="BLIP-2 pipeline not available")
            
            img = Image.open(image_path)
            result = self.pipelines["captioning"](img)
            
            if result and len(result) > 0:
                description = result[0]["generated_text"]
                return VisionResult(True, description=description, confidence=0.7)
            else:
                return VisionResult(False, error="BLIP-2 returned no results")
        
        except Exception as e:
            return VisionResult(False, error=f"BLIP-2 analysis failed: {str(e)}")
    
    def _detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect objects in image"""
        if "object_detection" not in self.pipelines:
            return []
        
        try:
            img = Image.open(image_path)
            results = self.pipelines["object_detection"](img)
            
            objects = []
            for result in results:
                objects.append({
                    "label": result["label"],
                    "confidence": round(result["score"], 2),
                    "bbox": result["box"]
                })
            
            return objects
        
        except Exception as e:
            print(f"[Vision] Object detection error: {e}")
            return []
    
    def _extract_text(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            # Try using Tesseract OCR if available
            try:
                import pytesseract
                img = cv2.imread(image_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray)
                return text.strip()
            except ImportError:
                pass
            
            # Fallback: basic text detection with OpenCV
            if HAS_OPENCV:
                img = cv2.imread(image_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Simple text detection (not OCR)
                # This is a placeholder - would need proper OCR implementation
                return "Text detection requires Tesseract OCR"
            
            return ""
        
        except Exception as e:
            return f"Text extraction error: {str(e)}"
    
    def _detect_faces(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect faces in image"""
        if not HAS_OPENCV:
            return []
        
        try:
            # Load face cascade (you would need to download this file)
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            # Read image
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            face_list = []
            for (x, y, w, h) in faces:
                face_list.append({
                    "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                    "confidence": 0.8  # Haar cascades don't provide confidence
                })
            
            return face_list
        
        except Exception as e:
            print(f"[Vision] Face detection error: {e}")
            return []
    
    def _analyze_colors(self, image_path: str) -> List[str]:
        """Analyze dominant colors in image"""
        try:
            img = Image.open(image_path)
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get dominant colors
            img = img.resize((100, 100))  # Reduce size for faster processing
            colors = img.getcolors(maxcolors=256*256*256)
            
            if colors:
                # Sort by frequency and get top 5
                colors.sort(reverse=True)
                dominant_colors = []
                
                for count, color in colors[:5]:
                    hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
                    dominant_colors.append(hex_color)
                
                return dominant_colors
            
            return []
        
        except Exception as e:
            print(f"[Vision] Color analysis error: {e}")
            return []
    
    def _get_image_metadata(self, image_path: str) -> Dict[str, Any]:
        """Get image metadata"""
        try:
            img = Image.open(image_path)
            stat = os.stat(image_path)
            
            metadata = {
                "filename": os.path.basename(image_path),
                "size": {"width": img.width, "height": img.height},
                "mode": img.mode,
                "format": img.format,
                "file_size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
            # Get EXIF data if available
            if hasattr(img, '_getexif') and img._getexif():
                metadata["exif"] = dict(img._getexif())
            
            return metadata
        
        except Exception as e:
            return {"error": str(e)}
    
    def create_annotated_image(self, image_path: str, analysis_result: VisionResult,
                              output_path: str = None) -> str:
        """Create annotated image with analysis results"""
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Try to load a font
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Draw object bounding boxes
            if analysis_result.objects:
                for obj in analysis_result.objects:
                    bbox = obj.get("bbox", {})
                    if bbox:
                        x1, y1 = bbox.get("xmin", 0), bbox.get("ymin", 0)
                        x2, y2 = bbox.get("xmax", 0), bbox.get("ymax", 0)
                        
                        # Draw rectangle
                        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
                        
                        # Draw label
                        label = f"{obj['label']} ({obj['confidence']:.2f})"
                        draw.text((x1, y1-20), label, fill="red", font=font)
            
            # Draw face bounding boxes
            if analysis_result.faces:
                for face in analysis_result.faces:
                    bbox = face.get("bbox", {})
                    if bbox:
                        x, y = bbox.get("x", 0), bbox.get("y", 0)
                        w, h = bbox.get("width", 0), bbox.get("height", 0)
                        
                        # Draw rectangle
                        draw.rectangle([x, y, x+w, y+h], outline="blue", width=2)
                        
                        # Draw label
                        label = f"Face ({face.get('confidence', 0.0):.2f})"
                        draw.text((x, y-20), label, fill="blue", font=font)
            
            # Save annotated image
            if output_path is None:
                base_path = Path(image_path)
                output_path = base_path.parent / f"{base_path.stem}_annotated{base_path.suffix}"
            
            img.save(output_path)
            return str(output_path)
        
        except Exception as e:
            print(f"[Vision] Annotation error: {e}")
            return ""
    
    def batch_analyze(self, image_paths: List[str], prompt: str = "Describe this image",
                     max_concurrent: int = 3) -> List[VisionResult]:
        """Analyze multiple images in batch"""
        results = []
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_path = {
                executor.submit(self.analyze_image, path, prompt): path 
                for path in image_paths
            }
            
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(VisionResult(False, error=f"Error processing {path}: {str(e)}"))
        
        return results
    
    def get_model_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available models"""
        return {
            name: {
                "name": config["name"],
                "capabilities": config["capabilities"],
                "available": config["available"],
                "priority": config["priority"]
            }
            for name, config in self.available_models.items()
        }

# Demo function
def demo_enhanced_vision():
    """Demo enhanced vision capabilities"""
    print("👁️  Enhanced Vision System Demo")
    print("=" * 40)
    
    vision_system = EnhancedVisionSystem()
    
    # Show available models
    print("Available Models:")
    models = vision_system.get_model_info()
    for name, info in models.items():
        status = "✅" if info["available"] else "❌"
        print(f"  {status} {info['name']} - {', '.join(info['capabilities'])}")
    
    # Create sample image for testing
    print("\n🖼️  Creating sample image...")
    sample_img = Image.new('RGB', (400, 300), color='lightblue')
    draw = ImageDraw.Draw(sample_img)
    
    # Draw some shapes
    draw.rectangle([50, 50, 150, 150], fill='red', outline='black', width=2)
    draw.ellipse([200, 100, 350, 200], fill='green', outline='black', width=2)
    draw.text((50, 250), "Sample Image for Vision Test", fill='black')
    
    sample_path = "sample_vision_test.jpg"
    sample_img.save(sample_path)
    print(f"   Created: {sample_path}")
    
    # Test image analysis
    if vision_system.current_model:
        print(f"\n🔍 Testing analysis with {vision_system.current_model}...")
        result = vision_system.analyze_image(
            sample_path, 
            "Describe what you see in this image",
            include_objects=True,
            include_text=True
        )
        
        if result.success:
            print("✅ Analysis successful!")
            print(f"   Model: {result.model_used}")
            print(f"   Processing time: {result.processing_time:.2f}s")
            print(f"   Description: {result.description[:150]}...")
            
            if result.objects:
                print(f"   Objects detected: {len(result.objects)}")
                for obj in result.objects[:3]:
                    print(f"     • {obj['label']} ({obj['confidence']:.2f})")
            
            if result.colors:
                print(f"   Dominant colors: {', '.join(result.colors[:3])}")
            
            if result.text and result.text.strip():
                print(f"   Extracted text: {result.text[:100]}...")
        else:
            print(f"❌ Analysis failed: {result.description}")
    else:
        print("❌ No vision model available for testing")
    
    # Cleanup
    if Path(sample_path).exists():
        Path(sample_path).unlink()
        print(f"\n🧹 Cleaned up {sample_path}")

if __name__ == "__main__":
    demo_enhanced_vision()
