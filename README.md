# memory-strata

Four-layer stratified memory architecture for long-horizon AI agent projects.

Solves the three most common memory failures in projects that span months to years:

1. **Critical fact forgetting** — screen orientation, component selection, build constraints lost between sessions
2. **Memory bloat** — information only accumulates, never decays or archives
3. **Knowledge stays episodic** — insights trapped in daily logs, never distilled into reusable knowledge

## Architecture

```
L1  System Injection   MEMORY.md — key points + anchors        (auto-loaded every session)
L2  Project Core       项目核心档案.md — stable facts + ADR     (rarely changes)
L3  Dev Status         开发状态.md — progress/params/issues     (updates with progress)
L4  Daily Journal      YYYY-MM-DD.md — session log             (per-session)
```

## Three Mechanisms

### 1. Auto-Distillation (Episodic → Semantic)

- L4→L3: milestone completed, or referenced across ≥2 sessions
- L3→L2: stable ≥1 month + confirmed fact + likely needed in future
- L2→L1: useful beyond this project (user preferences, general lessons)

### 2. Memory Strength Decay (`last_used`)

- Tag entries with `[last_used: YYYY-MM-DD]`
- >14 days unused → ⚡ rarely used
- >30 days unused → consider archiving

### 3. Zettelkasten Link Enhancement

- Bidirectional `[[]]` links between L2↔L3
- Check link integrity with the distillation script

## Memory Anchors

Explicitly mark facts that are easy to forget but costly to lose:

```markdown
- **Screen is landscape**: board defaults to portrait, product uses landscape — do not forget
- **AP6256 already selected**: SRRC certified, mainstream choice — do not re-research
```

## Quick Start

1. Copy `templates/` to your Obsidian vault under `20-projects/<your-project>/`
2. Fill in the project core file with stable facts
3. Add anchors to your `MEMORY.md` (L1)
4. Run the distillation check at session end:

```bash
python scripts/memory_distill_check.py
```

## Installation as DuMate Skill

Copy the `memory-strata/` directory to your DuMate skill installation path.

## Academic Context

| Concept | Source | This Skill |
|---------|--------|-----------|
| Write-Manage-Read loop | arXiv:2603.07670 | W(journal) + M(distill/decay) + R(search) |
| Episodic→Semantic promotion | A-MEM (NeurIPS 2025) | L4→L3→L2 distillation |
| Memory strength decay | MemoryBank (2024) | `last_used` + 30-day archive |
| Zettelkasten linking | A-MEM | Obsidian `[[]]` bidirectional links |
| Atomic facts | AtomMem (2026) | Memory anchors with consequence tags |

## License

MIT
