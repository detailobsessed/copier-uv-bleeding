# Agent Instructions

This project uses **tk** for local issue tracking. Tickets are stored as markdown files in `.tickets/`.

## Quick Reference

```bash
tk ready              # Find available work (open tickets with deps resolved)
tk show <id>          # View ticket details (supports partial ID matching)
tk start <id>         # Set status to in_progress
tk close <id>         # Set status to closed
tk list               # List all tickets
tk create "title" -t feature -p 2  # Create a ticket
tk add-note <id> "text"  # Append timestamped note
```
