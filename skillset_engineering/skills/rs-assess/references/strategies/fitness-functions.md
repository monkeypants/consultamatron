# Strategy: Fitness Functions

Replace maturity ratings with evaluable predicates about the
target skillset's fitness in its current context.

## When to Load

Always recommended. This strategy replaces Good/Adequate/Poor
ratings with testable predicates, making assessment findings
actionable and progress measurable.

## Method

### 1. Formulate predicates

For each assessment dimension, define predicates that return
pass/fail/partial:

**Pipeline fitness predicates** (structural dimension):
- Gates chain without gaps (prerequisite of N = produces of N-1)
- Every stage description is unique
- Conformance tests pass for all skills in the pipeline
- Skill files are under 500 lines
- Bash scripts are executable

**Methodological fitness predicates**:
- Domain vocabulary is used consistently across all skill files
- Bytecode references follow progressive disclosure (L0 alone
  enables correct high-level decisions)
- Each skill file references methodology grounded in domain research
- Presenter produces valid output for completed projects

**Operational fitness predicates**:
- No gates are routinely rubber-stamped (per operator interview)
- Operator can identify the value of each stage
- No persistent workarounds exist
- Token consumption per stage is proportionate to decision complexity

**Situational fitness predicates**:
- Pipeline serves its current users (not a past version of them)
- Deliverables are still the right format for current context
- No stages do custom work where commodities now exist

### 2. Test each predicate

For each predicate:
- Evaluate against current reality
- Record result: pass / fail / partial
- Cite evidence for the result
- Note confidence level (some predicates require human judgement)

### 3. Template functions

Reusable predicate templates adaptable to any target:

```
PIPELINE_FIT(target): All gates chain AND all conformance tests pass
  → Evidence: test output, pipeline definition
  → Evaluator: agent-autonomous

METHOD_FIT(target): Domain terms consistent AND bytecode progressive
  → Evidence: skill files, reference files
  → Evaluator: agent + human validation

OPERATIONAL_FIT(target): No rubber stamps AND no persistent workarounds
  → Evidence: operator interview
  → Evaluator: human-primary

SITUATIONAL_FIT(target): Users unchanged AND deliverables still relevant
  → Evidence: operator interview + context analysis
  → Evaluator: human + agent
```

### 4. Fitness function table

Compile results:

| Predicate | Result | Evidence | Confidence |
|-----------|--------|----------|------------|
| ... | Pass/Fail/Partial | ... | High/Medium/Low |

## Output

`assessment/strategies.md` section containing:
- Fitness function table with all predicates evaluated
- Cross-cutting findings (predicates that fail across dimensions)
- Comparison with maturity-rating approach (what the predicates
  reveal that ratings would obscure)
