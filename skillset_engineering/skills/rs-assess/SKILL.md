---
name: rs-assess
description: >
  Assess the quality of an existing skillset against structural,
  methodological, and operational criteria. Reads the target skillset's
  BC package, conformance test results, usage feedback, and domain
  research to produce a quality assessment. Identifies what works,
  what doesn't, and where the methodology has drifted from the domain.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: refine-skillset
  stage: "1"
---

# Skillset Quality Assessment

You are assessing the quality of an existing consulting skillset.
This is a diagnostic phase — you are finding what needs improvement,
not making changes yet.

## Prerequisites

The operator must identify the **target skillset** being refined.
Check that:
- The target skillset exists: `uv run practice skillset show --name {target}`
- The target BC package exists with `__init__.py`, `presenter.py`, and `tests/`
- Organisation research exists at `resources/index.md` in the project dir

If the target skillset does not exist or is not implemented, this skill
cannot proceed.

## Step 1: Structural assessment

Run the conformance tests against the target skillset:

```bash
uv run pytest -m doctrine -v 2>&1 | grep {target_bc_package}
```

Check each structural property:

### Pipeline coherence
- Do gates chain correctly (each stage's prerequisite = previous produces)?
- Are stage descriptions unique?
- Does the slug pattern contain `{n}`?

### BC completeness
- Does `__init__.py` export SKILLSETS and PRESENTER_FACTORY?
- Does `presenter.py` implement the ProjectPresenter protocol?
- Does `tests/test_presenter.py` exist with doctrine-marked tests?
- Do skill symlinks exist in `.claude/skills/`?

### Skill file quality
For each skill in the pipeline:
- Does `SKILL.md` exist with valid frontmatter?
- Does it have a prerequisites section?
- Does it have step-by-step methodology?
- Does it reference a bash wrapper script?
- Does the bash wrapper invoke the correct CLI commands?

Record findings to `assessment/structural.md`.

## Step 2: Methodological assessment

Read the target skillset's research and design documents (if they
exist from a `new-skillset` project), then read each skill file.

Evaluate:

### Domain fidelity
- Does the methodology match the domain's actual practices?
- Are domain terms used precisely and consistently?
- Has the domain evolved since the skillset was created?

### Semantic bytecode quality
If the skillset has reference files:
- Do they follow the L0-L3 hierarchy?
- Are token budgets respected?
- Does progressive disclosure work (each level adds without
  contradicting)?
- Is vocabulary precise (no ambiguous paraphrasing)?

### Deliverable quality
For each deliverable the skillset produces:
- Is the format clearly specified?
- Are quality criteria testable?
- Does the presenter render them correctly?

### Process quality
- Are gate artifacts the right checkpoints?
- Is the propose-negotiate-agree loop clearly documented?
- Are bash wrappers documenting all CLI operations correctly?

Record findings to `assessment/methodological.md`.

## Step 3: Operational assessment

Gather evidence from usage:

### Feedback sources
- Read any review documents from `review` skill outputs
- Check GitHub issues tagged with the skillset name
- Ask the operator for qualitative feedback

### Usage patterns
- Which stages do operators spend the most time on?
- Where do negotiations stall?
- What questions do operators ask that the skill files don't answer?
- Are there common workarounds?

### Token efficiency
- How large are the skill files? Could they be compressed?
- Are reference files loaded unnecessarily?
- Could bytecode levels be reorganised for better progressive
  disclosure?

Record findings to `assessment/operational.md`.

## Step 4: Synthesise assessment

Write `assessment/assessment.md` combining all three dimensions:

```markdown
# Quality Assessment: {Target Skillset}

## Summary

{2-3 paragraph overview of overall quality and key findings}

## Scorecard

| Dimension | Rating | Key Issues |
|-----------|--------|------------|
| Structural | {Good/Adequate/Poor} | {1-line summary} |
| Methodological | {Good/Adequate/Poor} | {1-line summary} |
| Operational | {Good/Adequate/Poor} | {1-line summary} |

## Strengths

1. {What works well — preserve these}
2. ...

## Issues

### Critical (blocks effective use)

1. **{Issue title}** — {description, evidence, impact}

### Important (degrades quality)

1. **{Issue title}** — {description, evidence, impact}

### Minor (polish)

1. **{Issue title}** — {description, evidence, impact}

## Recommendations

{Ordered list of improvements, most impactful first.
Each recommendation should reference specific issues above.}
```

## Step 5: Present to operator

Present the assessment. Ask:

1. "Does this assessment match your experience using this skillset?"
2. "Are there issues I've missed?"
3. "Do the priority ratings feel right?"
4. "Are there constraints on what we can change (e.g. existing
   projects in flight, external dependencies)?"

## Step 6: Iterate and agree

Based on operator feedback, update the assessment. When agreed:
1. Write `assessment.agreed.md`
2. Record the decision:
   ```
   skillset_engineering/skills/rs-assess/scripts/record-assessment-agreed.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Target={target skillset}" \
     --field "Critical={count}" \
     --field "Important={count}" \
     --field "Minor={count}"
   ```

## Monotonic improvement property

The refine-skillset methodology is designed so that **every iteration
improves quality**. This stage's output is a strictly prioritised
issue list. The next stage (rs-plan) selects the highest-impact
improvements. The stage after (rs-iterate) executes them. Even a
single iteration cycle must leave the skillset measurably better.

## Completion

When `assessment.agreed.md` is written, tell the operator the next
step is `rs-plan` to create an improvement plan targeting the most
impactful issues.
