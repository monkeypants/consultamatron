---
type: scenario
---

# Worked Example: Gatepoint in canvas-1

End-to-end trace of the observation-routing pattern through a
concrete scenario using a fictional client workspace.

## Context

- **Client:** acme-corp
- **Engagement:** strategy-1 (status: planning, allowed_sources: commons, personal)
- **Project:** canvas-1 (skillset: business-model-canvas, status: implementation)
- **Inflection point:** gatepoint — `segments.agreed.md` just negotiated
- **Sibling projects:** consult-1 (consulting), maps-1 (wardley-mapping)

## Step 1: Agent requests observation needs brief

```
practice observation-needs --client acme-corp --engagement strategy-1 --project canvas-1
```

The agent recognises the gatepoint as an inflection point and
requests the brief before the transient negotiation context
evaporates.

## Step 2: CLI builds the routing table (deny-all, allow-some)

| Destination | Eligible | Rule applied |
|---|---|---|
| personal/ skillsets | Yes | Always allowed |
| acme-corp client workspace | Yes | Client's own data |
| strategy-1 engagement | Yes | Engagement specified |
| canvas-1 project (BMC) | Yes | Project specified |
| consult-1 project (consulting) | Yes | Sibling in same engagement |
| maps-1 project (wardley-mapping) | Yes | Sibling in same engagement |
| commons/ skillsets | No | Dark channel only (#23) |
| Other clients | No | Denied by default |
| Other engagements | No | Engagement boundary is information barrier |

Sibling projects within the same engagement are eligible.
The engagement is the trust boundary, not the project. Everything
within an engagement shares a confidentiality context.

## Step 3: CLI gathers needs from eligible destinations

### Type-level needs (from type definitions)

The guiding principle: "what are we able to improve?" Information
needs are driven by the ability to act on the information — solving
problems, mitigating risks, achieving goals, driving continuous
improvement.

- **Client workspaces** need: stakeholder dynamics, constraints,
  preferences, decision patterns (improves: client service quality,
  delivery calibration)
- **BMC skillset** needs: segment validity signals, value proposition
  resonance, channel effectiveness (improves: methodology accuracy)
- **Engagements** need: process friction, timeline pressure, scope
  creep signals (improves: engagement delivery)
- **Practice layer** needs: infrastructure gaps, tooling friction
  (improves: platform effectiveness)

### Instance-level needs (from specific destinations)

- **acme-corp workspace:** "client has strong opinions about vendor
  selection — watch for procurement preferences that constrain
  delivery options"
- **canvas-1 project:** "core deliverable for funding round — watch
  for signals about what will convince investors"
- **maps-1 project:** "cross-references canvas customer segments —
  watch for segment assumptions that might not survive strategic
  analysis"
- **personal/ BMC skillset:** "watch for cases where segment
  negotiation reveals methodology gaps"

### Deduplication

The same BMC skillset appears via canvas-1's type-level needs and
personal/'s instance-level needs. These collapse to a single set.
The "large table of needs" problem is imaginary — distinct needs
deduplicate naturally.

## Step 4: CLI synthesises the brief

The brief is a structured artifact — markdown with frontmatter for
machine consumption (Python entities via repository), prose body
for agent consumption. Use cases operate in Python land through
the semantic waist; LLM-facing output is derived.

**Synthesised brief (agent-facing rendering):**

> Client knowledge (acme-corp):
> - Stakeholder dynamics, constraints, decision patterns
> - Vendor selection preferences
>
> Project knowledge (canvas-1, consult-1, maps-1):
> - Segment assumptions that might not survive strategic analysis
> - Signals about what will convince investors
>
> Methodology (business-model-canvas):
> - Segment negotiation methodology gaps
> - Value proposition resonance signals
>
> Engagement (strategy-1):
> - Process friction, timeline pressure, scope creep

## Step 5: Agent applies brief to gatepoint context

During segment negotiation, the operator said: "I don't think the
government sector segment will fly — the sponsor thinks public
procurement is too slow."

The agent, guided by the brief, extracts:

**Observation 1 — client domain:**
Sponsor has procurement speed as a decision criterion. Routes to:
acme-corp workspace. (Drives: delivery calibration — future
engagements should account for this preference.)

**Observation 2 — project domain:**
Government segment rejected on procurement grounds, not product-market
fit. Routes to: canvas-1 decisions log, maps-1 notes. (Drives:
maps-1 should note this constraint is political not structural,
consult-1 should be aware of the framing.)

**Observation 3 — methodology domain:**
Segment rejection reasons should distinguish "bad fit" from "client
constraint." The BMC methodology doesn't currently surface this
distinction. Routes to: personal/business-model-canvas. (Drives:
methodology improvement — add rejection-reason classification to
segment negotiation.)

## Questions this scenario surfaces

1. **Instance-level needs authoring.** Who writes "watch for vendor
   selection preferences"? The operator during engagement setup?
   The agent based on research findings? Both? (Likely both — the
   operator sets initial needs, the agent proposes refinements as
   client knowledge accumulates.)

2. **Brief size at scale.** This scenario: 3 projects, ~15 needs.
   A larger engagement with 10 projects — does the brief stay usable?
   (Deduplication should help, but needs monitoring.)

3. **Observation granularity.** The agent extracted 3 observations
   from one operator remark. Is that the right level? One observation
   per destination served, or one observation routed to multiple
   destinations? (Design question for the observation entity.)
