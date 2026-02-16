# Strategy: Context Efficiency

Evaluate the token economy of the target skillset's agent
interactions.

## When to Load

Target's agent interactions are slow, operator reports the
agent loading material that doesn't help, or skill files
are approaching size limits.

## Method

### 1. Skill file size audit

For each skill in the target pipeline:
- Count lines in SKILL.md (limit: 500)
- Estimate tokens (approx 0.75 tokens per word)
- Identify sections that could be compressed or moved to references

### 2. Reference utilisation check

For each file in the target's references/:
- Is it referenced by any skill file?
- Which skill(s) load it?
- Does the loaded material change agent decisions, or is it
  background that could be deferred to a lower bytecode level?

Flag unreferenced files as orphan references (see smell catalogue).

### 3. Bytecode level allocation

If the target has semantic bytecode references:
- Does L0 fit within 500 tokens?
- Does L1 fit within 1500 tokens?
- Does L2 fit within 3000 tokens?
- Does progressive disclosure work (each level adds without
  contradicting)?
- Is material at the right level (strategic decisions at L0,
  execution detail at L2, deep dives at L3)?

### 4. Skill file clarity assessment

For each skill file:
- Does it explain what the agent already knows vs what it
  needs to learn from references?
- Are instructions actionable without loading all references?
- Could the skill file work with L0+L1 alone for most runs,
  loading L2 only when needed?

### 5. Token waste patterns

Identify common token waste:
- Repeated context across skill files (could be factored into
  shared references)
- Inline explanations that belong in bytecode references
- Verbose instructions that could be compressed
- Defensive repetition of rules stated elsewhere

## Output

`assessment/strategies.md` section containing:
- Size audit table (skill, lines, estimated tokens, utilisation)
- Reference utilisation map (file, referencing skills, decision impact)
- Bytecode allocation findings
- Token waste patterns with evidence
- Pruning and restructuring recommendations
