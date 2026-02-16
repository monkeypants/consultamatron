# Strategy: Outcome Alignment

Assess whether the target skillset produces good client outcomes,
beyond structural and methodological compliance.

## When to Load

Target is structurally sound but unclear whether it produces
outcomes that clients value. Useful when conformance passes
but operator has doubts about effectiveness.

## Method

### 1. Decision log review

If the target has been used in prior engagements, examine
decision logs for:
- Rework patterns (same type of change revisited across cycles)
- Time-to-agreement per stage (proxy for negotiation friction)
- Fields recorded at gates (do they capture meaningful metrics?)

Source: `clients/{org}/engagements/{engagement}/{project}/decisions.json`

### 2. Review document analysis

If `review` skill has been run on target engagements:
- What themes recur across reviews?
- Were issues identified that the pipeline didn't catch?
- Did completed engagements lead to follow-on work?

Source: `clients/{org}/review.md`, engagement review artifacts

### 3. Deliverable value assessment

For each deliverable the target produces:
- Does the client use it after delivery?
- Does it inform decisions or sit on a shelf?
- Would the client pay for this deliverable independently?

This requires operator knowledge of client reception — the
agent cannot assess this from artifacts alone.

### 4. Change impact risk assessment

For changes the assessment recommends:
- Which changes improve client outcomes (vs process compliance)?
- Which changes risk degrading outcomes that currently work?
- What is the reversibility cost if a change makes things worse?

### 5. Outcome metrics

Compile available outcome indicators:
- Engagement completion rate
- Client re-engagement rate (if known)
- Rework frequency per pipeline stage
- Time-to-agreement trend across engagements

## Output

`assessment/strategies.md` section containing:
- Decision log analysis findings
- Review theme summary
- Deliverable value assessment (per deliverable)
- Change impact risk matrix
- Outcome metrics with interpretation
