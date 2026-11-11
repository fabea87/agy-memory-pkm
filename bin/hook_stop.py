#!/usr/bin/env python3
"""
Stop Hook for agy-cli: Dispatches background distillation worker asynchronously.
Exits immediately without delaying CLI loop termination.
"""

import sys
import json
import os
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    try:
        raw_in = sys.stdin.read()
        payload = json.loads(raw_in) if raw_in.strip() else {}
    except Exception:
        payload = {}

    bin_dir = os.path.dirname(os.path.abspath(__file__))
    daemon_script = os.path.join(bin_dir, "daemon.py")
    conv_id = payload.get("conversationId", "")

    if os.path.exists(daemon_script):
        cmd = [sys.executable, daemon_script, "--session", conv_id]
        kwargs = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL
        }
        if sys.platform == "win32":
            CREATE_NO_WINDOW = 0x08000000
            kwargs["creationflags"] = CREATE_NO_WINDOW
        else:
            kwargs["start_new_session"] = True

        try:
            subprocess.Popen(cmd, **kwargs)
        except Exception:
            pass

    # Acknowledge Stop
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
