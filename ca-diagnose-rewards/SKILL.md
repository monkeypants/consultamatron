---
name: ca-diagnose-rewards
description: >
  Diagnose Rule 6 of the Six Simple Rules: Reward Those Who Cooperate.
  Investigates whether incentive systems reward cooperation or
  individual performance at the expense of collective outcomes.
  Produces a diagnostic report that must be agreed before proceeding.
  Use after ca-diagnose-reciprocity is complete.
metadata:
  author: cybertrack01
  version: "0.1"
  skillset: six-simple-rules-complexity-audit
  stage: "7"
---

# Rule 6 Diagnostic: Reward Those Who Cooperate

You are conducting the **Rule 6 diagnostic** of a Six Simple Rules
Complexity Audit. This rule asks: do the organisation's incentives
reward cooperation, or do they reward individual performance even
when it undermines collective outcomes?

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md`
- `diagnostics/rule1-understanding.agreed.md`
- `diagnostics/rule2-integrators.agreed.md`
- `diagnostics/rule3-power.agreed.md`
- `diagnostics/rule4-future.agreed.md`
- `diagnostics/rule5-reciprocity.agreed.md`

If `diagnostics/rule5-reciprocity.agreed.md` is missing, tell the
user to complete `ca-diagnose-reciprocity` first.

The project path is
`clients/{org}/engagements/{engagement}/{project-slug}/`.

## The rule

**Reward Those Who Cooperate** — when individual metrics dominate,
people optimise for their own numbers even at collective cost. The
solution is not simply adding team metrics, but making transparency
non-threatening: blame those who don't cooperate, not those who
surface problems. Reward the cooperative behaviour, not just the
individual result.

Key diagnostic question: **Do people who cooperate — who help
others, surface problems, accept short-term cost for collective
benefit — get rewarded or punished for it?**

## Step 1: Review prior diagnostics

Read all five agreed diagnostics. The full picture of the
organisation's cooperation dynamics is now available. Rewards
either reinforce or undermine everything diagnosed in Rules 1-5.

## Step 2: Investigate

### Formal incentives
- What are people measured on? Individual KPIs, team metrics,
  or collective outcomes?
- How are bonuses, promotions, and raises determined?
- Do performance reviews assess cooperation or just output?

### Informal incentives
- What behaviour gets publicly recognised or praised?
- Who gets promoted — cooperators or solo performers?
- What does "high performer" mean in practice?

### Blame and transparency
- When problems surface, is the messenger rewarded or punished?
- Do people hide failures to protect their metrics?
- Is it safe to admit that a team needs help?

### Cooperation penalties
- Do people who spend time helping others fall behind on their
  own metrics?
- Is cross-functional work recognised in performance reviews?
- Do secondments or rotations help or harm career progression?

### Evidence sources
- Performance management frameworks and criteria
- Promotion patterns and who gets ahead
- Recognition programmes and what they celebrate
- How failures and mistakes are handled publicly
- Exit interview themes about cooperation and culture

## Step 3: Draft diagnostic

Write `diagnostics/rule6-rewards.md`:

```markdown
# Rule 6 Diagnostic: Reward Those Who Cooperate

## Summary

{Assessment of how incentives affect cooperation}

## Formal incentive analysis

### Performance metrics
{What is measured and how it affects cooperation}

### Promotion criteria
{What actually gets people promoted}

### Compensation structure
{How pay relates to individual vs collective outcomes}

## Informal incentive analysis

### Recognition patterns
{What behaviour is publicly celebrated}

### Blame dynamics
{How failures and problems are handled}

### Cooperation safety
{Whether it is safe to help others at personal cost}

## Assessment

**Rating**: Strong / Adequate / Weak / Critical

**Key findings**:
- {Finding 1}
- {Finding 2}

## Connections to prior rules

{How incentives reinforce or undermine the dynamics found in
Rules 1-5. This is the capstone diagnostic — it should reference
all prior findings.}

## Evidence

- From `resources/{file}`: "{relevant finding}"
```

## Step 4: Present and negotiate

Present the diagnostic. Ask:
1. "Do these incentive dynamics ring true?"
2. "Who in the organisation cooperates despite the incentives?"
3. "What would need to change for cooperation to be rewarded?"

## Step 5: Iterate and agree

When the client agrees:
1. Copy to `diagnostics/rule6-rewards.agreed.md`
2. Record the agreement:
   ```
   ca-diagnose-rewards/scripts/record-agreement.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Rating={assessment rating}" \
     --field "Key findings={summary}"
   ```

## Completion

When `diagnostics/rule6-rewards.agreed.md` is written, tell the user
the next step is `ca-aggregate` to coalesce all six diagnostics into
a unified picture with cross-cutting patterns and complexity hotspots.
