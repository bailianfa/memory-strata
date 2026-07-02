# Memory Strata — 四层分层记忆架构

> Four-layer stratified memory architecture for long-horizon AI agent projects.
> Solves critical fact forgetting, memory bloat, and knowledge sedimentation failures.

---

## Architecture

```
L1  System Injection   MEMORY.md — key points + anchors        (auto-loaded every session)
L2  Project Core       project-core.md — stable facts + ADR     (rarely changes)
L3  Dev Status         dev-status.md — progress/params/issues     (updates with progress)
L4  Daily Journal      YYYY-MM-DD.md — session log              (per-session)
```

## Three Mechanisms

### 1. Auto-Distillation (Episodic → Semantic)

- L4→L3: milestone completed, or referenced across ≥2 sessions
- L3→L2: stable ≥1 month + confirmed fact + likely needed in future
- L2→L1: useful beyond this project (user preferences, general lessons)

### 2. Memory Strength Decay (`last_used`)

- Tag entries with `[last_used: YYYY-MM-DD]`
- >14 days unused → ⚡ rarely used
- >30 days unused → auto-archive

### 3. Zettelkasten Link Enhancement

- Bidirectional `[[...]]` links between L2↔L3
- Check link integrity with the distillation script

## Quick Start

### 1. Initialize a project

```bash
npx pi-memory-strata init-project <project-name>
```

### 2. Run daily maintenance (or schedule with cron)

```bash
npx pi-memory-strata maintain --vault /path/to/vault
```

### 3. Check memory health

```bash
npx pi-memory-strata check --vault /path/to/vault
```

## Installation

### As Pi Extension

```bash
pi install npm:pi-memory-strata
```

### As npm package

```bash
npm install -g pi-memory-strata
```

### Direct usage (no install)

```bash
npx pi-memory-strata <command>
```

## Programmatic API

```typescript
import { MemoryStrata } from 'pi-memory-strata';

const strata = new MemoryStrata({
  vaultPath: '/path/to/obsidian-vault',
  autoArchiveDays: 30,
  staleWarningDays: 14,
});

// Run distillation check
const check = await strata.check();
console.log(check.ok);

// Run daily maintenance
const report = await strata.maintain();
console.log(report.health);

// Initialize new project
strata.initProject('my-project');
```

## Vault Structure

```
obsidian-vault/
├── 00-brain/
│   └── MEMORY.md              # L1: System injection
├── 10-journal/
│   ├── maintenance/           # Daily maintenance reports
│   ├── summary/               # Auto-generated daily summaries
│   └── 2026-01-01.md        # L4: Daily logs
├── 20-projects/
│   └── my-project/
│       ├── dev-status.md    # L3: Development status
│       └── project-core.md  # L2: Project core archive
├── 30-knowledge/
├── 60-learnings/
│   └── archive/             # Auto-archived entries
├── scripts/
│   ├── memory_distill_check.py
│   └── daily_memory_maintenance.py
└── templates/
    ├── 01-status.md
    └── 02-core.md
```

## Daily Maintenance (Automated)

Schedule daily maintenance with cron or systemd:

```bash
# Every day at 09:30
30 9 * * * npx pi-memory-strata maintain
```

Maintenance performs:
1. **Journal coverage check** — verify last 7 days have logs
2. **Dev status freshness** — warn if >7 days without update
3. **Core archive freshness** — warn if >30 days without update
4. **Memory decay** — identify entries with stale `last_used`
5. **Anchor integrity** — verify memory anchors exist
6. **Bidirectional links** — check L2↔L3 link completeness
7. **Auto-archive** — move >30d stale entries to `60-learnings/archive/`
8. **Daily summary** — generate previous day's summary

## Academic Context

| Concept | Source | This Package |
|---------|--------|-------------|
| Write-Manage-Read loop | arXiv:2603.07670 | W(journal) + M(distill/decay) + R(search) |
| Episodic→Semantic promotion | A-MEM (NeurIPS 2025) | L4→L3→L2 distillation |
| Memory strength decay | MemoryBank (2024) | `last_used` + 30-day archive |
| Zettelkasten linking | A-MEM | Obsidian `[[...]]` bidirectional links |
| Atomic facts | AtomMem (2026) | Memory anchors with consequence tags |

## License

MIT
