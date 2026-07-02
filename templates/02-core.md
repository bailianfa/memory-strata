# {{PROJECT_NAME}} — Project Core Archive

> Last updated: {{YYYY-MM-DD}}
> Type: L2 (Project Core)

---

## Hardware Selections

| Component | Model | Status | Rationale |
|-----------|-------|--------|-----------|
| **CPU/SoC** | {{model}} | {{selected / testing}} | {{reason}} |
| **WiFi/BT** | {{model}} | {{selected / testing}} | {{SRRC certified, avoid re-research}} |
| **Camera IR** | {{model}} | {{selected / testing}} | {{global shutter for eye tracking}} |
| **Camera RGB** | {{model}} | {{selected / testing}} | {{4K for fundus imaging}} |
| **Display** | {{model}} | {{selected / testing}} | {{resolution, interface}} |
| **Touch** | {{model}} | {{selected / testing}} | {{capacitive/resistive}} |

## Architecture Decision Records (ADR)

### ADR-001: {{Decision Title}}
- **Context**: {{Why this decision was needed}}
- **Decision**: {{What was chosen}}
- **Consequences**: {{Trade-offs and implications}}
- **Date**: {{YYYY-MM-DD}}

### ADR-002: {{Decision Title}}
- **Context**: {{Why this decision was needed}}
- **Decision**: {{What was chosen}}
- **Consequences**: {{Trade-offs and implications}}
- **Date**: {{YYYY-MM-DD}}

## Memory Anchors

> These are facts that are easy to forget but costly to lose. Do NOT re-research these.

- **{{Anchor title}}**: {{Anchor content}} — [last_used: {{YYYY-MM-DD}}]
- **{{Anchor title}}**: {{Anchor content}} — [last_used: {{YYYY-MM-DD}}]

## Build & Deployment

| Environment | Details |
|-------------|---------|
| **Build** | {{Build method, e.g., WSL2 Ubuntu 22.04}} |
| **Compiler** | {{aarch64-buildroot-linux-gnu-gcc}} |
| **Deployment** | {{scp/rsync method}} |
| **Remote** | {{user@host}} |

## External References

- **Hardware Docs**: {{Link to datasheets}}
- **SDK Docs**: {{Link to SDK documentation}}
- **Vendor Contact**: {{Vendor name, contact}}

---

## Bidirectional Links

- [[{{Dev Status}}]] ← current development progress and recent decisions

---
*Auto-maintained by [pi-memory-strata](https://github.com/bailianfa/pi-memory-strata)*
