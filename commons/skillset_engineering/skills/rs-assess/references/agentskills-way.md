# The agentskills.io Way

Compact reference for evaluating whether a skillset's skill files
follow the agentskills.io standard. Used during assessment to check
skill file quality beyond structural conformance.

## Three-Tier Architecture

| Tier | Purpose | What it controls |
|------|---------|-----------------|
| Discovery | Agent finds the skill | Name, description, metadata |
| Activation | Agent decides to use it | Prerequisites, frontmatter, description quality |
| Execution | Agent follows the methodology | Steps, references, gate protocol |

## Core Constraints

- Skill file name: kebab-case, ≤64 characters
- Description: ≤1024 characters, describes what the skill does
  (not how) in a way that enables correct selection
- SKILL.md: <500 lines total
- Frontmatter: name, description, metadata (author, version,
  skillset, stage for pipeline skills)
- Bash scripts: executable, in scripts/ subdirectory

## Design Principles

- **Conciseness**: Say it once, at the right abstraction level.
  Skill files instruct; references explain.
- **Degrees of freedom**: Constrain what must be constrained,
  leave room for agent judgement elsewhere. Over-specification
  produces rigid behaviour; under-specification produces drift.
- **Progressive disclosure**: Skill file references bytecode
  hierarchy. Agent loads L0 for decisions, L1-L2 for execution,
  L3 on demand. Each level self-contained.
- **Evaluation-driven development**: Gate artifacts, conformance
  tests, and fitness functions make quality measurable.

## Structural Patterns

- **Template pattern**: Skill provides a fill-in structure for
  the artifact it produces (assessment template, brief template)
- **Feedback loop**: Gate negotiation cycle — propose, present,
  incorporate feedback, agree
- **Conditional workflow**: Steps that branch based on what the
  agent discovers (e.g. strategy selection based on findings)

## Anti-Patterns

- **Monolith skill**: Everything in SKILL.md, no references —
  wastes tokens on runs that don't need full detail
- **Reference sprawl**: Too many small files with unclear loading
  criteria — agent can't decide what to read
- **Implicit knowledge**: Skill assumes agent knows domain
  concepts not defined in any loaded reference
- **Approval theatre**: Gates where the human confirms what the
  agent already verified — wastes human attention

## Quality Checklist

- [ ] Name matches directory and is discoverable
- [ ] Description enables correct selection without reading the file
- [ ] Prerequisites are checkable before starting
- [ ] Steps are ordered and each produces a named artifact
- [ ] References are one level deep from SKILL.md
- [ ] Bash wrappers document all CLI operations
- [ ] Gate protocol follows propose-negotiate-agree
- [ ] Progressive disclosure: L0 alone enables correct decisions

## Theoretical Grounding

Progressive disclosure in skill design mirrors LeCun's Hierarchical
JEPA principle: higher abstraction levels discard detail irrelevant
to decisions at that planning horizon, making predictions more
tractable. L0 (executive) handles strategic decisions with minimal
tokens, just as H-JEPA's upper level forecasts coarse state
evolution. L1-L2 add precision for artifact creation and methodology
execution, as lower JEPA levels handle higher-fidelity short-term
prediction. L3 provides full detail on demand, loaded only when the
decision requires it. Each level is self-contained because each
planning horizon must be independently actionable.

Source: LeCun, "A Path Towards Autonomous Machine Intelligence"
(2022); Bandaru, "Deep Dive into JEPA" analysis of H-JEPA two-tier
structure.
