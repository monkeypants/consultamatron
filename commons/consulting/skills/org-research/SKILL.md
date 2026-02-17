---
name: org-research
description: >
  Research a real organisation for strategic consulting. Negotiates a
  research strategy with the operator, executes research tasks, confirms
  findings are sufficient, then compresses results into a token-efficient
  semantic bytecode hierarchy. Creates the client workspace if it does
  not exist. Use when onboarding a new client or refreshing research.
metadata:
  author: monkeypants
  version: "0.3"
---

# Organisation Research

You are conducting **organisation research** for a consulting engagement.
Your goal is to gather publicly available information about a real
organisation, structured for use by any downstream skillset.

Research produces two parallel outputs:
- A **human-friendly tree**: prose synthesis pointing to primary
  research reports (token-inefficient, for the operator)
- A **semantic bytecode hierarchy**: L0/L1/L2 compressed
  representation derived from the primary research (token-efficient,
  for downstream agent processes)

## Before you start

Check `clients/` for existing workspaces. If one exists for this
organisation, you may be refreshing research — see
[Refreshing research](#refreshing-research).

If no workspace exists, ask the operator for:
1. **Organisation name** (and URL if available)
2. **Workspace path** (default: `./clients/{org-slug}/`)

Initialize the workspace:
```
org-research/scripts/init-workspace.sh --client {org-slug}
```

Then create the resources directory structure:
```
mkdir -p clients/{org-slug}/resources/reports
mkdir -p clients/{org-slug}/resources/bytecode
```

See [workspace-layout.md](assets/workspace-layout.md) for the full
workspace convention.

## Step 1: Propose research strategy (Gate 1)

Before any research work begins, negotiate a research strategy with
the operator.

### Assess initial signals

Gather preliminary information about the organisation's public
presence. Check whether a corporate website exists, whether there
is recent press coverage, job postings, regulatory filings, and
whether sources are consistent.

### Select and propose strategy

Read [research-strategies.md](references/research-strategies.md) for
available strategies. Based on initial signals, propose:

1. **Which strategy** to use and why
2. **Which research tasks** to execute (elaborated from the strategy)
3. **Expected sources** for each task
4. **Any modifications** to the default task list (additions,
   removals, or scope changes based on what the signals suggest)

Present to the operator. This is a negotiation — the operator may:
- Change the strategy
- Add, remove, or modify research tasks
- Narrow or expand scope for specific tasks
- Provide insider knowledge that changes the approach

### Agree and record

When the operator confirms the strategy, write
`resources/strategy.agreed.md` recording:
- Chosen strategy and rationale
- Agreed research tasks (the specific list to execute)
- Any operator-provided context that shapes the research

**Do not begin research until the strategy is agreed.**

## Step 2: Execute research

Run the agreed research tasks. Where possible, run them **in
parallel** to maximise throughput. Each task produces a report in
`resources/reports/`.

Reports must follow the template in
[research-template.md](references/research-template.md):

- Every factual claim must have a citation with URL
- Include a confidence level (High / Medium / Low) with reasoning
- Include a "Strategic Relevance" section
- Use direct quotes where possible
- Each report must reference at least 3 distinct sources

After each report is written, register it:
```
org-research/scripts/register-topic.sh --client {org-slug} \
  --topic "{topic name}" --filename "{filename}.md" --confidence "{level}"
```

## Step 3: Review findings (Gate 2)

After all research tasks are complete, write
`resources/summary_prose.md` — a human-readable synthesis that:

1. Summarises findings across all research tasks
2. Identifies themes that cut across topics
3. Notes contradictions or gaps
4. Highlights strategic implications:
   - Who the organisation's users likely are
   - What core capabilities appear to be
   - Where technology or market evolution is happening
   - What constraints exist (regulatory, contractual, technical)
5. Points to each report in `resources/reports/` for detail

### Verify citation density

Before presenting to the operator:
- Every factual claim in every report must have an inline citation
- Each report must reference at least 3 distinct sources
- If any report falls below threshold, fix it before proceeding

### Present and negotiate

Present `summary_prose.md` to the operator. The operator decides:

- **Research is sufficient** — proceed to compression
- **Specific areas need more depth** — return to Step 2 for those
  areas, then present again
- **New tasks needed** — agree additional tasks, execute, present again

**Do not proceed to Step 4 until the operator confirms primary
research is complete.**

## Step 4: Compress into semantic bytecode

Derive a token-efficient three-tier representation from the primary
research. All three tiers are token-efficient. This is the **narrow
semantic waist** that downstream skills consume.

### L2: Compressed detail

For each semantic cluster of related findings, write a compressed
detail file to `resources/bytecode/`. Each L2 file:
- Summarises the findings from one cluster of related reports
- Uses precise vocabulary aligned with downstream consumer needs
- Routes to the specific reports in `resources/reports/` for evidence

### L1: Cluster summaries

For each group of related L2 files, write an L1 summary to
`resources/bytecode/`. Each L1 file:
- Summarises and routes to its L2 files
- Characterises what kinds of questions the cluster answers
- Uses vocabulary that downstream skills search for

### L0: Index

Write `resources/index.md` — the root of the semantic bytecode
hierarchy and the gate artifact for this skill. The index:

- Provides a compressed summary of all research findings
- Routes to each L1 cluster summary with a characterisation of
  what it contains and what questions it answers
- Points to `summary_prose.md` for human-readable access
- Records the research strategy used and task manifest

**Design priorities for L0**: The index serves two purposes equally —
compressing information into a token-efficient summary, and making
information findable by routing downstream skills to the right L1
resources. Neither purpose is subordinate to the other.

The index is the primary input for downstream skills and the gate
artifact for this skill.

## Refreshing research

When research already exists:
1. Read `resources/index.md` for existing state
2. Check dates in the manifest — identify stale topics
3. Return to Step 1 to negotiate a refresh strategy with the
   operator (which topics to re-research, whether the strategy
   itself should change)
4. Execute the agreed refresh tasks, update reports and synthesis
5. Recompress the semantic bytecode hierarchy

## Completion

When all artifacts are written, summarise what you found and tell
the operator to use the `engage` skill to plan their consulting
engagement, or to invoke a specific skillset skill directly if they
already know what they want.
