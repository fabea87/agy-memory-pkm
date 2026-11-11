# Antigravity PKM Memory Conventions

## 1. Context-Injected Active Memory
- When a prompt activates a known theme, a concise `Active Thematic Memory` block is injected as a system message.
- Adhere strictly to the injected principles and decisions without prompting the user to restate them.

## 2. On-Demand Memory Exploration
- Use `memory_search(query, theme)` or `memory_read(id)` when encountering an ambiguous design choice or reference to an earlier project convention.
- Follow `[[wikilinks]]` in insights to inspect connected decisions or historical contexts.

## 3. Autonomous Memory Recording
- When the user explicitly states a lasting technical constraint, preference, or workflow convention, record it using `memory_create` with appropriate tags and links to the relevant theme.
- Never record transient noise, temporary debugging steps, or ephemeral variables.
