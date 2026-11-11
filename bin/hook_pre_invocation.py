#!/usr/bin/env python3
"""
PreInvocation Hook for agy-cli: Two-Tier Theme-Gated Context Injection.
Executes in < 25ms. Injects 0 tokens when user prompt doesn't intersect known themes.
"""

import sys
import json
import os
import re

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

VAULT_DIR = os.environ.get("AGY_MEMORY_VAULT", os.path.expanduser("~/.gemini/memory"))
THEME_INDEX = os.path.join(VAULT_DIR, ".state", "theme_index.json")

def score_theme(theme, prompt_lower, cwd_lower):
    score = 0.0

    # 1. Path Pattern Match (Strongest signal)
    for pat in theme.get("path_patterns", []):
        pat_clean = pat.replace("*", "").lower().strip()
        if pat_clean and pat_clean in cwd_lower:
            score += 0.55
            break

    # 2. Keyword Trigger Match
    matched_kws = 0
    for kw in theme.get("keywords", []):
        kw_clean = kw.lower().strip()
        if kw_clean and re.search(r"\b" + re.escape(kw_clean) + r"\b", prompt_lower):
            matched_kws += 1

    if matched_kws > 0:
        score += min(0.20 * matched_kws, 0.60)

    return score

def main():
    try:
        raw_in = sys.stdin.read()
        payload = json.loads(raw_in) if raw_in.strip() else {}
    except Exception:
        payload = {}

    user_prompt = payload.get("lastUserInput", "")
    cwd = payload.get("cwd", "")

    # Zero-token injection on empty input or missing index
    if not os.path.exists(THEME_INDEX) or not user_prompt.strip():
        print(json.dumps({"injectSteps": []}))
        return

    try:
        with open(THEME_INDEX, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception:
        print(json.dumps({"injectSteps": []}))
        return

    prompt_lower = user_prompt.lower()
    cwd_lower = cwd.lower().replace("\\", "/")

    # Tier 1: Theme Gatekeeper
    best_theme = None
    best_score = 0.0

    for theme in registry.get("themes", []):
        s = score_theme(theme, prompt_lower, cwd_lower)
        if s > best_score:
            best_score = s
            best_theme = theme

    # Gating Threshold: 0.35. If no theme matches, inject 0 tokens.
    if not best_theme or best_score < 0.35:
        print(json.dumps({"injectSteps": []}))
        return

    # Tier 2: Precision Leaf Retrieval within Active Theme
    principles = best_theme.get("core_principles", [])
    prompt_words = set(re.findall(r"\w{3,}", prompt_lower))

    scored = []
    for p in principles:
        overlap = sum(1 for w in prompt_words if w in p.lower())
        scored.append((overlap, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected_principles = [p for _, p in scored[:2]] if scored else principles[:2]

    injected_lines = [f"**Active Theme: {best_theme.get('title', 'General')}**"]
    for p in selected_principles:
        injected_lines.append(f"- {p}")

    # Connected Atomic Insights
    for ins in best_theme.get("connected_insights", [])[:2]:
        injected_lines.append(f"- *Insight [[{ins.get('id', '')}]]*: {ins.get('title', '')}")

    system_msg = "### 🧠 Active Thematic Memory\n" + "\n".join(injected_lines)

    output = {
        "injectSteps": [
            {
                "systemMessage": {
                    "systemMessage": system_msg
                }
            }
        ]
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
