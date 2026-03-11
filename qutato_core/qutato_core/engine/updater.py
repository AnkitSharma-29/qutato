import requests
import os
from qutato_core.version import __version__

# The public URL for the version file on GitHub
VERSION_URL = "https://raw.githubusercontent.com/AnkitSharma-29/qutato/main/qutato_core/qutato_core/version.py"

def check_for_updates():
    """
    Checks if a newer version of Qutato is available on GitHub.
    Returns (True, latest_version) if update available, else (False, current_version).
    """
    try:
        # Timeout 2s to prevent hanging on slow internet
        response = requests.get(VERSION_URL, timeout=2)
        if response.status_code == 200:
            # Extract version from the python file content
            content = response.text
            if "__version__ =" in content:
                latest_version = content.split('__version__ = "')[1].split('"')[0]
                
                # Simple string comparison (e.g., "0.1.1" > "0.1.0")
                if latest_version > __version__:
                    return True, latest_version
    except:
        # Fail silently if offline or URL fails
        pass
    
    return False, __version__

def print_update_notification():
    """Prints a notification if an update is available."""
    update_available, latest = check_for_updates()
    if update_available:
        print(f"\n✨ [Qutato Update] A newer version (v{latest}) is available!")
        print(f"👉 Run 'git pull' to update your local installation.\n")
