"""Utility functions for Parallax OpsPilot."""
import os
import platform
from pathlib import Path


def get_system_info() -> str:
    """
    Get system information including OS and shell.

    Returns:
        A string describing the OS and current shell, e.g.,
        "macOS /bin/zsh" or "Linux Ubuntu /bin/bash"
    """
    # Detect OS
    system = platform.system()
    os_name: str

    if system == "Darwin":
        # macOS
        os_name = "macOS"
        # Try to get macOS version
        try:
            release = platform.release()
            if release:
                os_name = f"macOS {release}"
        except Exception:
            pass
    elif system == "Linux":
        # Try to get Linux distribution name
        try:
            # Try to read /etc/os-release
            os_release_path = Path("/etc/os-release")
            if os_release_path.exists():
                with open(os_release_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            os_name = line.split("=", 1)[1].strip().strip('"')
                            break
                    else:
                        os_name = "Linux"
            else:
                os_name = "Linux"
        except Exception:
            os_name = "Linux"
    elif system == "Windows":
        os_name = "Windows"
    else:
        os_name = system

    # Detect shell
    shell_path = os.environ.get("SHELL", "")
    if not shell_path:
        # Fallback: try to detect from common locations
        if system == "Darwin":
            # macOS typically uses zsh by default
            shell_path = "/bin/zsh"
        elif system == "Linux":
            # Linux typically uses bash
            shell_path = "/bin/bash"
        else:
            shell_path = "/bin/sh"

    return f"{os_name} {shell_path}"

