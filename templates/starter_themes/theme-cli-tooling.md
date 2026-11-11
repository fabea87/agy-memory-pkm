---
id: theme-cli-tooling
title: Antigravity CLI & Terminal Environment
type: theme
tags:
  - agy-cli
  - statusline
  - shell
  - cli-tools
semantic_scope:
  - "Antigravity CLI configuration, settings.json, custom statusline"
  - "Terminal utilities: bat, fd, rg, fff MCP, powershell, zsh"
  - "UTF-8 normalization, platform compatibility between macOS and Windows"
activation_triggers:
  keywords:
    - statusline
    - agy
    - cli
    - terminal
    - powershell
    - bat
    - rg
    - fff
  path_patterns:
    - "*antigravity-cli*"
    - "*scripts*"
created_at: 2026-11-11T08:50:00+08:00
updated_at: 2026-11-11T08:50:00+08:00
---

# Theme: Antigravity CLI & Terminal Environment

## Distilled Core Principles
1. **Model Slug Fidelity**: Display accurate normalized model slugs with version and effort badge in the statusline (e.g. `gemini-3.8-flash (high)`). Avoid generic or truncated labels.
2. **Contemporary CLI Standards**: Prioritize `bat` (with `--paging=never`) over `cat`, `fd` over `find`, `rg` over `grep`, and `fff` MCP tools for codebase symbol/file lookup.
3. **Cross-Platform UTF-8**: Ensure all CLI scripts run cleanly across Windows (PowerShell) and macOS (Bash/Zsh) using UTF-8 encoding and LF line endings.

## Connected Insights
- [[dec-statusline-model]]
