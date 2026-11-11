# 🧠 agy-memory-pkm

**Autonomous, Theme-Centric Hierarchical PKM Memory Extension for Antigravity CLI (`agy`)**

Persistent agent memory structured as a personal knowledge management (PKM) vault with two-tier gated contextual injection, periodic delta distillation, and Markdown digest export.

---

## ⚡ One-Line Installation

Works identically across **Windows** and **macOS**. `install.py` will automatically verify and install dependencies from `requirements.txt` if needed.

### macOS / Linux (Terminal)
```bash
python3 install.py
# Or using the shell wrapper:
bash install.sh
```

### Windows (PowerShell)
```powershell
python install.py
# Or using the PowerShell wrapper:
.\install.ps1
```

*(Optional: manual dependency install)*
```bash
pip install -r requirements.txt
```

---

## 🌟 Key Architecture & Capabilities

1. **Theme-Centric Hierarchy (H-PKM)**:
   - Eliminates context-polluting flat memory dumps.
   - Experiences cluster under **Living Themes** (Maps of Content), linking to atomic architectural decisions, empirical research protocols, and user preferences.
2. **Two-Tier Gated Injection (`< 25ms`)**:
   - **Tier 1 (Theme Router)**: Checks if user intent intersects an active theme. If confidence is below threshold, **injects 0 tokens** (clean context).
   - **Tier 2 (Precision Leaf Extraction)**: Pulls only the top 1–2 specific directives under the active theme.
3. **Autonomous Thematic Distillation**:
   - The `Stop` hook dispatches a background daemon asynchronously.
   - Tracks transcript deltas via `.state/cursors.json` and updates theme hubs and indices without blocking user prompts.
4. **Consolidated Markdown Digest Export**:
   - Compiles the entire knowledge base into a single-file, structured Markdown compendium with Table of Contents, thematic Maps of Content, and cross-referenced `[[wikilinks]]`.

---

## 📖 CLI Commands

The package includes a management CLI located at `bin/cli.py` (or installed at `~/.gemini/config/plugins/memory-pkm/bin/cli.py`):

```bash
# View vault metrics & active themes
python bin/cli.py stats

# List living themes and atomic insights
python bin/cli.py list

# Search memory vault
python bin/cli.py search "statusline"

# Trigger background distillation across session transcripts
python bin/cli.py distill

# Compile and export knowledge vault to Markdown digest
python bin/cli.py export --output ~/Desktop/Agent-Memory-Digest.md
```

---

## 📁 Vault Structure (`~/.gemini/memory/`)

```text
~/.gemini/memory/
├── themes/                 # Living Maps of Content (MOCs)
│   ├── theme-applied-linguistics.md
│   └── theme-cli-tooling.md
├── insights/               # Atomic decisions and preferences
│   ├── dec-officecli-usage.md
│   └── dec-statusline-model.md
└── .state/
    ├── theme_index.json    # Fast in-memory index (< 25ms gate)
    └── cursors.json        # Delta transcript tracking
```

---

## 🗑️ Uninstallation

```bash
python install.py --uninstall
```
*(Your markdown vault in `~/.gemini/memory/` is preserved.)*
