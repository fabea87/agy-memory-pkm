#!/usr/bin/env python3
"""
PKM Memory Vault to Consolidated Markdown Exporter.
Compiles living themes, distilled principles, and atomic insights into a clean,
structured, single-file Markdown digest.
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime, timezone

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

def parse_md(path):
    content = path.read_text(encoding="utf-8")
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            current_key = None
            for line in parts[1].splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("- ") and current_key:
                    val = stripped[2:].strip().strip('"').strip("'")
                    if not isinstance(meta[current_key], list):
                        meta[current_key] = []
                    meta[current_key].append(val)
                elif ":" in line:
                    k, v = line.split(":", 1)
                    current_key = k.strip()
                    val = v.strip().strip('"').strip("'")
                    meta[current_key] = val if val else []
            body = parts[2]
    return meta, body

def export_markdown(output_path=None):
    if not output_path:
        output_path = VAULT_DIR / "Memory-Vault-Digest.md"
    else:
        output_path = Path(output_path)

    themes = []
    if THEMES_DIR.exists():
        for tp in sorted(THEMES_DIR.glob("*.md")):
            meta, body = parse_md(tp)
            principles = []
            for line in body.splitlines():
                line = line.strip()
                if line.startswith(("- ", "1. ", "2. ", "3. ", "4. ", "5. ")) and len(line) > 10:
                    clean = re.sub(r"^(\d+\.|\-)\s*", "", line).strip()
                    if clean:
                        principles.append(clean)
            themes.append({
                "id": meta.get("id", tp.stem),
                "title": meta.get("title", tp.stem),
                "meta": meta,
                "body": body.strip(),
                "principles": principles
            })

    insights = []
    if INSIGHTS_DIR.exists():
        for ip in sorted(INSIGHTS_DIR.glob("*.md")):
            meta, body = parse_md(ip)
            insights.append({
                "id": meta.get("id", ip.stem),
                "title": meta.get("title", ip.stem),
                "type": meta.get("type", "insight"),
                "theme": meta.get("theme", ""),
                "meta": meta,
                "body": body.strip()
            })

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build Consolidated Markdown Document
    md = []
    md.append("---")
    md.append("title: AI Agent PKM Memory Vault Digest")
    md.append(f"generated_at: {now_iso}")
    md.append(f"total_themes: {len(themes)}")
    md.append(f"total_insights: {len(insights)}")
    md.append("---")
    md.append("")
    md.append("# 🧠 AI Agent PKM Memory Vault Digest")
    md.append("")
    md.append(f"> Autonomously compiled memory compendium. Generated on **{now_iso}**.")
    md.append("")
    md.append("## 📊 Vault Metrics")
    md.append(f"- **Active Living Themes**: {len(themes)}")
    md.append(f"- **Atomic Insights & Decisions**: {len(insights)}")
    md.append(f"- **Vault Location**: `{VAULT_DIR}`")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 📑 Table of Contents")
    md.append("### Living Themes (Maps of Content)")
    for t in themes:
        slug = re.sub(r"[^a-zA-Z0-9\-_]+", "", t["id"].lower())
        md.append(f"- [{t['title']}](#{slug})")
    md.append("")
    md.append("### Atomic Insights")
    for i in insights:
        slug = re.sub(r"[^a-zA-Z0-9\-_]+", "", i["id"].lower())
        md.append(f"- `[{i['type'].upper()}]` [{i['title']}](#{slug})")
    md.append("")
    md.append("---")
    md.append("")

    # Part 1: Themes
    md.append("## 📂 Living Themes (Maps of Content)")
    md.append("")
    for t in themes:
        md.append(f"### <a id=\"{t['id']}\"></a>{t['title']} (`{t['id']}`)")
        tags = t["meta"].get("tags", [])
        if tags:
            tag_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
            md.append(f"**Tags**: `{tag_str}`  ")
        md.append("")
        if t["principles"]:
            md.append("#### Distilled Core Principles")
            for idx, p in enumerate(t["principles"], 1):
                md.append(f"{idx}. {p}")
            md.append("")

        # Filter related insights
        related = [i for i in insights if i["theme"] == t["id"] or t["id"] in str(i["meta"].get("links", []))]
        if related:
            md.append("#### Connected Insights")
            for r in related:
                md.append(f"- [[{r['id']}]] ({r['title']})")
            md.append("")
        md.append("---")
        md.append("")

    # Part 2: Insights
    md.append("## 📄 Atomic Insights & Decisions")
    md.append("")
    for i in insights:
        md.append(f"### <a id=\"{i['id']}\"></a>[{i['type'].upper()}] {i['title']} (`{i['id']}`)")
        if i["theme"]:
            md.append(f"**Parent Theme**: [[{i['theme']}]]  ")
        tags = i["meta"].get("tags", [])
        if tags:
            tag_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
            md.append(f"**Tags**: `{tag_str}`  ")
        md.append("")
        clean_body = re.sub(r"^#+ .*", "", i["body"]).strip()
        md.append(clean_body)
        md.append("")
        md.append("---")
        md.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(md), encoding="utf-8")
    print(f"✅ Successfully exported Markdown digest to: {output_path}")
    return str(output_path)

if __name__ == "__main__":
    out_target = sys.argv[1] if len(sys.argv) > 1 else None
    export_markdown(out_target)
