#!/usr/bin/env python3
"""
SATCN Prerequisites Checker

Run this BEFORE installing SATCN to check if your system is ready.
"""

import sys
import subprocess
import shutil
import platform
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
    """Check Python version."""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print(f"\n📌 Python: {version_str}")
    print(f"   Executable: {sys.executable}")
    print(f"   Platform: {platform.platform()}")

    checks = []

    # Check minimum version
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        checks.append(print_check(
            False,
            f"Python 3.11+ required (found {version_str})",
            "Download Python 3.11 or 3.12 from https://python.org/downloads/"
        ))
    else:
        checks.append(print_check(True, f"Python version OK ({version_str})"))

    # Warn about 3.13
    if version.major == 3 and version.minor >= 13:
        print_check(
            False,
            "Python 3.13+: GPU builds may not be available",
            "For GPU support, consider Python 3.11 or 3.12"
        )

    return all(checks)


def check_pip():
    """Check if pip is available."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            pip_version = result.stdout.strip()
            return print_check(True, f"pip available: {pip_version}")
        else:
            return print_check(
                False,
                "pip not working correctly",
                "Reinstall Python or run: python -m ensurepip"
            )
    except Exception as e:
        return print_check(
            False,
            f"pip not available: {e}",
            "Install pip: python -m ensurepip"
        )


def check_git():
    """Check if git is available (for cloning)."""
    git_path = shutil.which("git")
    if git_path:
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return print_check(True, f"git available: {result.stdout.strip()}")
        except:
            pass
    return print_check(
        False,
        "git not available",
        "Optional but recommended for cloning repository"
    )


def check_tkinter():
    """Check if tkinter is available (required for GUI on Linux)."""
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        root.destroy()
        return print_check(True, "tkinter available (required for GUI)")
    except ImportError:
        if sys.platform.startswith("linux"):
            return print_check(
                False,
                "tkinter not available (required for GUI)",
                "Ubuntu/Debian: sudo apt-get install python3-tk\n       Fedora: sudo dnf install python3-tkinter"
            )
        else:
            return print_check(
                False,
                "tkinter not available",
                "Reinstall Python with tkinter support"
            )
    except Exception as e:
        return print_check(
            False,
            f"tkinter error: {e}",
            "Check your display settings"
        )


def check_disk_space():
    """Check available disk space."""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")

        free_gb = free // (2**30)
        print(f"\n💾 Disk space: {free_gb} GB free")

        if free_gb < 5:
            return print_check(
                False,
                f"Only {free_gb} GB free (need at least 5 GB for full install)",
                "Free up disk space"
            )
        else:
            return print_check(True, f"{free_gb} GB free (sufficient)")
    except Exception as e:
        print(f"⚠️  Could not check disk space: {e}")
        return True


def check_nvidia_gpu():
    """Check if NVIDIA GPU is available (optional)."""
    print("\n🎮 GPU Support (Optional):")

    # Check for nvidia-smi
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                gpu_info = result.stdout.strip()
                print_check(True, f"NVIDIA GPU detected: {gpu_info}")
                print("   For GPU support, see docs/GPU_SETUP_GUIDE.md")
                return True
        except Exception:
            pass

    print_check(False, "No NVIDIA GPU detected", "GPU support is optional (CPU-only mode works fine)")
    return True


def main():
    """Run all prerequisite checks."""
    print_header("SATCN Prerequisites Checker")
    print("\nRun this BEFORE installing SATCN to verify your system is ready.")

    checks = []

    print_header("Required")
    checks.append(check_python_version())
    checks.append(check_pip())

    print_header("Recommended")
    check_git()  # Optional
    checks.append(check_tkinter())  # Required for GUI
    check_disk_space()  # Warning only

    print_header("Optional")
    check_nvidia_gpu()  # Optional

    # Final summary
    print_header("Summary")
    if all(checks):
        print("✅ Your system is ready to install SATCN!")
        print("\nNext steps:")
        print("  1. Clone repository: git clone https://github.com/hebbihebb/SATCN.git")
        print("  2. Enter directory: cd SATCN")
        print("  3. Install package: pip install -e \".[gui]\"")
        print("  4. Verify install: python scripts/validate_installation.py")
        print("\nFor detailed instructions, see README.md")
        return 0
    else:
        print("❌ Some prerequisites are missing. See above for fixes.")
        print("\nFix the issues above, then run this script again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
