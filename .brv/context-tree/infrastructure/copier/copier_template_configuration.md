---
title: Copier Template Configuration
tags: []
keywords: []
importance: 50
recency: 1
maturity: draft
createdAt: '2026-03-11T23:24:12.009Z'
updatedAt: '2026-03-11T23:24:12.009Z'
---
## Raw Concept

**Task:**
Maintain Copier template configuration

**Changes:**

- Replaced complex bash check-template-update.sh with wrapper
- Updated copier.yml _min_copier_version to 9.13
- Configured check-template poe task to handle exit code 0

**Files:**

- project/scripts/check-template-update.sh
- copier.yml

**Flow:**
Hook triggers -> check-template-update.sh -> copier check-update

**Timestamp:** 2026-03-12

## Narrative

### Structure

The template uses a lightweight wrapper for copier check-update. The check-template poe task ensures consistent exit codes for non-blocking notifications.

### Highlights

Simplification of template update checks, removal of redundant bash tests, and alignment with copier internal functionality.

### Rules

Rule: Always use `|| true` with `copier check-update` in shell tasks to prevent blocking CI/CD pipelines due to non-zero exit codes when updates are detected.

## Facts

- **copier_version**: Minimum copier version is 9.13.0 [project]
- **check_update_behavior**: check-update task is configured to exit 0 [convention]
- **file_restore_behavior**: File-level restores are skipped in check-template-update.sh [convention]
