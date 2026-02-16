# Strategy: Situational Scan

Assess whether the target skillset's pipeline still fits the
landscape it was designed for.

## When to Load

The operational interview suggests the target's assumptions may
not match the current context: users have changed, the market has
evolved, or the pipeline was designed for a situation that no
longer exists.

## Method

### 1. Context reconstruction

Identify the assumptions the target was designed under:
- Who were the intended users when the pipeline was created?
- What did the competitive/commodity landscape look like?
- What delivery constraints existed?

Source this from design documents, skill file preambles, and
operator recollection.

### 2. Anchor drift detection

Compare the original context to the current one:
- Have the target's users changed roles, skills, or expectations?
- Has the problem domain been redefined by market shifts?
- Are there new stakeholders the pipeline doesn't account for?

For each drift, record the original anchor and current reality.

### 3. Evolution mismatch detection

Check whether the target pipeline does custom work where
commodities or established practices now exist:
- Are there stages that could be replaced by standard tools?
- Does the pipeline build from scratch what could be purchased?
- Has the domain codified practices the target still treats as novel?

### 4. Commoditisation scan

For each deliverable the target produces:
- Is this deliverable now available as a commodity service?
- Has the format been standardised since the target was created?
- Could a simpler pipeline produce equivalent client value?

## Output

`assessment/strategies.md` section containing:
- Context reconstruction summary
- Anchor drift findings (original vs current, per anchor)
- Evolution mismatch findings with evidence
- Commoditisation opportunities
- Situational fitness finding: does the pipeline serve its
  actual current users, or a past version of them?
