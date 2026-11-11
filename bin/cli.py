#!/usr/bin/env python3
"""
CLI Utility for Antigravity PKM Memory Vault.
Provides stats, listing, search, manual distillation, and Markdown export.
"""

import sys
import os
import argparse
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
STATE_DIR = VAULT_DIR / ".state"

def cmd_stats(args):
    print("=" * 50)
    print("  🧠 Antigravity PKM Memory Vault Status")
    print("=" * 50)
    print(f"Vault Directory: {VAULT_DIR}")
    
    themes_count = len(list(THEMES_DIR.glob("*.md"))) if THEMES_DIR.exists() else 0
    insights_count = len(list(INSIGHTS_DIR.glob("*.md"))) if INSIGHTS_DIR.exists() else 0
    
    print(f"Active Themes:   {themes_count}")
    print(f"Atomic Insights: {insights_count}")

    index_file = STATE_DIR / "theme_index.json"
    if index_file.exists():
        size_kb = index_file.stat().st_size / 1024.0
        print(f"Compiled Index:  Active ({size_kb:.1f} KB)")
    else:
        print("Compiled Index:  Not generated (run 'reindex')")

def cmd_list(args):
    if args.themes or not args.insights:
        print("\n📂 Living Themes:")
        if THEMES_DIR.exists():
            for tp in THEMES_DIR.glob("*.md"):
                print(f"  - [[{tp.stem}]]")
        else:
            print("  (None)")

    if args.insights or not args.themes:
        print("\n📄 Atomic Insights:")
        if INSIGHTS_DIR.exists():
            for ip in INSIGHTS_DIR.glob("*.md"):
                print(f"  - [[{ip.stem}]]")
        else:
            print("  (None)")

def cmd_search(args):
    q = args.query
    print(f"🔍 Semantic Vault Search for: '{q}'\n")

    vector_store_file = STATE_DIR / "vector_store.json"
    results = []

    # 1. Try Dense Semantic Vector Search (paraphrase-multilingual-MiniLM)
    try:
        bin_dir = Path(__file__).parent
        if str(bin_dir) not in sys.path:
            sys.path.insert(0, str(bin_dir))
        from semantic_engine import embed_single, cosine_similarity

        if vector_store_file.exists():
            import json
            store = json.loads(vector_store_file.read_text(encoding="utf-8"))
            q_vec = embed_single(q)
            if q_vec:
                for item in store:
                    iv = item.get("vector")
                    if iv:
                        sim = cosine_similarity(q_vec, iv)
                        if sim >= 0.20:
                            results.append((sim, item["type"], item["id"], item["title"]))
                results.sort(key=lambda x: x[0], reverse=True)
    except Exception:
        results = []

    if results:
        print(f"Found {len(results)} semantically relevant entries:\n")
        for sim, ntype, nid, title in results[:8]:
            icon = "🔷 [THEME]  " if ntype == "theme" else "🔹 [INSIGHT]"
            print(f"  {icon} [[{nid}]] ({title})  [Sim: {sim:.3f}]")
        return

    # 2. Fallback to Substring Search
    found = 0
    q_low = q.lower()
    if THEMES_DIR.exists():
        for tp in THEMES_DIR.glob("*.md"):
            if q_low in tp.read_text(encoding="utf-8").lower():
                print(f"🔷 Theme: [[{tp.stem}]]")
                found += 1
    if INSIGHTS_DIR.exists():
        for ip in INSIGHTS_DIR.glob("*.md"):
            if q_low in ip.read_text(encoding="utf-8").lower():
                print(f"🔹 Insight: [[{ip.stem}]]")
                found += 1
    if found == 0:
        print("No matching notes found.")

def cmd_distill(args):
    from daemon import run_distillation
    print("Running autonomous distillation across session transcripts...")
    run_distillation(args.session)
    print("✅ Distillation complete. Theme index updated.")

def cmd_export_md(args):
    from md_exporter import export_markdown
    print("Exporting PKM Memory Vault to consolidated Markdown...")
    out = export_markdown(args.output)
    if out:
        print(f"✅ Generated Markdown Digest: {out}")
    else:
        print("❌ Markdown export failed.")

def cmd_reindex(args):
    from daemon import compile_theme_index
    print("Recompiling theme index...")
    compile_theme_index()
    print("✅ Index successfully updated.")

def main():
    parser = argparse.ArgumentParser(description="Antigravity PKM Memory Vault CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # stats
    sub.add_parser("stats", help="Display memory metrics and vault status")

    # list
    p_list = sub.add_parser("list", help="List active themes and insights")
    p_list.add_argument("--themes", action="store_true", help="List themes only")
    p_list.add_argument("--insights", action="store_true", help="List insights only")

    # search
    p_search = sub.add_parser("search", help="Search vault notes")
    p_search.add_argument("query", help="Keyword or search phrase")

    # distill
    p_distill = sub.add_parser("distill", help="Trigger autonomous distillation")
    p_distill.add_argument("--session", help="Optional conversation session ID")

    # export / export-md
    p_md = sub.add_parser("export", help="Export vault into a consolidated Markdown digest")
    p_md.add_argument("--output", "-o", help="Target Markdown file path")

    p_md2 = sub.add_parser("export-md", help="Export vault into a consolidated Markdown digest")
    p_md2.add_argument("--output", "-o", help="Target Markdown file path")

    # reindex
    sub.add_parser("reindex", help="Recompile theme registry cache")

    args = parser.parse_args()
    if args.cmd == "stats":
        cmd_stats(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "search":
        cmd_search(args)
    elif args.cmd == "distill":
        cmd_distill(args)
    elif args.cmd in ("export", "export-md"):
        cmd_export_md(args)
    elif args.cmd == "reindex":
        cmd_reindex(args)

if __name__ == "__main__":
    main()
