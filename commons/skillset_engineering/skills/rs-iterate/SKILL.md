---
name: rs-iterate
description: >
  Execute planned improvements to a skillset. Applies each change
  from the agreed plan, verifies acceptance criteria, runs conformance
  tests, and presents results. Produces an iteration report documenting
  what changed and what quality level the skillset now achieves. The
  project can cycle back to rs-assess for further refinement.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: refine-skillset
  stage: "3"
  freedom: low
---

# Skillset Iteration

You are executing planned improvements to an existing skillset.
Follow the plan precisely — this is construction, not design. Every
change has acceptance criteria. Meet them.

## Prerequisites

Check that the project directory contains:
- `assessment.agreed.md` (stage 1 gate)
- `plan.agreed.md` (stage 2 gate)

If missing, tell the operator to complete `rs-plan` first.

Read both documents. The assessment tells you why changes are needed.
The plan tells you exactly what to do.

## Step 1: Baseline

Before making any changes, capture the current state:

```bash
uv run pytest -m doctrine --tb=short 2>&1 > iteration/baseline-doctrine.txt
uv run pytest --tb=short 2>&1 > iteration/baseline-full.txt
```

Record the test counts. After iteration, the counts must not decrease.

Also read the target skillset's current artifacts to understand the
starting point. You cannot verify "before/after" without knowing
"before."

## Step 2: Execute changes in sequence

Follow the execution sequence from `plan.agreed.md`. For each change:

### 2a. Announce

Tell the operator which change you are making and what files will
be modified.

### 2b. Apply

Make the specified changes. Follow the plan's "files to modify"
list. Do not make unplanned changes — even if you spot other issues,
those belong in the next assessment cycle.

### 2c. Verify

After each change, run the acceptance criteria:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -m doctrine
```

The doctrine suite includes `TestSkillFileConformance` which
validates SKILL.md frontmatter (name format, description length,
directory name match), symlink existence, and bash wrapper
executability. If you modified any skill files, bash scripts, or
symlinks, these tests will catch violations.

If any acceptance criterion fails, fix the change before proceeding.
Do not accumulate failures.

### 2d. Record

Write a brief record of the change to `iteration/changes/{n}-{slug}.md`:

```markdown
# Change {n}: {Title}

**Plan reference**: {section in plan.agreed.md}
**Files modified**: {list}

## What changed

{Brief description}

## Acceptance criteria

- [x] {criterion — met}
- [x] {criterion — met}

## Notes

{Anything surprising or notable about the change}
```

## Step 3: Run full verification

After all changes are applied:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -m doctrine -v
uv run pytest -v
```

Compare against the baseline:
- Test count must not decrease
- No new failures
- All planned acceptance criteria met

All skillsets — commons, personal, and partnership — are full BC
packages with doctrine test coverage. The conformance suite applies
uniformly regardless of source.

## Step 4: Write iteration report

Write `iteration/report.md`:

```markdown
# Iteration Report: {Target Skillset}

## Cycle

**Assessment**: {date of assessment.agreed.md}
**Plan**: {date of plan.agreed.md}
**Iteration**: {today}

## Changes applied

| # | Change | Files | Status |
|---|--------|-------|--------|
| 1 | {title} | {count} | {Done/Partial} |
| 2 | {title} | {count} | {Done/Partial} |

## Quality improvement

| Metric | Before | After |
|--------|--------|-------|
| Doctrine tests | {n} pass | {n} pass |
| Total tests | {n} pass | {n} pass |
| Critical issues | {n} | {n} |
| Important issues | {n} | {n} |

## Remaining issues

{Issues from the assessment that were not addressed in this cycle,
with updated priority based on what we learned during iteration}

## Recommendations

{Should the operator run another refine cycle? If so, what should
the next assessment focus on?}
```

## Step 5: Present to operator

Present the iteration report. Show:
1. What changed (with diffs if helpful)
2. Quality metrics before and after
3. Remaining issues and recommendations

Ask:

1. "Are you satisfied with these improvements?"
2. "Should we do another refinement cycle?"
3. "Have any new issues emerged from these changes?"

## Step 6: Agree and close

Based on operator feedback:
1. Write `iteration.agreed.md` (the full report, confirmed)
2. Record the decision:
   ```
   skillset_engineering/skills/rs-iterate/scripts/record-iteration-agreed.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Changes={count}" \
     --field "Tests before={n}" \
     --field "Tests after={n}" \
     --field "Another cycle={yes/no}"
   ```

## Monotonic improvement guarantee

This is the core property of refine-skillset: **every iteration
leaves the skillset strictly better**. This is guaranteed by:

1. The assessment identifies real issues (not speculative ones)
2. The plan selects changes with verifiable acceptance criteria
3. The iteration applies changes only if they pass verification
4. Test counts cannot decrease
5. The report measures improvement quantitatively

If a change cannot be verified as an improvement, it is reverted.
The skillset after iteration is at least as good as before, and
measurably better on the dimensions targeted by the plan.

## Cycling

After `iteration.agreed.md` is written, the project can:
- **Close**: The skillset is good enough for now
- **Cycle**: Start a new `rs-assess` → `rs-plan` → `rs-iterate`
  cycle targeting remaining or newly discovered issues

Each cycle further improves quality. There is no maximum number of
cycles. The operator decides when the skillset is "done enough."

## Completion

When `iteration.agreed.md` is written, tell the operator:
- What quality level the skillset now achieves
- Whether another cycle is recommended
- That they can restart with `rs-assess` at any time
