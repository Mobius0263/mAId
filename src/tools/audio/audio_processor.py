"""
Audio Processing Tool for AI Companion
Handles speech-to-text, text-to-speech, and audio analysis
"""

import os
import io
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
import tempfile
import wave
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AudioProcessor:
    """Handles audio processing including TTS and STT"""
    
    def __init__(self):
        """Initialize audio processor with available services"""
        self.whisper_available = False
        self.openai_available = False
        self.edge_tts_available = False
        self.pyttsx3_available = False
        
        self._initialize_services()
        print(f"[AUDIO] Available services: {self._get_available_services()}")
    
    def _initialize_services(self):
        """Initialize available audio services"""
        
        # Check OpenAI Whisper for STT
        try:
            import whisper
            self.whisper_model = whisper.load_model("base")
            self.whisper_available = True
            print("✅ Whisper STT loaded")
        except ImportError:
            print("⚠️ Whisper not available. Install with: pip install openai-whisper")
        except Exception as e:
            print(f"⚠️ Whisper failed to load: {e}")
        
        # Check OpenAI API for advanced STT/TTS
        try:
            import openai
            self.openai_key = os.getenv("OPENAI_API_KEY")
            if self.openai_key:
                self.openai_client = openai.OpenAI(api_key=self.openai_key)
                self.openai_available = True
                print("✅ OpenAI Audio API available")
        except ImportError:
            print("⚠️ OpenAI not available. Install with: pip install openai")
        except Exception as e:
            print(f"⚠️ OpenAI setup failed: {e}")
        
        # Check Edge TTS (free, high-quality)
        try:
            import edge_tts
            self.edge_tts_available = True
            print("✅ Edge TTS available")
        except ImportError:
            print("⚠️ Edge TTS not available. Install with: pip install edge-tts")
        
        # Check pyttsx3 (offline backup)
        try:
            import pyttsx3
            self.pyttsx3_engine = pyttsx3.init()
            self.pyttsx3_available = True
            print("✅ Pyttsx3 TTS available")
        except ImportError:
            print("⚠️ Pyttsx3 not available. Install with: pip install pyttsx3")
        except Exception as e:
            print(f"⚠️ Pyttsx3 failed: {e}")
    
    def _get_available_services(self) -> List[str]:
        """Get list of available audio services"""
        services = []
        if self.whisper_available:
            services.append("Whisper STT")
        if self.openai_available:
            services.append("OpenAI Audio")
        if self.edge_tts_available:
            services.append("Edge TTS")
        if self.pyttsx3_available:
            services.append("Pyttsx3 TTS")
        return services if services else ["None available"]
    
    def speech_to_text(self, audio_file_path: str) -> Dict[str, Any]:
        """Convert speech to text using available STT services"""
        
        try:
            # Try OpenAI Whisper API first (if available)
            if self.openai_available:
                try:
                    with open(audio_file_path, 'rb') as audio_file:
                        transcript = self.openai_client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file
                        )
                    return {
                        "success": True,
                        "text": transcript.text,
                        "service": "OpenAI Whisper API",
                        "confidence": 0.95
                    }
                except Exception as e:
                    print(f"[AUDIO] OpenAI API failed: {e}")
            
            # Fallback to local Whisper
            if self.whisper_available:
                try:
                    result = self.whisper_model.transcribe(audio_file_path)
                    return {
                        "success": True,
                        "text": result["text"].strip(),
                        "service": "Local Whisper",
                        "confidence": result.get("confidence", 0.9)
                    }
                except Exception as e:
                    print(f"[AUDIO] Local Whisper failed: {e}")
            
            return {
                "success": False,
                "error": "No STT service available",
                "text": ""
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"STT failed: {str(e)}",
                "text": ""
            }
    
    def text_to_speech(self, text: str, voice: str = "female", output_path: str = None) -> Dict[str, Any]:
        """Convert text to speech using available TTS services"""
        
        try:
            if not output_path:
                output_path = tempfile.mktemp(suffix=".wav")
            
            # Try Edge TTS first (high quality, free)
            if self.edge_tts_available:
                try:
                    return self._edge_tts_generate(text, voice, output_path)
                except Exception as e:
                    print(f"[AUDIO] Edge TTS failed: {e}")
            
            # Try OpenAI TTS
            if self.openai_available:
                try:
                    return self._openai_tts_generate(text, voice, output_path)
                except Exception as e:
                    print(f"[AUDIO] OpenAI TTS failed: {e}")
            
            # Fallback to pyttsx3
            if self.pyttsx3_available:
                try:
                    return self._pyttsx3_generate(text, output_path)
                except Exception as e:
                    print(f"[AUDIO] Pyttsx3 failed: {e}")
            
            return {
                "success": False,
                "error": "No TTS service available",
                "audio_path": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"TTS failed: {str(e)}",
                "audio_path": None
            }
    
    def _edge_tts_generate(self, text: str, voice: str, output_path: str) -> Dict[str, Any]:
        """Generate speech using Edge TTS"""
        import edge_tts
        import asyncio
        
        # Voice mapping
        voice_map = {
            "female": "en-US-JennyNeural",
            "male": "en-US-GuyNeural",
            "british": "en-GB-SoniaNeural",
            "australian": "en-AU-NatashaNeural"
        }
        
        selected_voice = voice_map.get(voice, voice_map["female"])
        
        async def generate():
            communicate = edge_tts.Communicate(text, selected_voice)
            await communicate.save(output_path)
        
        asyncio.run(generate())
        
        return {
            "success": True,
            "audio_path": output_path,
            "service": "Edge TTS",
            "voice": selected_voice
        }
    
    def _openai_tts_generate(self, text: str, voice: str, output_path: str) -> Dict[str, Any]:
        """Generate speech using OpenAI TTS"""
        
        # Voice mapping for OpenAI
        voice_map = {
            "female": "nova",
            "male": "onyx",
            "british": "shimmer",
            "alloy": "alloy"
        }
        
        selected_voice = voice_map.get(voice, "nova")
        
        response = self.openai_client.audio.speech.create(
            model="tts-1",
            voice=selected_voice,
            input=text
        )
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return {
            "success": True,
            "audio_path": output_path,
            "service": "OpenAI TTS",
            "voice": selected_voice
        }
    
    def _pyttsx3_generate(self, text: str, output_path: str) -> Dict[str, Any]:
        """Generate speech using pyttsx3"""
        
        self.pyttsx3_engine.save_to_file(text, output_path)
        self.pyttsx3_engine.runAndWait()
        
        return {
            "success": True,
            "audio_path": output_path,
            "service": "Pyttsx3",
            "voice": "system_default"
        }
    
    def record_audio(self, duration: int = 5, sample_rate: int = 16000) -> Dict[str, Any]:
        """Record audio from microphone"""
        try:
            import sounddevice as sd
            import scipy.io.wavfile as wav
            
            print(f"🎤 Recording audio for {duration} seconds...")
            
            # Record audio
            recording = sd.rec(int(duration * sample_rate), 
                             samplerate=sample_rate, 
                             channels=1, 
                             dtype='int16')
            sd.wait()
            
            # Save to temporary file
            temp_path = tempfile.mktemp(suffix=".wav")
            wav.write(temp_path, sample_rate, recording)
            
            return {
                "success": True,
                "audio_path": temp_path,
                "duration": duration,
                "sample_rate": sample_rate
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "Audio recording requires: pip install sounddevice scipy"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Recording failed: {str(e)}"
            }
    
    def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """Analyze audio file properties"""
        try:
            import wave
            
            with wave.open(audio_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
            
            return {
                "success": True,
                "duration": round(duration, 2),
                "sample_rate": sample_rate,
                "channels": channels,
                "sample_width": sample_width,
                "total_frames": frames
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Audio analysis failed: {str(e)}"
            }

# Demo function
def demo_audio_processing():
    """Demo audio processing capabilities"""
    print("🎵 Audio Processing Demo")
    print("=" * 30)
    
    processor = AudioProcessor()
    
    if not processor._get_available_services():
        print("❌ No audio services available. Install dependencies:")
        print("  pip install openai-whisper edge-tts pyttsx3 sounddevice scipy")
        return
    
    # Test TTS
    print("🔊 Testing Text-to-Speech...")
    tts_result = processor.text_to_speech(
        "Hello! This is a test of the AI Companion audio system. Can you hear me clearly?",
        voice="female"
    )
    
    if tts_result["success"]:
        print(f"✅ TTS successful: {tts_result['service']}")
        print(f"📁 Audio saved to: {tts_result['audio_path']}")
    else:
        print(f"❌ TTS failed: {tts_result['error']}")

if __name__ == "__main__":
    demo_audio_processing()
