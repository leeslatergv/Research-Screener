"""
Script to create a standalone executable for the Research Screener
"""
import os
import sys
import subprocess

def create_executable():
    # Install PyInstaller if not already installed
    print("Installing/updating PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"])
    
    # Create a spec file first for better control
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['research_screener.py'],
    pathex=[],
    binaries=[],
    datas=[('scholar_results.json', '.')],
    hiddenimports=['dash', 'dash_bootstrap_components', 'pandas'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ResearchScreener',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Changed to True so you can see any errors
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    # Write spec file
    with open('ResearchScreener.spec', 'w') as f:
        f.write(spec_content)
    
    print("\nCreating executable...")
    
    # Run PyInstaller with the spec file
    subprocess.check_call([sys.executable, "-m", "PyInstaller", "ResearchScreener.spec"])
    
    print("\nExecutable created successfully!")
    print("Look for 'ResearchScreener.exe' in the 'dist' folder")
    
    # Create a simple batch file to run it
    batch_content = '''@echo off
cd /d "%~dp0"
start "" "dist\\ResearchScreener.exe"
'''
    with open('Run_ResearchScreener.bat', 'w') as f:
        f.write(batch_content)
    
    print("\nAlso created 'Run_ResearchScreener.bat' for easy launching")

if __name__ == "__main__":
    try:
        create_executable()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTrying alternative method...")
        
        # If PyInstaller fails, create a simple launcher
        launcher_content = '''import subprocess
import sys
import os

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Run the app
subprocess.call([sys.executable, "research_screener.py"])
'''
        with open('launcher.pyw', 'w') as f:
            f.write(launcher_content)
        
        print("Created 'launcher.pyw' - double-click this to run the app")
        
        # Also create a batch file
        batch_content = '''@echo off
cd /d "%~dp0"
python research_screener.py
pause
'''
        with open('Run_Screener.bat', 'w') as f:
            f.write(batch_content)
        
        print("Also created 'Run_Screener.bat' as an alternative")