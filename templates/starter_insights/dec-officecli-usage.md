---
id: dec-officecli-usage
title: Strict Officecli Tooling Rule
type: decision
tags:
  - officecli
  - docx
  - xlsx
  - pptx
  - python-ban
theme: theme-applied-linguistics
confidence: 1.00
created_at: 2026-11-11T08:50:00+08:00
updated_at: 2026-11-11T08:50:00+08:00
links:
  - "[[theme-applied-linguistics]]"
---

## Decision
Create and modify Office documents (`.docx`, `.xlsx`, `.pptx`) strictly via the `officecli` binary (`officecli` or `officecli.exe`).

## Rationale
Ad-hoc Python packages (`python-docx`, `openpyxl`, `python-pptx`) introduce inconsistent formatting, missing XML schemas, and unwanted dependency drift. `officecli` provides robust, reproducible programmatic document formatting.
