# pi-memory-strata

## Installation

```bash
pi install npm:pi-memory-strata
```

Or via npm directly:
```bash
npm install -g pi-memory-strata
```

## Commands

### `pi-memory-strata check`
Run distillation check on memory system health.

```bash
pi-memory-strata check --vault /path/to/vault
```

### `pi-memory-strata maintain`
Run daily maintenance routine (journal check, project status, auto-archive).

```bash
pi-memory-strata maintain --vault /path/to/vault [--dry-run]
```

### `pi-memory-strata init-project`
Initialize a new project with templates.

```bash
pi-memory-strata init-project <project-name> --vault /path/to/vault
```

## Vault Structure

```
vault/
├── 00-brain/
│   └── MEMORY.md              # L1: System injection
├── 10-journal/
│   ├── maintenance/           # Auto-maintenance reports
│   ├── summary/               # Daily summaries
│   └── 2026-01-01.md        # L4: Daily session logs
├── 20-projects/
│   └── my-project/
│       ├── dev-status.md    # L3: Development status
│       └── project-core.md  # L2: Project core archive
├── 60-learnings/
│   └── archive/             # Auto-archived entries
├── scripts/
│   ├── daily_memory_maintenance.py
│   └── memory_distill_check.py
└── templates/
    ├── 01-status.md
    └── 02-core.md
```

## Configuration

Set your vault path via environment variable:
```bash
export OBSIDIAN_VAULT_PATH=/path/to/vault
```

Or pass `--vault` to every command.

## Features

- **Four-layer memory architecture** (L1-L4)
- **Auto-distillation** (L4→L3→L2 promotion)
- **Memory decay** (last_used tracking with 30-day auto-archive)
- **Bidirectional link checking** (L2↔L3)
- **Daily maintenance automation**
- **Zettelkasten link enhancement**

## License

MIT
