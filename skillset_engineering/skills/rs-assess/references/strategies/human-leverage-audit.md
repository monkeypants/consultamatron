# Strategy: Human Leverage Audit

Evaluate whether the target skillset uses the human's time on
tasks where human judgement is genuinely needed.

## When to Load

Operator reports rubber-stamping gates, feels the pipeline
doesn't use their time well, or describes approval fatigue.

## Method

### 1. Per-stage information advantage analysis

For each stage in the target pipeline, determine:
- Who has the information advantage (agent or human)?
- What decision is being made at the gate?
- Could the agent make this decision autonomously?
- Does the human bring irreplaceable signal (tacit knowledge,
  client relationships, situational awareness)?

Record as a table:

| Stage | Gate decision | Info advantage | Human contribution |
|-------|--------------|----------------|-------------------|
| ... | ... | Agent / Human / Shared | ... |

### 2. Walking skeleton assessment

Attempt a thin vertical slice across all target stages:
- For each stage, identify the minimum human input needed
- Check whether that input is requested at the right time
- Note where the human is asked to confirm what the agent
  already knows vs provide new information

### 3. Agent-human allocation map

Classify each stage interaction:
- **Agent-autonomous**: Agent can complete with no human input
- **Human-sourced**: Human provides primary signal, agent structures
- **Collaborative**: Both contribute substantive information
- **Human-approves**: Agent does work, human confirms (potential waste)

Flag any "human-approves" classification — these are candidates
for either removing the gate or restructuring so the human
provides signal rather than approval.

### 4. Leverage ratio

Count across the target pipeline:
- Stages where human provides unique signal
- Stages where human only approves agent output
- Calculate ratio: signal-stages / total-human-stages

A low ratio suggests the pipeline under-uses human capabilities.

## Output

`assessment/strategies.md` section containing:
- Per-stage allocation table
- Walking skeleton findings
- Leverage ratio with interpretation
- Specific recommendations for reallocating human effort
