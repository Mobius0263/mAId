"""
Code Interpreter Tool for AI Companion
Safe code execution environment with multiple language support
"""

import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import shutil

class CodeInterpreter:
    """Safe code execution environment supporting multiple languages"""
    
    def __init__(self):
        """Initialize code interpreter with security settings"""
        self.supported_languages = {
            'python': {
                'extension': '.py',
                'command': 'python',
                'timeout': 30,
                'available': self._check_python()
            },
            'javascript': {
                'extension': '.js',
                'command': 'node',
                'timeout': 30,
                'available': self._check_node()
            },
            'bash': {
                'extension': '.sh',
                'command': 'bash',
                'timeout': 15,
                'available': self._check_bash()
            },
            'powershell': {
                'extension': '.ps1',
                'command': 'powershell',
                'timeout': 15,
                'available': self._check_powershell()
            }
        }
        
        # Security restrictions
        self.blocked_imports = {
            'python': ['os', 'subprocess', 'sys', 'shutil', '__import__', 'eval', 'exec'],
            'javascript': ['fs', 'child_process', 'os', 'process'],
            'bash': ['rm', 'sudo', 'chmod', 'chown', 'dd', 'mkfs'],
            'powershell': ['Remove-Item', 'Set-ExecutionPolicy', 'Invoke-Command']
        }
        
        self.max_output_size = 10000  # 10KB max output
        self.working_directory = self._create_sandbox()
        
        print(f"[CODE] Available languages: {self._get_available_languages()}")
        print(f"[CODE] Sandbox: {self.working_directory}")
    
    def _check_python(self) -> bool:
        """Check if Python is available"""
        try:
            result = subprocess.run(['python', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_node(self) -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_bash(self) -> bool:
        """Check if Bash is available"""
        try:
            result = subprocess.run(['bash', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_powershell(self) -> bool:
        """Check if PowerShell is available"""
        try:
            result = subprocess.run(['powershell', '-Command', 'echo "test"'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _get_available_languages(self) -> List[str]:
        """Get list of available programming languages"""
        return [lang for lang, config in self.supported_languages.items() 
                if config['available']]
    
    def _create_sandbox(self) -> str:
        """Create a secure sandbox directory for code execution"""
        sandbox_dir = tempfile.mkdtemp(prefix="ai_code_sandbox_")
        return sandbox_dir
    
    def _security_check(self, code: str, language: str) -> Dict[str, Any]:
        """Perform security checks on code before execution"""
        
        blocked = self.blocked_imports.get(language, [])
        code_lower = code.lower()
        
        # Check for blocked imports/commands
        for blocked_item in blocked:
            if blocked_item.lower() in code_lower:
                return {
                    "safe": False,
                    "reason": f"Blocked item detected: {blocked_item}",
                    "category": "import_restriction"
                }
        
        # Check for file system operations
        dangerous_patterns = [
            'open(', 'file(', 'write', 'delete', 'remove',
            'mkdir', 'rmdir', 'chmod', 'system('
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return {
                    "safe": False,
                    "reason": f"Potentially dangerous operation: {pattern}",
                    "category": "filesystem_access"
                }
        
        # Check code length (prevent resource exhaustion)
        if len(code) > 50000:  # 50KB max
            return {
                "safe": False,
                "reason": "Code too long (max 50KB)",
                "category": "size_limit"
            }
        
        return {"safe": True, "reason": "Code passed security checks"}
    
    def execute_code(self, code: str, language: str = 'python', 
                    input_data: str = None) -> Dict[str, Any]:
        """Execute code safely in sandbox environment"""
        
        # Validate language support
        if language not in self.supported_languages:
            return {
                "success": False,
                "error": f"Unsupported language: {language}",
                "available_languages": list(self.supported_languages.keys())
            }
        
        lang_config = self.supported_languages[language]
        
        if not lang_config['available']:
            return {
                "success": False,
                "error": f"{language} interpreter not available",
                "suggestion": f"Install {language} to enable code execution"
            }
        
        # Security check
        security_result = self._security_check(code, language)
        if not security_result["safe"]:
            return {
                "success": False,
                "error": f"Security check failed: {security_result['reason']}",
                "category": security_result.get("category", "security")
            }
        
        try:
            # Create temporary file for code
            code_file = os.path.join(
                self.working_directory, 
                f"code_{int(time.time())}{lang_config['extension']}"
            )
            
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Prepare execution command
            if language == 'python':
                command = [sys.executable, code_file]
            else:
                command = [lang_config['command'], code_file]
            
            # Execute code
            start_time = time.time()
            
            process = subprocess.run(
                command,
                cwd=self.working_directory,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=lang_config['timeout']
            )
            
            execution_time = time.time() - start_time
            
            # Get output (limit size)
            stdout = process.stdout
            stderr = process.stderr
            
            if len(stdout) > self.max_output_size:
                stdout = stdout[:self.max_output_size] + "\n... [Output truncated]"
            
            if len(stderr) > self.max_output_size:
                stderr = stderr[:self.max_output_size] + "\n... [Error truncated]"
            
            # Clean up
            try:
                os.remove(code_file)
            except:
                pass
            
            return {
                "success": True,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": process.returncode,
                "execution_time": round(execution_time, 3),
                "language": language,
                "code_file": os.path.basename(code_file)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Code execution timed out after {lang_config['timeout']} seconds",
                "timeout": lang_config['timeout']
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "language": language
            }
    
    def install_package(self, package_name: str, language: str = 'python') -> Dict[str, Any]:
        """Install package in sandbox environment"""
        
        if language == 'python':
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package_name,
                    '--target', os.path.join(self.working_directory, 'packages')
                ], capture_output=True, text=True, timeout=60)
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "package": package_name
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "Package installation timed out"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Installation failed: {str(e)}"
                }
        
        elif language == 'javascript':
            try:
                result = subprocess.run([
                    'npm', 'install', package_name
                ], cwd=self.working_directory, 
                   capture_output=True, text=True, timeout=60)
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "package": package_name
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"NPM installation failed: {str(e)}"
                }
        
        return {
            "success": False,
            "error": f"Package installation not supported for {language}"
        }
    
    def create_visualization(self, data: Dict[str, Any], chart_type: str = 'bar') -> Dict[str, Any]:
        """Create data visualization using matplotlib"""
        
        code = f"""
import matplotlib.pyplot as plt
import json
import base64
from io import BytesIO

# Data provided by user
data = {json.dumps(data)}

plt.figure(figsize=(10, 6))

if '{chart_type}' == 'bar':
    if isinstance(data, dict):
        keys = list(data.keys())
        values = list(data.values())
        plt.bar(keys, values)
        plt.title('Bar Chart')
    else:
        print("Error: Bar chart requires dictionary data")
        
elif '{chart_type}' == 'line':
    if isinstance(data, dict):
        keys = list(data.keys())
        values = list(data.values())
        plt.plot(keys, values, marker='o')
        plt.title('Line Chart')
    else:
        print("Error: Line chart requires dictionary data")

elif '{chart_type}' == 'pie':
    if isinstance(data, dict):
        labels = list(data.keys())
        sizes = list(data.values())
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title('Pie Chart')
    else:
        print("Error: Pie chart requires dictionary data")

plt.tight_layout()

# Save plot to base64 string
buffer = BytesIO()
plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()
print(f"CHART_DATA:{{image_base64}}")
plt.close()
"""
        
        result = self.execute_code(code, 'python')
        
        if result["success"] and "CHART_DATA:" in result["stdout"]:
            try:
                chart_data = result["stdout"].split("CHART_DATA:")[1].strip()
                return {
                    "success": True,
                    "chart_base64": chart_data,
                    "chart_type": chart_type
                }
            except:
                pass
        
        return {
            "success": False,
            "error": "Failed to generate chart",
            "details": result
        }
    
    def cleanup(self):
        """Clean up sandbox directory"""
        try:
            shutil.rmtree(self.working_directory)
            print(f"[CODE] Cleaned up sandbox: {self.working_directory}")
        except Exception as e:
            print(f"[CODE] Cleanup warning: {e}")

# Demo function
def demo_code_interpreter():
    """Demo code interpretation capabilities"""
    print("💻 Code Interpreter Demo")
    print("=" * 30)
    
    interpreter = CodeInterpreter()
    
    # Test Python code
    python_code = """
print("Hello from Python!")
result = 2 + 2
print(f"2 + 2 = {result}")

# Simple calculation
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(f"Sum of {numbers} = {total}")
"""
    
    print("🐍 Testing Python code...")
    result = interpreter.execute_code(python_code, 'python')
    
    if result["success"]:
        print("✅ Python execution successful!")
        print(f"Output: {result['stdout']}")
        print(f"Execution time: {result['execution_time']}s")
    else:
        print(f"❌ Python execution failed: {result['error']}")
    
    # Test data visualization
    if 'python' in interpreter._get_available_languages():
        print("\n📊 Testing data visualization...")
        sample_data = {
            "Python": 45,
            "JavaScript": 30,
            "Java": 15,
            "C++": 10
        }
        
        chart_result = interpreter.create_visualization(sample_data, 'bar')
        if chart_result["success"]:
            print("✅ Chart generation successful!")
            print(f"Chart data length: {len(chart_result['chart_base64'])} characters")
        else:
            print(f"❌ Chart generation failed: {chart_result['error']}")
    
    # Cleanup
    interpreter.cleanup()

if __name__ == "__main__":
    demo_code_interpreter()
