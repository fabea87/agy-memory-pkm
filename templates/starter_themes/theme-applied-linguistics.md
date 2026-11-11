---
id: theme-applied-linguistics
title: Applied Linguistics & Empirical Research
type: theme
tags:
  - corpus-linguistics
  - automated-writing-evaluation
  - epistemic-network-analysis
  - discourse-analysis
semantic_scope:
  - "Corpus linguistics, feedback analysis, automated writing evaluation"
  - "Epistemic network analysis, rENA, qeviz, cognitive-regulatory mechanisms"
  - "Empirical journal publishing, discourse analysis, peer review"
activation_triggers:
  keywords:
    - corpus
    - ENA
    - qeviz
    - rENA
    - feedback
    - manuscript
    - discourse
    - linguistics
    - writing-analytics
  path_patterns:
    - "*PE as MI*"
    - "*正在工作的文件夹*"
    - "*期刊投稿*"
created_at: 2026-11-11T08:50:00+08:00
updated_at: 2026-11-11T08:50:00+08:00
---

# Theme: Applied Linguistics & Empirical Research

## Distilled Core Principles
1. **Model Authority**: Epistemic Network Analysis figures and parameters must come directly from verified confirmatory analysis runs (`01_build_models.R` using `rENA 0.3.1` with window size 4). Never manually fabricate or edit coordinate data.
2. **Markdown-First Drafting**: All initial research notes, literature summaries, and manuscript drafts must remain in clean, portable Markdown before any external formatting.
3. **Office CLI Exclusivity**: Strictly create or edit Word manuscripts (`.docx`) and Excel tables (`.xlsx`) via the `officecli` binary. Never use Python Office libraries (`python-docx`, `openpyxl`).

## Connected Insights
- [[dec-officecli-usage]]
