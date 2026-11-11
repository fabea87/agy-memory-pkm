#!/usr/bin/env python3
"""
Universal Cross-Platform Installer for agy-memory-pkm.
Works seamlessly across Windows and macOS.
"""

import sys
import os
import shutil
import json
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PACKAGE_ROOT = Path(__file__).parent.resolve()
GEMINI_HOME = Path(os.environ.get("GEMINI_HOME", os.path.expanduser("~/.gemini")))
PLUGIN_TARGET = GEMINI_HOME / "config" / "plugins" / "memory-pkm"
VAULT_DIR = GEMINI_HOME / "memory"
CONFIG_FILE = GEMINI_HOME / "config" / "config.json"

def print_banner():
    print("=" * 60)
    print("  🚀 Antigravity PKM Memory Extension Installer")
    print("  Theme-Centric Gated Memory • Multi-OS (macOS & Windows)")
    print("=" * 60)

def install():
    print_banner()

    py_bin = Path(sys.executable).as_posix()
    print(f"[*] Detected Host OS:      {sys.platform}")
    print(f"[*] Python Executable:     {py_bin}")
    print(f"[*] Target Plugin Path:    {PLUGIN_TARGET}")
    print(f"[*] Target Vault Path:     {VAULT_DIR}")

    # 0. Check & Install Python Dependencies
    req_file = PACKAGE_ROOT / "requirements.txt"
    try:
        import fastembed
        print("[+] Verified dependency: fastembed (multilingual ONNX embedding engine)")
    except ImportError:
        print("[*] Installing required dependencies from requirements.txt...")
        if req_file.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], check=False)
        else:
            subprocess.run([sys.executable, "-m", "pip", "install", "fastembed>=0.9.0"], check=False)

    # 1. Ensure target directory structure
    PLUGIN_TARGET.mkdir(parents=True, exist_ok=True)
    (PLUGIN_TARGET / "bin").mkdir(parents=True, exist_ok=True)
    (PLUGIN_TARGET / "rules").mkdir(parents=True, exist_ok=True)
    (PLUGIN_TARGET / "skills" / "memory-pkm").mkdir(parents=True, exist_ok=True)

    # 2. Copy source files
    print("\n[+] Deploying extension modules...")
    for item in ["plugin.json", "requirements.txt"]:
        if (PACKAGE_ROOT / item).exists():
            shutil.copy2(PACKAGE_ROOT / item, PLUGIN_TARGET / item)

    for item in (PACKAGE_ROOT / "bin").glob("*.py"):
        shutil.copy2(item, PLUGIN_TARGET / "bin" / item.name)

    shutil.copy2(PACKAGE_ROOT / "rules" / "AGENTS.md", PLUGIN_TARGET / "rules" / "AGENTS.md")
    shutil.copy2(PACKAGE_ROOT / "skills" / "memory-pkm" / "SKILL.md", PLUGIN_TARGET / "skills" / "memory-pkm" / "SKILL.md")

    # 3. Generate platform-specific hooks.json
    print("[+] Configuring lifecycle hooks (SessionStart, PreInvocation, Stop)...")
    hook_pre_path = (PLUGIN_TARGET / "bin" / "hook_pre_invocation.py").as_posix()
    hook_stop_path = (PLUGIN_TARGET / "bin" / "hook_stop.py").as_posix()

    hooks_payload = {
        "memory-pkm-hooks": {
            "SessionStart": [
                {
                    "type": "command",
                    "command": f'"{py_bin}" "{hook_stop_path}"',
                    "timeout": 5
                }
            ],
            "PreInvocation": [
                {
                    "type": "command",
                    "command": f'"{py_bin}" "{hook_pre_path}"',
                    "timeout": 5
                }
            ],
            "Stop": [
                {
                    "type": "command",
                    "command": f'"{py_bin}" "{hook_stop_path}"',
                    "timeout": 5
                }
            ]
        }
    }
    (PLUGIN_TARGET / "hooks.json").write_text(json.dumps(hooks_payload, indent=2), encoding="utf-8")

    # 4. Generate mcp_config.json
    print("[+] Registering MCP memory server...")
    mcp_server_path = (PLUGIN_TARGET / "bin" / "mcp_server.py").as_posix()
    mcp_payload = {
        "mcpServers": {
            "memory-pkm": {
                "command": py_bin,
                "args": [mcp_server_path],
                "tools": {
                    "memory_search": {"eager": True},
                    "memory_read": {"eager": True},
                    "memory_create": {"eager": False},
                    "memory_export_md": {"eager": False}
                }
            }
        }
    }
    (PLUGIN_TARGET / "mcp_config.json").write_text(json.dumps(mcp_payload, indent=2), encoding="utf-8")

    # 5. Enable in ~/.gemini/config/config.json
    print("[+] Enabling plugin in config.json...")
    config_data = {}
    if CONFIG_FILE.exists():
        try:
            config_data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            config_data = {}

    plugins_map = config_data.setdefault("plugins", {})
    plugins_map["memory-pkm"] = {"enabled": True}
    CONFIG_FILE.write_text(json.dumps(config_data, indent=4), encoding="utf-8")

    # 6. Initialize PKM Vault if empty
    print("[+] Initializing PKM Vault structure...")
    (VAULT_DIR / "themes").mkdir(parents=True, exist_ok=True)
    (VAULT_DIR / "insights").mkdir(parents=True, exist_ok=True)
    (VAULT_DIR / ".state").mkdir(parents=True, exist_ok=True)

    # Copy starter themes if none exist
    starter_themes = list((PACKAGE_ROOT / "templates" / "starter_themes").glob("*.md"))
    for st in starter_themes:
        dest = VAULT_DIR / "themes" / st.name
        if not dest.exists():
            shutil.copy2(st, dest)

    starter_insights = list((PACKAGE_ROOT / "templates" / "starter_insights").glob("*.md"))
    for si in starter_insights:
        dest = VAULT_DIR / "insights" / si.name
        if not dest.exists():
            shutil.copy2(si, dest)

    # 7. Compile Initial Theme Index
    print("[+] Compiling initial theme index...")
    daemon_path = PLUGIN_TARGET / "bin" / "daemon.py"
    subprocess.run([py_bin, str(daemon_path)], check=True)

    # 8. Self-Test
    print("[+] Running verification self-test...")
    test_proc = subprocess.run(
        [py_bin, str(hook_pre_path)],
        input=json.dumps({"lastUserInput": "check statusline model slug", "cwd": ""}),
        text=True,
        capture_output=True,
        encoding="utf-8"
    )
    if test_proc.returncode == 0:
        res = json.loads(test_proc.stdout or "{}")
        if res.get("injectSteps"):
            print("  ✅ Theme Gating Test Passed: Injected active memory for statusline query.")
        else:
            print("  ℹ️ Gating Active: Clean context (0 tokens injected).")
    else:
        print(f"  ⚠️ Warning: Self-test exited with code {test_proc.returncode}")

    print("\n" + "=" * 60)
    print("  🎉 Installation Successful!")
    print("  The memory extension is now active in Antigravity CLI.")
    print("  Try running in agy:")
    print("    python ~/.gemini/config/plugins/memory-pkm/bin/cli.py stats")
    print("    python ~/.gemini/config/plugins/memory-pkm/bin/cli.py export")
    print("=" * 60 + "\n")

def uninstall():
    print_banner()
    print("[*] Uninstalling agy-memory-pkm...")
    if PLUGIN_TARGET.exists():
        shutil.rmtree(PLUGIN_TARGET)
        print(f"[+] Removed plugin directory: {PLUGIN_TARGET}")

    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if "plugins" in cfg and "memory-pkm" in cfg["plugins"]:
                del cfg["plugins"]["memory-pkm"]
                CONFIG_FILE.write_text(json.dumps(cfg, indent=4), encoding="utf-8")
                print("[+] Unregistered from config.json")
        except Exception:
            pass

    print("[i] Note: Your markdown vault at ~/.gemini/memory/ was preserved.")
    print("✅ Uninstallation complete.")

if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        uninstall()
    else:
        install()
