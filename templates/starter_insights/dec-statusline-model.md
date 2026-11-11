---
id: dec-statusline-model
title: Statusline Normalized Model Slug
type: decision
tags:
  - statusline
  - agy-cli
  - model-display
theme: theme-cli-tooling
confidence: 0.95
created_at: 2026-11-11T08:50:00+08:00
updated_at: 2026-11-11T08:50:00+08:00
links:
  - "[[theme-cli-tooling]]"
---

## Decision
Configure `agy-statusline.py` to preserve model version numbers and emit clean lowercase slugs (e.g., `gemini-3.8-flash (high)`) instead of coarse labels like `Gemini Flash`.

## Rationale
Subtle behavioral changes between sub-models (e.g. 3.1 Pro vs 3.5 Flash vs 3.8 Flash) require immediate visual identification in the CLI status bar.
