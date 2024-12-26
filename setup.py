from cx_Freeze import setup, Executable
import sys
import os
import site

# Application metadata
app_name = "Super UAC Admin"
version = "0.1"
description = "Secret UAC Level At Windows Which Fully Avoids Disabling UAC"
author = "Emirhan Ucan"

def include_files():
    # Find the pywin32_system32 directory
    pywin32_system32 = None
    for path in site.getsitepackages():
        potential_path = os.path.join(path, "pywin32_system32")
        if os.path.exists(potential_path):
            pywin32_system32 = potential_path
            break

    if pywin32_system32 is None:
        raise FileNotFoundError("pywin32_system32 directory not found. Ensure pywin32 is installed.")

    # Include all DLLs from pywin32_system32
    pywin32_files = [(os.path.join(pywin32_system32, file), file) for file in os.listdir(pywin32_system32)]
    
    # Include additional resources
    return [
        ("assets/shield.png", "assets/shield.png"),  # Icon file for PySide6 GUI
    ] + pywin32_files  # Add pywin32 DLLs

# Base setup
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Executable setup
executables = [
    Executable(
        script="SuperUACAdmin.py",  # Main script
        base=base,
        target_name="SuperUACAdmin.exe",
        icon="assets/shield.ico",  # Application icon
        uac_admin=True  # Request admin privileges
    )
]

# Setup configuration
setup(
    name=app_name,
    version=version,
    description=description,
    author=author,
    options={
        "build_exe": {
            "include_files": include_files(),
            "packages": ["PySide6", "winreg", "ctypes", "win32security", "ntsecuritycon", "winsound"]
        }
    },
    executables=executables,
)
