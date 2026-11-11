---
name: memory-pkm
description: Manage the Antigravity Theme-Centric PKM Memory Vault. Use to inspect active themes, search insights, trigger background distillation, and export memory digests to Markdown.
---

# Antigravity PKM Memory System

The `memory-pkm` extension organizes long-term agent experiences into a Hierarchical Personal Knowledge Management (H-PKM) vault, clustering atomic insights under living Themes.

## Common CLI Workflows

Run the following commands via the terminal or Python CLI:

### 1. View Vault Status & Themes
```bash
python ~/.gemini/config/plugins/agy-memory-pkm/bin/cli.py stats
python ~/.gemini/config/plugins/agy-memory-pkm/bin/cli.py list --themes
```

### 2. Search Insights
```bash
python ~/.gemini/config/plugins/agy-memory-pkm/bin/cli.py search "statusline model"
```

### 3. Run Autonomous Distillation Manually
Scans recent transcripts across `~/.gemini/antigravity-cli/brain/` and distills new insights:
```bash
python ~/.gemini/config/plugins/agy-memory-pkm/bin/cli.py distill --all
```

### 4. Export Memory Vault to Markdown Digest
Compiles all themes, principles, and atomic insights into a consolidated Markdown document:
```bash
python ~/.gemini/config/plugins/agy-memory-pkm/bin/cli.py export --output ~/Desktop/Agent-Memory-Digest.md
```
