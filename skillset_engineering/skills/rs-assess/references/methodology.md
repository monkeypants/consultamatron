# Methodology — Skillset Quality Assessment

## Five-Phase Process

### Phase 1: Structural scan (agent-autonomous)

- Input: Target skillset identifier
- Output: `assessment/structural.md`
- Method: Run conformance tests, check pipeline mechanics, apply
  mechanically-testable subset of 7 coherence criteria (gate chaining,
  unique descriptions, file structure)
- Decision: None — this is mechanical verification. Proceed to Phase 2
  regardless of results.

### Phase 2: Operational interview (human-primary)

- Input: Structural findings (for context)
- Output: `assessment/operational.md`
- Method: Present structured probes about the operator's experience
  using the target skillset. Record responses verbatim.
- Probes:
  - "Which stages feel most/least useful in the target?"
  - "Where do you find yourself working around the process?"
  - "Which gates do you carefully evaluate vs rubber-stamp?"
  - "Has the context this skillset serves changed since it was created?"
  - "Where does the agent load material that doesn't help?"
- Decision: Operator identifies which areas feel problematic.

### Phase 3: Fitness evaluation (human + agent)

- Input: Operational interview, structural findings
- Output: `assessment/fitness.md`
- Method: Apply the 7 pipeline coherence criteria using interview
  evidence. Formulate fitness functions as evaluable predicates.
  Agent proposes predicates, human confirms whether they test the
  right things.
- Decision: Operator validates that fitness functions capture real concerns.

### Phase 4: Methodological assessment (collaborative)

- Input: Target's skill files, bytecode, references
- Output: `assessment/methodological.md`
- Method: Agent reads target artifacts and applies smell catalogue.
  Human provides tacit domain knowledge. Evaluate skill files against
  agentskills-way standard. Check domain fidelity, vocabulary precision,
  progressive disclosure quality.
- Decision: Collaborative classification of methodology findings.

### Phase 5: Synthesis and strategy selection

- Input: All dimension findings
- Output: `assessment/assessment.md`, `assessment/strategies.md`
- Method: Select strategies based on findings (see strategy selection
  table). Load each selected strategy and apply its method to deepen
  the assessment. Synthesise into fitness function table.
- Decision: Operator agrees assessment captures the full picture.

## Strategy Selection

| What assessment reveals about the target | Strategies to load |
|------------------------------------------|-------------------|
| Passes checks but operator reports friction | smell-detection, human-leverage-audit |
| Pipeline designed for different context | situational-scan |
| Process overhead disproportionate to changes | vertical-slice-test |
| Agent performance or context window issues | context-efficiency |
| Conformant but quality uncertain | fitness-functions, outcome-alignment |
| Operator rubber-stamps gates | human-leverage-audit, vertical-slice-test |

Load fitness-functions strategy by default — it replaces maturity
ratings with evaluable predicates and is always applicable.

## Smell Catalogue

### Structural smells
- **Phantom gate**: Gate artifact referenced but never produced or checked
  - Detection: search for gate paths not matching pipeline definition
- **Orphan reference**: Reference file exists but no skill loads it
  - Detection: cross-reference skill file references with files on disk
- **Brittle join**: Two artifacts depend on string equality that could drift
  - Detection: search for joins between decision titles and stage descriptions

### Methodological smells
- **Parrot methodology**: Skill file repeats domain vocabulary without grounding
  - Detection: terminology present but no definitions or citations
- **Token bloat**: Reference material loaded that doesn't influence decisions
  - Detection: measure which loaded references change agent output
- **Vocabulary drift**: Same concept named differently across skill files
  - Detection: extract domain terms per skill, check for synonyms

### Operational smells
- **Rubber stamp**: Gate consistently approved without negotiation
  - Detection: operator reports auto-approving certain gates
- **Negotiation desert**: No feedback loop between stages
  - Detection: pipeline is strictly linear with no iteration paths
- **Workaround prevalence**: Operators skip or modify steps informally
  - Detection: operator describes common workarounds

### Pipeline smells
- **Ceremony debt**: Process overhead disproportionate to change risk
  - Detection: count steps and artifacts per unit of typical change
- **Horizontal lock**: Must complete entire pipeline before any value
  - Detection: check whether partial pipeline produces usable output
- **Missing feedback loop**: Later-stage insights cannot reach earlier stages
  - Detection: check for mechanisms to propagate late findings backward

## Quality Criteria

- Every finding cites specific evidence
- Fitness functions are evaluable (pass/fail/partial, not subjective)
- Strategy selection is justified by assessment findings
- Assessment distinguishes agent-verifiable from human-sourced findings
- Synthesis does not introduce findings absent from dimensional assessments

## Anti-Patterns

- Rating dimensions Good/Adequate/Poor without evaluable criteria
- Running all strategies regardless of findings (wastes tokens)
- Treating structural conformance as sufficient for quality
- Synthesising before gathering human signal
- Assuming operational quality from structural compliance
