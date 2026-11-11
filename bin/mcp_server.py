#!/usr/bin/env python3
"""
Lightweight STDIO MCP Server for PKM Memory Vault.
Implements JSON-RPC 2.0 protocol without external pip dependencies.
"""

import sys
import json
import os
import re
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

VAULT_DIR = Path(os.environ.get("AGY_MEMORY_VAULT", os.path.expanduser("~/.gemini/memory")))
THEMES_DIR = VAULT_DIR / "themes"
INSIGHTS_DIR = VAULT_DIR / "insights"

def list_tools():
    return [
        {
            "name": "memory_search",
            "description": "Search the PKM memory vault for themes, distilled principles, and atomic insights.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword or natural language query"},
                    "theme": {"type": "string", "description": "Optional theme filter ID (e.g. theme-applied-linguistics)"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "memory_read",
            "description": "Read the full markdown content and connections of a theme or insight note by ID.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Note identifier (e.g. dec-officecli-usage or theme-cli-tooling)"}
                },
                "required": ["id"]
            }
        },
        {
            "name": "memory_create",
            "description": "Record a new persistent architectural decision or user preference into the PKM vault.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Unique slug ID (e.g. dec-officecli-usage)"},
                    "title": {"type": "string", "description": "Human-readable title"},
                    "theme": {"type": "string", "description": "Parent theme ID (e.g. theme-cli-tooling)"},
                    "type": {"type": "string", "enum": ["decision", "preference", "concept", "workflow"]},
                    "content": {"type": "string", "description": "Markdown body detailing context and decision"}
                },
                "required": ["id", "title", "theme", "content"]
            }
        },
        {
            "name": "memory_export_md",
            "description": "Compile the entire PKM memory vault into a consolidated Markdown digest.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "output_path": {"type": "string", "description": "Optional destination file path for the Markdown digest"}
                }
            }
        }
    ]

def handle_call_tool(name, args):
    if name == "memory_search":
        q = args.get("query", "")
        t_filter = args.get("theme", "")
        vector_store_file = VAULT_DIR / ".state" / "vector_store.json"
        results = []

        # 1. Semantic Vector Search (Multilingual MiniLM)
        try:
            bin_dir = Path(__file__).parent
            if str(bin_dir) not in sys.path:
                sys.path.insert(0, str(bin_dir))
            from semantic_engine import embed_single, cosine_similarity

            if vector_store_file.exists():
                store = json.loads(vector_store_file.read_text(encoding="utf-8"))
                q_vec = embed_single(q)
                if q_vec:
                    ranked = []
                    for item in store:
                        if t_filter and item.get("theme") != t_filter:
                            continue
                        iv = item.get("vector")
                        if iv:
                            sim = cosine_similarity(q_vec, iv)
                            if sim >= 0.20:
                                ranked.append((sim, item))
                    ranked.sort(key=lambda x: x[0], reverse=True)
                    for sim, item in ranked[:5]:
                        nid = item["id"]
                        ntype = item["type"]
                        target_dir = THEMES_DIR if ntype == "theme" else INSIGHTS_DIR
                        fpath = target_dir / f"{nid}.md"
                        snippet = fpath.read_text(encoding="utf-8")[:350] if fpath.exists() else item.get("title", "")
                        results.append(f"### [{ntype.upper()}] [[{nid}]] (Semantic Relevance: {sim:.3f})\n{snippet}...\n")
        except Exception:
            results = []

        # 2. Substring Fallback
        if not results:
            q_low = q.lower()
            if THEMES_DIR.exists():
                for tp in THEMES_DIR.glob("*.md"):
                    content = tp.read_text(encoding="utf-8")
                    if q_low in content.lower():
                        results.append(f"### [Theme] [[{tp.stem}]]\n{content[:400]}...\n")

            if INSIGHTS_DIR.exists():
                for ip in INSIGHTS_DIR.glob("*.md"):
                    content = ip.read_text(encoding="utf-8")
                    if t_filter and t_filter not in content:
                        continue
                    if q_low in content.lower():
                        results.append(f"### [Insight] [[{ip.stem}]]\n{content[:400]}...\n")

        text = "\n---\n".join(results) if results else f"No memory entries matching '{q}'."
        return {"content": [{"type": "text", "text": text}]}

    elif name == "memory_read":
        nid = args.get("id", "").strip("[]")
        target = None
        for d in [THEMES_DIR, INSIGHTS_DIR]:
            p = d / f"{nid}.md"
            if p.exists():
                target = p
                break

        if target:
            return {"content": [{"type": "text", "text": target.read_text(encoding="utf-8")}]}
        return {"content": [{"type": "text", "text": f"Note '{nid}' not found in PKM vault."}], "isError": True}

    elif name == "memory_create":
        nid = args.get("id", "").strip("[]")
        title = args.get("title", "")
        theme = args.get("theme", "")
        ntype = args.get("type", "decision")
        content = args.get("content", "")

        INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
        note_path = INSIGHTS_DIR / f"{nid}.md"
        body = f"""---
id: {nid}
title: {title}
type: {ntype}
theme: {theme}
confidence: 1.00
links:
  - "[[{theme}]]"
---

{content}
"""
        note_path.write_text(body, encoding="utf-8")
        # Trigger index recompile
        bin_dir = Path(__file__).parent
        daemon_py = bin_dir / "daemon.py"
        if daemon_py.exists():
            import subprocess
            subprocess.Popen([sys.executable, str(daemon_py)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return {"content": [{"type": "text", "text": f"Successfully recorded insight [[{nid}]] under theme [[{theme}]]."}]}

    elif name in ("memory_export_md", "memory_export"):
        bin_dir = Path(__file__).parent
        md_exporter = bin_dir / "md_exporter.py"
        out_target = args.get("output_path")
        if md_exporter.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("md_exporter", str(md_exporter))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            res = mod.export_markdown(out_target)
            if res:
                return {"content": [{"type": "text", "text": f"Markdown digest successfully exported to: {res}"}]}
        return {"content": [{"type": "text", "text": "Failed to export Markdown digest."}], "isError": True}

    return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "memory-pkm", "version": "1.0.0"},
                        "capabilities": {"tools": {}}
                    }
                }
            elif method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": list_tools()}
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                call_res = handle_call_tool(tool_name, tool_args)
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": call_res
                }
            else:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }

            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
