# Supply Chain Document Templates

## Per-Need Chain Template

Use this for each file in `chain/chains/{need-slug}.md`.

```markdown
# Supply Chain: {Need Name}

## Dependency Tree

{Need Name}
├── {Capability 1}
│   ├── {Sub-capability 1a}
│   │   └── {Sub-sub-capability}
│   └── {Sub-capability 1b}
├── {Capability 2}
│   └── {Sub-capability 2a}
└── {Capability 3}

## Components

| Component | Description | Shared With |
|-----------|-------------|-------------|
| {name} | {what it is, briefly} | {other needs using this} |

## Notes

- {Any observations about this chain — single points of failure,
  surprising dependencies, etc.}

## Evidence

- From `resources/{topic}.md`: {supporting finding}
```

---

## Consolidated Supply Chain Template

Use this for `chain/supply-chain.md`.

```markdown
# Supply Chain — {Organisation Name}

## Dependency Graph

{User Class 1}
├── {Need 1}
│   ├── {Capability}
│   │   └── ...
│   └── {Capability}
├── {Need 2}
│   └── ...

{User Class 2}
├── {Need 3}
│   └── ...

## Shared Components

Components appearing in multiple chains. These are structurally
important — they serve multiple needs and sit at critical junctions
in the value chain.

| Component | Serves Needs | Depth |
|-----------|-------------|-------|
| {name} | {need 1}, {need 2} | {levels from user} |

## Component Inventory

Complete list of all unique components identified.

| # | Component | Depends On | Depended On By | Notes |
|---|-----------|-----------|----------------|-------|
| 1 | {name} | {parents} | {children} | {notes} |

## Observations

- {Structural observations: bottlenecks, single points of failure,
  surprisingly deep chains, missing capabilities, etc.}

## Open Questions

- {Questions for client review}
```

---

## Notes for agents

- Depth in the tree corresponds to visibility in the eventual map.
  Components near the top are visible to users; components at the
  bottom are invisible infrastructure.
- Stop decomposing when you reach commodities or externally-provided
  services. "Electricity" or "Internet connectivity" are usually the
  floor unless the engagement is specifically about infrastructure.
- Do not attempt to position components on the evolution axis. That
  is stage 4. The horizontal axis has no meaning at this stage.
- Shared components are important — flag them clearly. They often
  become strategic leverage points.
