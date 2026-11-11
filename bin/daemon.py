#!/usr/bin/env python3
"""
Autonomous Thematic Distillation Engine for agy-cli.
Processes session transcripts incrementally, clusters insights under living themes,
and compiles the fast index cache.
"""

import sys
import os
import json
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
STATE_DIR = VAULT_DIR / ".state"
INDEX_FILE = STATE_DIR / "theme_index.json"
CURSOR_FILE = STATE_DIR / "cursors.json"
BRAIN_DIR = Path(os.path.expanduser("~/.gemini/antigravity-cli/brain"))

def load_cursors():
    if CURSOR_FILE.exists():
        try:
            return json.loads(CURSOR_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_cursors(cursors):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    CURSOR_FILE.write_text(json.dumps(cursors, indent=2, ensure_ascii=False), encoding="utf-8")

def parse_markdown_frontmatter(content):
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_meta = parts[1]
            body = parts[2]
            current_key = None
            for line in raw_meta.splitlines():
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
    return meta, body

def compile_theme_index():
    """Compiles all themes into a fast in-memory index for hook_pre_invocation.py."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    themes = []

    if not THEMES_DIR.exists():
        THEMES_DIR.mkdir(parents=True, exist_ok=True)

    # First load all atomic insights for fast linking
    insights_by_theme = {}
    if INSIGHTS_DIR.exists():
        for ipath in INSIGHTS_DIR.glob("*.md"):
            try:
                icontent = ipath.read_text(encoding="utf-8")
                imeta, _ = parse_markdown_frontmatter(icontent)
                tid = imeta.get("theme", "")
                if tid:
                    insights_by_theme.setdefault(tid, []).append({
                        "id": imeta.get("id", ipath.stem),
                        "title": imeta.get("title", ipath.stem)
                    })
            except Exception:
                pass

    for tpath in THEMES_DIR.glob("*.md"):
        try:
            content = tpath.read_text(encoding="utf-8")
            meta, body = parse_markdown_frontmatter(content)
            tid = meta.get("id", tpath.stem)

            # Extract distilled principles
            principles = []
            for line in body.splitlines():
                line = line.strip()
                if line.startswith(("- ", "1. ", "2. ", "3. ", "4. ", "5. ")) and len(line) > 10:
                    clean = re.sub(r"^(\d+\.|\-)\s*", "", line)
                    clean = re.sub(r"\[\[.*?\]\]", "", clean).strip()
                    if clean:
                        principles.append(clean)

            # Keywords & path patterns
            raw_kws = meta.get("keywords", [])
            kws = raw_kws if isinstance(raw_kws, list) else [k.strip("- ") for k in str(raw_kws).split(",") if k.strip()]

            raw_tags = meta.get("tags", [])
            tags = raw_tags if isinstance(raw_tags, list) else [t.strip("- ") for t in str(raw_tags).split(",") if t.strip()]
            combined_kws = list(set(kws + tags))

            raw_pats = meta.get("path_patterns", [])
            pats = raw_pats if isinstance(raw_pats, list) else [p.strip("- ") for p in str(raw_pats).split(",") if p.strip()]

            themes.append({
                "id": tid,
                "title": meta.get("title", tpath.stem),
                "keywords": combined_kws,
                "path_patterns": pats,
                "semantic_scope": meta.get("semantic_scope", ""),
                "core_principles": principles[:6],
                "connected_insights": insights_by_theme.get(tid, [])
            })
        except Exception:
            pass

    # Pre-compute semantic vectors using multilingual MiniLM
    try:
        bin_dir = Path(__file__).parent
        if str(bin_dir) not in sys.path:
            sys.path.insert(0, str(bin_dir))
        from semantic_engine import embed_texts, embed_single
        descriptions = []
        for t in themes:
            scope = t.get("semantic_scope", "")
            scope_str = " ".join(scope) if isinstance(scope, list) else str(scope)
            principles_str = " ".join(t.get("core_principles", []))
            descriptions.append(f"{t['title']}. Scope: {scope_str}. Principles: {principles_str}")

        vectors = embed_texts(descriptions)
        if vectors:
            for idx, vec in enumerate(vectors):
                themes[idx]["vector"] = vec

        # Pre-compute vectors for each theme's core principles (for Tier-2 semantic matching)
        for t in themes:
            pr_list = t.get("core_principles", [])
            if pr_list:
                pr_vecs = embed_texts(pr_list)
                if pr_vecs:
                    t["principle_vectors"] = pr_vecs

        # Pre-compute all insight vectors for fast semantic search
        all_notes_index = []
        for t in themes:
            all_notes_index.append({
                "id": t["id"],
                "title": t["title"],
                "type": "theme",
                "vector": t.get("vector")
            })

        if INSIGHTS_DIR.exists():
            insight_paths = list(INSIGHTS_DIR.glob("*.md"))
            insight_texts = []
            insight_metas = []
            for ip in insight_paths:
                try:
                    icontent = ip.read_text(encoding="utf-8")
                    imeta, ibody = parse_markdown_frontmatter(icontent)
                    insight_metas.append({
                        "id": imeta.get("id", ip.stem),
                        "title": imeta.get("title", ip.stem),
                        "type": imeta.get("type", "insight"),
                        "theme": imeta.get("theme", "")
                    })
                    insight_texts.append(f"{imeta.get('title', '')} {ibody[:300]}")
                except Exception:
                    pass

            if insight_texts:
                i_vecs = embed_texts(insight_texts)
                if i_vecs:
                    for m, iv in zip(insight_metas, i_vecs):
                        m["vector"] = iv
                        all_notes_index.append(m)

        (STATE_DIR / "vector_store.json").write_text(json.dumps(all_notes_index, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    INDEX_FILE.write_text(json.dumps({"themes": themes}, indent=2, ensure_ascii=False), encoding="utf-8")

def extract_insights_from_transcript(transcript_path, last_step):
    """Parses transcript lines since last_step for actionable insights."""
    if not transcript_path.exists():
        return [], last_step

    new_insights = []
    current_max_step = last_step

    try:
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    step = json.loads(line)
                except Exception:
                    continue

                idx = step.get("step_index", 0)
                if idx <= last_step:
                    continue
                if idx > current_max_step:
                    current_max_step = idx

                step_type = step.get("type", "")
                content = step.get("content", "")

                # User prompt inspection for rules/preferences
                if step_type == "USER_INPUT" and content:
                    # Detect constraints & preferences
                    if re.search(r"\b(always|never|do not|must|prefer|wish|remember)\b", content, re.I):
                        cleaned_pref = re.sub(r"<[^>]+>", "", content).strip()
                        if len(cleaned_pref) > 15:
                            new_insights.append({
                                "type": "preference",
                                "raw": cleaned_pref,
                                "step": idx
                            })

                # Planner tool execution inspection
                elif step_type == "PLANNER_RESPONSE" and "tool_calls" in step:
                    # Detect major architectural decisions or tool fixes
                    pass
    except Exception:
        pass

    return new_insights, current_max_step

def run_distillation(session_id=None):
    """Main distillation runner."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    THEMES_DIR.mkdir(parents=True, exist_ok=True)
    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)

    cursors = load_cursors()

    sessions_to_check = []
    if session_id:
        sessions_to_check.append(session_id)
    elif BRAIN_DIR.exists():
        for p in BRAIN_DIR.iterdir():
            if p.is_dir():
                sessions_to_check.append(p.name)

    for sid in sessions_to_check:
        tpath = BRAIN_DIR / sid / ".system_generated" / "logs" / "transcript.jsonl"
        last_step = cursors.get(sid, {}).get("last_processed_step", 0)
        extracted, new_step = extract_insights_from_transcript(tpath, last_step)

        if extracted:
            now_iso = datetime.now(timezone.utc).isoformat()
            # For each extracted preference, integrate into theme or save as atomic insight
            for idx, item in enumerate(extracted):
                raw = item["raw"]
                # Detect target theme via dense semantic vector similarity
                target_theme = "theme-cli-tooling"
                best_sim = -1.0
                try:
                    from semantic_engine import embed_single, cosine_similarity
                    raw_vec = embed_single(raw)
                    if raw_vec and INDEX_FILE.exists():
                        cur_idx = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
                        for th in cur_idx.get("themes", []):
                            th_vec = th.get("vector")
                            if th_vec:
                                sim = cosine_similarity(raw_vec, th_vec)
                                if sim > best_sim:
                                    best_sim = sim
                                    target_theme = th["id"]
                except Exception:
                    pass
                slug = re.sub(r"[^a-zA-Z0-9]+", "-", raw[:40].lower()).strip("-")
                iid = f"pref-{slug}-{item['step']}"
                if len(iid) > 50:
                    iid = iid[:50].rstrip("-")

                note_file = INSIGHTS_DIR / f"{iid}.md"
                if not note_file.exists():
                    note_content = f"""---
id: {iid}
title: Auto-distilled Insight from Session {sid[:8]}
type: preference
theme: {target_theme}
confidence: 0.90
created_at: {now_iso}
updated_at: {now_iso}
source_session: {sid}
source_step: {item['step']}
links:
  - "[[{target_theme}]]"
---

## Summary Directive
{raw}
"""
                    note_file.write_text(note_content, encoding="utf-8")

        cursors[sid] = {
            "last_processed_step": new_step,
            "last_processed_timestamp": datetime.now(timezone.utc).isoformat()
        }

    save_cursors(cursors)
    compile_theme_index()

if __name__ == "__main__":
    sid_arg = None
    if "--session" in sys.argv:
        try:
            sid_arg = sys.argv[sys.argv.index("--session") + 1]
        except Exception:
            pass
    run_distillation(sid_arg)
