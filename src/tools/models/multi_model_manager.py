"""
Multi-Model Switching Manager for AI Companion
Manages multiple AI model connections and intelligent switching
"""

import os
import json
import requests
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ModelType(Enum):
    """Available model types"""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    KOBOLDCPP = "koboldcpp"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"

@dataclass
class ModelConfig:
    """Configuration for a model"""
    name: str
    model_type: ModelType
    endpoint: str
    api_key: Optional[str]
    model_id: str
    context_length: int
    supports_vision: bool = False
    supports_tools: bool = False
    supports_streaming: bool = False
    cost_per_1k_tokens: float = 0.0
    available: bool = True
    priority: int = 1  # Higher = preferred
    specialties: List[str] = None

class MultiModelManager:
    """Manages multiple AI models with intelligent switching"""
    
    def __init__(self, config_file: str = None):
        """Initialize multi-model manager"""
        self.models: Dict[str, ModelConfig] = {}
        self.current_model = None
        self.conversation_history = []
        self.model_stats = {}
        
        # Load configuration
        if config_file and os.path.exists(config_file):
            self._load_config(config_file)
        else:
            self._initialize_default_models()
        
        # Test model availability
        self._test_model_availability()
        
        print(f"[MultiModel] Initialized with {len(self.models)} models")
        self._print_model_status()
    
    def _initialize_default_models(self):
        """Initialize default model configurations"""
        
        # Gemini models
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            self.models["gemini-pro"] = ModelConfig(
                name="Gemini Pro",
                model_type=ModelType.GEMINI,
                endpoint="https://generativelanguage.googleapis.com/v1beta",
                api_key=gemini_api_key,
                model_id="gemini-1.5-pro-latest",
                context_length=2000000,
                supports_vision=True,
                supports_tools=True,
                supports_streaming=True,
                priority=5,
                specialties=["general", "reasoning", "vision", "tools"]
            )
            
            self.models["gemini-flash"] = ModelConfig(
                name="Gemini Flash",
                model_type=ModelType.GEMINI,
                endpoint="https://generativelanguage.googleapis.com/v1beta",
                api_key=gemini_api_key,
                model_id="gemini-1.5-flash-latest",
                context_length=1000000,
                supports_vision=True,
                supports_tools=True,
                supports_streaming=True,
                priority=4,
                specialties=["fast", "general", "vision"]
            )
        
        # OpenAI models
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.models["gpt-4"] = ModelConfig(
                name="GPT-4",
                model_type=ModelType.OPENAI,
                endpoint="https://api.openai.com/v1",
                api_key=openai_api_key,
                model_id="gpt-4-turbo-preview",
                context_length=128000,
                supports_vision=True,
                supports_tools=True,
                supports_streaming=True,
                cost_per_1k_tokens=0.03,
                priority=4,
                specialties=["reasoning", "code", "analysis"]
            )
            
            self.models["gpt-3.5-turbo"] = ModelConfig(
                name="GPT-3.5 Turbo",
                model_type=ModelType.OPENAI,
                endpoint="https://api.openai.com/v1",
                api_key=openai_api_key,
                model_id="gpt-3.5-turbo-0125",
                context_length=16385,
                supports_tools=True,
                supports_streaming=True,
                cost_per_1k_tokens=0.001,
                priority=2,
                specialties=["fast", "general", "code"]
            )
        
        # Anthropic models
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            self.models["claude-3-sonnet"] = ModelConfig(
                name="Claude 3 Sonnet",
                model_type=ModelType.ANTHROPIC,
                endpoint="https://api.anthropic.com/v1",
                api_key=anthropic_api_key,
                model_id="claude-3-sonnet-20240229",
                context_length=200000,
                supports_vision=True,
                supports_streaming=True,
                cost_per_1k_tokens=0.015,
                priority=4,
                specialties=["reasoning", "analysis", "writing"]
            )
        
        # KoboldCPP (local)
        kobold_endpoint = os.getenv("KOBOLDCPP_ENDPOINT", "http://localhost:5001")
        self.models["koboldcpp"] = ModelConfig(
            name="KoboldCPP Local",
            model_type=ModelType.KOBOLDCPP,
            endpoint=kobold_endpoint,
            api_key=None,
            model_id="local",
            context_length=8192,
            supports_streaming=True,
            priority=1,
            specialties=["local", "private"]
        )
        
        # Ollama models
        ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        self.models["llama3"] = ModelConfig(
            name="Llama 3 (Ollama)",
            model_type=ModelType.OLLAMA,
            endpoint=ollama_endpoint,
            api_key=None,
            model_id="llama3:latest",
            context_length=8192,
            supports_streaming=True,
            priority=2,
            specialties=["local", "general"]
        )
    
    def _test_model_availability(self):
        """Test which models are actually available"""
        for model_name, config in self.models.items():
            try:
                if config.model_type == ModelType.GEMINI:
                    # Test Gemini
                    if config.api_key:
                        genai.configure(api_key=config.api_key)
                        model = genai.GenerativeModel(config.model_id)
                        response = model.generate_content("Hi", 
                            generation_config=genai.types.GenerationConfig(max_output_tokens=1))
                        config.available = True
                    else:
                        config.available = False
                
                elif config.model_type == ModelType.OPENAI:
                    # Test OpenAI
                    if config.api_key:
                        headers = {"Authorization": f"Bearer {config.api_key}"}
                        response = requests.get(f"{config.endpoint}/models", 
                                              headers=headers, timeout=5)
                        config.available = response.status_code == 200
                    else:
                        config.available = False
                
                elif config.model_type == ModelType.ANTHROPIC:
                    # Test Anthropic
                    if config.api_key:
                        headers = {
                            "x-api-key": config.api_key,
                            "anthropic-version": "2023-06-01"
                        }
                        # Just test if we can reach the API
                        config.available = bool(config.api_key)
                    else:
                        config.available = False
                
                elif config.model_type in [ModelType.KOBOLDCPP, ModelType.OLLAMA]:
                    # Test local models
                    try:
                        if config.model_type == ModelType.KOBOLDCPP:
                            response = requests.get(f"{config.endpoint}/api/v1/info", timeout=3)
                        else:  # Ollama
                            response = requests.get(f"{config.endpoint}/api/tags", timeout=3)
                        config.available = response.status_code == 200
                    except:
                        config.available = False
                
            except Exception as e:
                print(f"[MultiModel] Model {model_name} unavailable: {str(e)}")
                config.available = False
        
        # Set current model to highest priority available model
        available_models = [(name, config) for name, config in self.models.items() 
                           if config.available]
        if available_models:
            self.current_model = max(available_models, key=lambda x: x[1].priority)[0]
            print(f"[MultiModel] Default model: {self.current_model}")
    
    def _print_model_status(self):
        """Print status of all models"""
        print("\n📊 Model Status:")
        for name, config in sorted(self.models.items(), 
                                 key=lambda x: x[1].priority, reverse=True):
            status = "✅" if config.available else "❌"
            current = "👈" if name == self.current_model else "  "
            specialties = ", ".join(config.specialties or [])
            print(f"  {status} {current} {config.name} ({config.model_type.value}) - {specialties}")
    
    def get_available_models(self) -> List[Tuple[str, ModelConfig]]:
        """Get list of available models"""
        return [(name, config) for name, config in self.models.items() 
                if config.available]
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a specific model"""
        if model_name in self.models and self.models[model_name].available:
            old_model = self.current_model
            self.current_model = model_name
            print(f"[MultiModel] Switched from {old_model} to {model_name}")
            return True
        else:
            print(f"[MultiModel] Model {model_name} not available")
            return False
    
    def auto_select_model(self, task_type: str, context_length: int = 0, 
                         needs_vision: bool = False, needs_tools: bool = False) -> str:
        """Automatically select best model for task"""
        
        available_models = self.get_available_models()
        if not available_models:
            return None
        
        # Filter by requirements
        suitable_models = []
        for name, config in available_models:
            if needs_vision and not config.supports_vision:
                continue
            if needs_tools and not config.supports_tools:
                continue
            if context_length > config.context_length:
                continue
            
            # Score based on specialties
            score = config.priority
            if config.specialties:
                if task_type in config.specialties:
                    score += 2
                elif any(spec in task_type.lower() for spec in config.specialties):
                    score += 1
            
            suitable_models.append((name, config, score))
        
        if not suitable_models:
            # Fallback to any available model
            return available_models[0][0]
        
        # Select highest scoring model
        best_model = max(suitable_models, key=lambda x: x[2])
        selected_model = best_model[0]
        
        if selected_model != self.current_model:
            self.switch_model(selected_model)
        
        return selected_model
    
    def generate_response(self, prompt: str, model_name: str = None, 
                         system_prompt: str = None, max_tokens: int = 1000,
                         temperature: float = 0.7) -> Dict[str, Any]:
        """Generate response using specified or current model"""
        
        if model_name and model_name != self.current_model:
            if not self.switch_model(model_name):
                return {"success": False, "error": f"Model {model_name} not available"}
        
        if not self.current_model:
            return {"success": False, "error": "No model available"}
        
        config = self.models[self.current_model]
        
        try:
            start_time = time.time()
            
            if config.model_type == ModelType.GEMINI:
                response = self._generate_gemini(prompt, system_prompt, max_tokens, temperature)
            elif config.model_type == ModelType.OPENAI:
                response = self._generate_openai(prompt, system_prompt, max_tokens, temperature)
            elif config.model_type == ModelType.ANTHROPIC:
                response = self._generate_anthropic(prompt, system_prompt, max_tokens, temperature)
            elif config.model_type == ModelType.KOBOLDCPP:
                response = self._generate_koboldcpp(prompt, max_tokens, temperature)
            elif config.model_type == ModelType.OLLAMA:
                response = self._generate_ollama(prompt, max_tokens, temperature)
            else:
                return {"success": False, "error": f"Model type {config.model_type} not implemented"}
            
            response_time = time.time() - start_time
            
            # Update statistics
            if self.current_model not in self.model_stats:
                self.model_stats[self.current_model] = {
                    "requests": 0, "total_time": 0, "errors": 0
                }
            
            stats = self.model_stats[self.current_model]
            stats["requests"] += 1
            stats["total_time"] += response_time
            
            if response["success"]:
                response["model"] = self.current_model
                response["response_time"] = round(response_time, 2)
                return response
            else:
                stats["errors"] += 1
                return response
        
        except Exception as e:
            print(f"[MultiModel] Error with {self.current_model}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_gemini(self, prompt: str, system_prompt: str = None, 
                        max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate response using Gemini"""
        config = self.models[self.current_model]
        
        genai.configure(api_key=config.api_key)
        model = genai.GenerativeModel(config.model_id, 
                                    system_instruction=system_prompt)
        
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature
        )
        
        response = model.generate_content(prompt, generation_config=generation_config)
        
        return {
            "success": True,
            "response": response.text,
            "tokens_used": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
        }
    
    def _generate_openai(self, prompt: str, system_prompt: str = None,
                        max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        config = self.models[self.current_model]
        
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": config.model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(f"{config.endpoint}/chat/completions",
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "response": result["choices"][0]["message"]["content"],
                "tokens_used": result.get("usage", {}).get("total_tokens", 0)
            }
        else:
            return {"success": False, "error": f"OpenAI API error: {response.status_code}"}
    
    def _generate_anthropic(self, prompt: str, system_prompt: str = None,
                          max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate response using Anthropic Claude"""
        config = self.models[self.current_model]
        
        headers = {
            "x-api-key": config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": config.model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            data["system"] = system_prompt
        
        response = requests.post(f"{config.endpoint}/messages",
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "response": result["content"][0]["text"],
                "tokens_used": result.get("usage", {}).get("input_tokens", 0) + 
                              result.get("usage", {}).get("output_tokens", 0)
            }
        else:
            return {"success": False, "error": f"Anthropic API error: {response.status_code}"}
    
    def _generate_koboldcpp(self, prompt: str, max_tokens: int = 1000, 
                           temperature: float = 0.7) -> Dict[str, Any]:
        """Generate response using KoboldCPP"""
        config = self.models[self.current_model]
        
        data = {
            "prompt": prompt,
            "max_context_length": config.context_length,
            "max_length": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "typical": 1.0,
            "rep_pen": 1.1
        }
        
        response = requests.post(f"{config.endpoint}/api/v1/generate",
                               json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "response": result["results"][0]["text"],
                "tokens_used": 0  # KoboldCPP doesn't return token count
            }
        else:
            return {"success": False, "error": f"KoboldCPP error: {response.status_code}"}
    
    def _generate_ollama(self, prompt: str, max_tokens: int = 1000,
                        temperature: float = 0.7) -> Dict[str, Any]:
        """Generate response using Ollama"""
        config = self.models[self.current_model]
        
        data = {
            "model": config.model_id,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        response = requests.post(f"{config.endpoint}/api/generate",
                               json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "response": result["response"],
                "tokens_used": 0  # Ollama doesn't always return token count
            }
        else:
            return {"success": False, "error": f"Ollama error: {response.status_code}"}
    
    def get_model_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all models"""
        stats = {}
        for model_name, model_stats in self.model_stats.items():
            avg_time = (model_stats["total_time"] / model_stats["requests"] 
                       if model_stats["requests"] > 0 else 0)
            success_rate = ((model_stats["requests"] - model_stats["errors"]) / 
                           model_stats["requests"] if model_stats["requests"] > 0 else 1.0)
            
            stats[model_name] = {
                "requests": model_stats["requests"],
                "avg_response_time": round(avg_time, 2),
                "success_rate": round(success_rate * 100, 1),
                "errors": model_stats["errors"]
            }
        
        return stats
    
    def save_config(self, config_file: str):
        """Save current configuration to file"""
        config_data = {
            "models": {},
            "current_model": self.current_model
        }
        
        for name, config in self.models.items():
            config_data["models"][name] = {
                "name": config.name,
                "model_type": config.model_type.value,
                "endpoint": config.endpoint,
                "model_id": config.model_id,
                "context_length": config.context_length,
                "supports_vision": config.supports_vision,
                "supports_tools": config.supports_tools,
                "supports_streaming": config.supports_streaming,
                "priority": config.priority,
                "specialties": config.specialties
            }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

# Demo function
def demo_multi_model():
    """Demo multi-model switching capabilities"""
    print("🔄 Multi-Model Manager Demo")
    print("=" * 35)
    
    manager = MultiModelManager()
    
    # Show available models
    print("\n📋 Available Models:")
    available = manager.get_available_models()
    for name, config in available:
        print(f"  • {config.name} ({config.model_type.value})")
        print(f"    Specialties: {', '.join(config.specialties or ['general'])}")
        print(f"    Context: {config.context_length:,} tokens")
    
    if not available:
        print("❌ No models available - check your API keys!")
        return
    
    # Test auto-selection
    print("\n🤖 Testing auto-selection:")
    
    test_cases = [
        ("coding", "Write a Python function", False, False),
        ("reasoning", "Explain quantum physics", False, False),
        ("vision", "Analyze this image", True, False),
        ("fast", "Quick response needed", False, False)
    ]
    
    for task_type, prompt, needs_vision, needs_tools in test_cases:
        selected = manager.auto_select_model(task_type, needs_vision=needs_vision, 
                                           needs_tools=needs_tools)
        if selected:
            config = manager.models[selected]
            print(f"  Task: {task_type} → {config.name}")
        else:
            print(f"  Task: {task_type} → No suitable model")
    
    # Test response generation
    print("\n💬 Testing response generation...")
    if manager.current_model:
        result = manager.generate_response("Hello! What's your name?", max_tokens=50)
        if result["success"]:
            print(f"✅ Response from {result['model']}:")
            print(f"   {result['response'][:100]}...")
            print(f"   Time: {result['response_time']}s")
        else:
            print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    demo_multi_model()
