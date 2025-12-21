#!/usr/bin/env python3
"""
SATCN Installation Validator

This script validates that SATCN is properly installed and configured.
It checks Python version, package installation, entry points, and dependencies.
"""

import sys
import subprocess
import shutil
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def print_check(passed, message, fix=None):
    """Print a check result."""
    status = "✅" if passed else "❌"
    print(f"{status} {message}")
    if not passed and fix:
        print(f"   Fix: {fix}")
    return passed


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print(f"\n📌 Python version: {version_str}")

    checks = []

    # Check minimum version
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        checks.append(print_check(
            False,
            f"Python 3.11+ required (found {version_str})",
            "Install Python 3.11 or 3.12 from python.org"
        ))
    else:
        checks.append(print_check(True, f"Python version OK ({version_str})"))

    # Warn about 3.13
    if version.major == 3 and version.minor >= 13:
        print_check(
            False,
            f"Python 3.13+ detected - GPU builds may not be available",
            "Consider using Python 3.11 or 3.12 for GPU support"
        )
        # Don't fail, just warn
        checks.append(True)

    return all(checks)


def check_satcn_installed():
    """Check if SATCN package is installed."""
    try:
        import satcn
        location = Path(satcn.__file__).parent.parent
        print_check(True, f"SATCN package installed at: {location}")
        return True
    except ImportError:
        print_check(
            False,
            "SATCN package not installed",
            "Run: pip install -e ."
        )
        return False


def check_entry_points():
    """Check if entry points are working."""
    checks = []

    # Check satcn CLI
    satcn_path = shutil.which("satcn")
    if satcn_path:
        checks.append(print_check(True, f"CLI entry point 'satcn' found: {satcn_path}"))
    else:
        checks.append(print_check(
            False,
            "CLI entry point 'satcn' not found",
            "Reinstall with: pip install -e ."
        ))

    # Check satcn-gui
    gui_path = shutil.which("satcn-gui")
    if gui_path:
        checks.append(print_check(True, f"GUI entry point 'satcn-gui' found: {gui_path}"))
    else:
        checks.append(print_check(
            False,
            "GUI entry point 'satcn-gui' not found",
            "Reinstall with: pip install -e ."
        ))

    return all(checks)


def check_extras_installed():
    """Check which optional extras are installed."""
    print("\n📦 Optional extras:")

    extras = {
        "gui": ["customtkinter"],
        "grmr": ["llama_cpp"],
        "t5": ["transformers", "torch"],
        "dev": ["pytest", "ruff", "black"]
    }

    for extra_name, packages in extras.items():
        all_installed = True
        for package in packages:
            try:
                __import__(package)
            except ImportError:
                all_installed = False
                break

        if all_installed:
            print_check(True, f"[{extra_name}] extra installed")
        else:
            print_check(False, f"[{extra_name}] extra not installed", f"pip install -e \".[{extra_name}]\"")


def check_system_dependencies():
    """Check system-level dependencies."""
    print("\n🔧 System dependencies:")

    # Check tkinter (required for GUI on Linux)
    try:
        import tkinter
        print_check(True, "tkinter available")
    except ImportError:
        if sys.platform.startswith("linux"):
            print_check(
                False,
                "tkinter not available",
                "Ubuntu/Debian: sudo apt-get install python3-tk\n       Fedora: sudo dnf install python3-tkinter"
            )
        else:
            print_check(False, "tkinter not available", "Reinstall Python with tkinter support")


def check_gpu_support():
    """Check if GPU support is available."""
    print("\n🎮 GPU support:")

    try:
        from llama_cpp import Llama
        # Try to check if CUDA is available
        # Note: This is a basic check, actual GPU usage depends on model loading
        print_check(True, "llama-cpp-python installed (GPU support may be available)")
    except ImportError:
        print_check(
            False,
            "llama-cpp-python not installed",
            "pip install -e \".[grmr]\""
        )


def main():
    """Run all validation checks."""
    print_header("SATCN Installation Validator")

    all_checks = []

    # Critical checks
    print_header("Critical Checks")
    all_checks.append(check_python_version())
    all_checks.append(check_satcn_installed())

    # Only check entry points if package is installed
    if all_checks[-1]:
        all_checks.append(check_entry_points())

    # Optional checks (don't affect overall status)
    print_header("Optional Features")
    check_extras_installed()
    check_system_dependencies()
    check_gpu_support()

    # Final summary
    print_header("Summary")
    if all(all_checks):
        print("✅ Installation is working correctly!")
        print("\nYou can now:")
        print("  - Run the CLI: satcn --help")
        print("  - Run the GUI: satcn-gui")
        print("  - Use launchers in the launchers/ directory")
        return 0
    else:
        print("❌ Some critical issues found. See above for fixes.")
        print("\nFor detailed installation instructions, see:")
        print("  - README.md")
        print("  - INSTALLATION.md (if available)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
