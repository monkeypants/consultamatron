# Strategy: Smell Detection

Pattern-based search through the target skillset's artifacts
for indicators of quality problems.

## When to Load

Target passes structural checks but the operator reports friction,
or the assessment across dimensions feels incomplete — something
is wrong but no single finding captures it.

## Method

### 1. Artifact collection

Gather the target's assessable artifacts:
- Skill files (SKILL.md for each pipeline stage)
- Pipeline definition in `__init__.py`
- Reference files (bytecode hierarchy, detail files)
- Bash wrapper scripts
- Presenter and test files

### 2. Structural smell scan

| Smell | Detection heuristic | Indicates |
|-------|-------------------|-----------|
| Phantom gate | Gate path in pipeline definition has no corresponding file pattern in any skill's produces/checks | Dead pipeline branch |
| Orphan reference | File in references/ not loaded by any skill file | Wasted tokens, stale content |
| Brittle join | String equality between decision titles and stage descriptions | Fragile pipeline progression |

### 3. Methodological smell scan

| Smell | Detection heuristic | Indicates |
|-------|-------------------|-----------|
| Parrot methodology | Domain terms used without definitions, citations, or grounding | Superficial domain knowledge |
| Token bloat | Reference files loaded that don't change agent decisions | Wasted context window |
| Vocabulary drift | Same concept named differently across skills | Integration friction, ambiguity |

### 4. Operational smell scan

| Smell | Detection heuristic | Indicates |
|-------|-------------------|-----------|
| Rubber stamp | Operator reports auto-approving certain gates | Gate adds ceremony without value |
| Negotiation desert | No iteration path between stages | Rigid, non-adaptive pipeline |
| Workaround prevalence | Operator describes common informal modifications | Process-reality mismatch |

### 5. Pipeline smell scan

| Smell | Detection heuristic | Indicates |
|-------|-------------------|-----------|
| Ceremony debt | Steps and artifacts disproportionate to typical change risk | Over-engineered process |
| Horizontal lock | No usable output until entire pipeline completes | All-or-nothing delivery |
| Missing feedback loop | No mechanism for late findings to reach earlier stages | Linear-only information flow |

### 6. Severity classification

For each detected smell:
- **Critical**: Blocks effective use of the target
- **Important**: Degrades quality or efficiency
- **Minor**: Cosmetic or low-impact

## Output

`assessment/strategies.md` section containing:
- Smell inventory table: name, evidence, severity
- Smell cluster analysis (do multiple smells share a root cause?)
- Recommended actions per smell
