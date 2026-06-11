# 🚀 How to Build the AI Companion Executable

## Method 1: Using the Batch Files (Recommended)

### Simple Build (Excludes problematic packages):
```powershell
.\build_simple.bat
```

### Full Build (Includes all packages, may fail with PyTorch):
```powershell
.\build_executable.bat
```

## Method 2: Direct PowerShell Commands

```powershell
# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Install build tools
pip install cx_Freeze

# Build using the simple configuration
python build_exe_simple.py build

# Or build using the full configuration
python build_exe.py build
```

## Method 3: Running from Command Prompt

```cmd
# Navigate to project directory
cd "c:\Users\user\Documents\AI Companion Project"

# Run the simple build
.\build_simple.bat

# Or run individual commands
call .venv\Scripts\activate.bat
pip install cx_Freeze
python build_exe_simple.py build
```

## Method 4: Direct Python Command

```powershell
# From the project root directory
python -m cx_Freeze ai_companion_launcher.py --target-dir=dist --target-name=AI_Companion.exe
```

## After Building

The executable will be created in the `dist\` folder:
- **Main executable**: `dist\AI_Companion.exe`
- **Required files**: All dependencies are included in the `dist` folder

## Running the Executable

### From Terminal:
```powershell
cd dist
.\AI_Companion.exe
```

### From File Explorer:
- Navigate to the `dist` folder
- Double-click `AI_Companion.exe`

## Troubleshooting

### If the build fails with PyTorch errors:
- Use `build_simple.bat` instead of `build_executable.bat`
- The simple build excludes PyTorch and other heavy ML packages

### If the executable doesn't start:
1. Check that KoboldCPP is running on localhost:5001
2. Make sure all required files are in the `dist` folder
3. Run from terminal to see any error messages

### Alternative Build Tools:
If cx_Freeze fails, you can try:
```powershell
pip install auto-py-to-exe
auto-py-to-exe
```
This opens a GUI where you can configure the build settings manually.

## Distribution

The entire `dist` folder can be copied to another Windows machine and the executable will run independently (no Python installation required on the target machine).

## Success! ✅

Your AI Companion is now available as a standalone executable in the `dist` folder. The build process successfully:
- ✅ Created `AI_Companion.exe` 
- ✅ Included all necessary Python libraries
- ✅ Packaged the GUI application
- ✅ Fixed path resolution issues for executable environment
- ✅ Made it ready for distribution

## Fixed Issues

The initial build had a `NotADirectoryError` with library.zip paths. This was resolved by:
1. **Creating a dedicated executable launcher** (`ai_companion_exe.py`) optimized for frozen environments
2. **Updating build configuration** to avoid zip packaging issues
3. **Improving path resolution** for both development and executable environments

## Current Status

✅ **Working executable** at `dist\AI_Companion.exe`  
✅ **Proper error handling** with user-friendly dialogs  
✅ **Path resolution** works correctly in executable environment  
✅ **All dependencies** included and working
