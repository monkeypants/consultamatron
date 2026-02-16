---
name: ca-research
description: >
  Kick off a Six Simple Rules Complexity Audit. Reads shared organisation
  research, agrees audit scope with the client, creates the project
  directory, and produces an audit brief. Use when starting a new
  complexity audit for a client that has already been researched.
metadata:
  author: cybertrack01
  version: "0.1"
  skillset: six-simple-rules-complexity-audit
  stage: "1"
---

# Complexity Audit Project Kickoff

You are starting a new **Six Simple Rules Complexity Audit**. Your goal
is to agree on the audit scope with the client, set up the project
directory, and produce an audit brief that frames the diagnostic work.

## Prerequisites

Check that the client workspace contains:
- `resources/index.md` (shared research gate)

If missing, tell the user to run `org-research` first.

Identify the project directory. Either:
- The user specifies a project slug
- The `engage` skill has already created one (check the engagement's
  `projects.json`)
- You create one using the convention `audit-{n}` (check existing
  projects to determine `n`)

The project path is
`clients/{org}/engagements/{engagement}/{project-slug}/`.

## Background: Six Simple Rules

The Six Simple Rules framework (Yves Morieux, Boston Consulting Group)
addresses organisational complexity by focusing on cooperation rather
than adding structure. The six rules are:

1. **Understand What People Really Do** — observe actual behaviours
   and the rational strategies people adopt to cope with complexity
2. **Reinforce Integrators** — strengthen roles and units that
   naturally coordinate across silos
3. **Increase Total Quantity of Power** — create new power bases so
   that cooperation is not zero-sum
4. **Extend the Shadow of the Future** — make the consequences of
   today's actions visible to those making decisions
5. **Increase Reciprocity** — remove buffers and self-sufficiency
   that allow people to avoid cooperation
6. **Reward Those Who Cooperate** — shift incentives from individual
   metrics to collective outcomes, making transparency safe

The audit diagnoses how the organisation performs against each rule,
then synthesises recommendations.

## Step 1: Read research

Read `resources/index.md` and all sub-reports in `resources/`.

Identify:
- Organisational structure and reporting lines
- Known pain points, bottlenecks, or coordination failures
- How teams interact (or fail to)
- Incentive structures and performance management
- Recent reorganisations or transformation programmes
- Customer-facing complexity symptoms (delays, errors, handoffs)

## Step 2: Propose audit scope

Present an audit brief to the client:

```markdown
# Complexity Audit Brief — {Organisation Name}

## Scope

{What this audit will examine: the whole enterprise, a specific
division, a cross-functional process, or a transformation programme}

## Hypothesis

{Initial reading on where complexity is concentrated and why,
based on research}

## Focus areas

{Which of the six rules the research suggests are most relevant}

## Out of scope

{What this audit will not cover}

## Information needs

{What additional access or data would strengthen the diagnostic —
e.g. org charts, survey results, process documentation}
```

## Step 3: Negotiate and agree

This is a negotiation. The client may:
- Narrow or widen the scope
- Redirect focus to specific rules or problem areas
- Provide additional context about internal dynamics

Iterate until the client confirms.

When the client agrees:
1. If the project is not yet registered, register it now:
   ```
   engage/scripts/register-project.sh --client {org} --engagement {engagement} \
     --slug {slug} --skillset "six-simple-rules-complexity-audit" \
     --scope "{agreed scope}"
   ```
   If the project already exists in the registry, skip this step.
2. Create the project directory (if not already created):
   ```
   {project-slug}/
   └── diagnostics/
   ```
3. Write `brief.agreed.md` with the agreed scope
4. Record the brief agreement and activate the project:
   ```
   ca-research/scripts/record-brief-agreed.sh --client {org} \
     --engagement {engagement} --project {slug} \
     --field "Scope={agreed scope}" --field "Focus areas={list}"
   ```

## Completion

When all artifacts are written, summarise the agreed scope and tell the
user the next step is `ca-diagnose-understanding` to begin the Rule 1
diagnostic: understanding what people really do.
