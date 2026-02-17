# Prompt Engineering

How to structure information flowing into and out of LLM workloads,
and why the two directions have fundamentally different requirements.

## Semantic bytecode

A prompt is not a conversation. It is a program — a compressed
encoding of intent, context, and constraints that an LLM executes.
The analogy to bytecode is precise: just as a compiler strips source
code down to the semantic operations a VM needs to execute, a
well-engineered prompt strips natural language down to the semantic
operations an LLM needs to reason about.

```
Source code          →  Compiler  →  Bytecode        →  VM
Human understanding  →  Prompt    →  Semantic payload →  LLM
```

The compiler analogy clarifies what belongs in a prompt and what
does not. Bytecode does not contain comments for other programmers.
It does not contain whitespace for readability. It does not contain
the developer's uncertainty about whether they chose the right
approach. It contains exactly the operations the VM will execute,
in the most compact form the VM can consume.

A prompt engineered to this standard:
- Uses precise technical terms over explanatory sentences
  ("implement memoization" not "store the results so you don't
  have to calculate them again")
- Carries hierarchical structure (dense problem statement, then
  decision-relevant context, then detail on demand)
- Omits social niceties, hedging, and conversational padding
- Includes constraints and invariants, not wishes and preferences

Every token in the prompt that does not contribute to the LLM's
reasoning is waste. Not aesthetic waste — economic waste.

## Token economics

The context window is a fixed-size resource. Tokens spent on noise
are tokens unavailable for signal. This is not a soft preference;
it is a hard constraint with measurable consequences.

### The cost model

Three costs compound:

1. **Financial cost.** API pricing is per-token. Padding a 500-token
   semantic payload with 2000 tokens of conversational prose
   quadruples the cost with zero additional value.

2. **Attention cost.** The transformer attention mechanism processes
   all tokens. Noise tokens compete with signal tokens for attention
   weight. A prompt diluted with irrelevant context produces worse
   reasoning than the same semantic content presented cleanly.

3. **Displacement cost.** Context window space occupied by noise
   cannot be occupied by useful context. In a long-running agent
   session, this displacement compounds: each turn's noise crowds
   out material that subsequent turns need.

### The semantic waist connection

The semantic waist (`docs/semantic-waist.md`) is this principle
applied to data flow between agent sessions. Each convergence point
crystallises diffuse understanding into structured data so that the
next divergence starts from concentrated signal rather than
re-mining prose.

The same economics apply within a single session. When a skill
prompt says "read `decisions.md` and figure out what stage the
project is at," it is asking the LLM to spend tokens recovering
information that exists in structured form. When it says "call
`consultamatron project progress`," it gets the same information
for zero tokens. The waist is a token-economic optimisation: route
bookkeeping through deterministic software so the LLM's token
budget is spent on analytical judgment.

Every architectural decision in Consultamatron that moves work from
prose to structure — the CLI, the entity model, the typed DTOs, the
gate protocol — is a token-economic decision. The semantic waist is
not a software engineering affectation. It is the mechanism by which
the system spends its inference budget on thinking rather than
parsing.

### Information architecture, not information density

Density alone is not the goal. A prompt compressed to illegibility
is dense but not useful — the LLM cannot reason about what it
cannot parse. The goal is *information architecture*: structure that
makes the semantic payload navigable.

The Agent Skills standard (`docs/open-standards.md`) embodies this
with progressive disclosure: metadata (~100 tokens) loaded at
startup, instructions (<5000 tokens) loaded on activation, resources
loaded on reference. The agent carries the full skill catalogue at
low cost and pays the full context price only for the skill it
actually invokes. This is hierarchical density — maximum information
available, minimum information loaded, structure determining what
loads when.

The same principle applies to file context. Giving an agent a
directory tree and letting it request specific files is information
architecture. Pasting every file into the prompt is bulk transfer.
Both deliver the same information; only one respects the token
budget.

### The description field as API contract

The SKILL.md `description` frontmatter field is not documentation. It
is an API contract that determines when the skill activates. The agent
loads all descriptions at startup (~100 tokens each) and uses them to
match user intent to skills. All triggering logic must go in the
description (loaded always), not the body (loaded on demand).

Write the description in third person. Include both what the skill
does and when to use it. A description that says "Identify customer
segments" is less effective than one that says "Identify customer
segments and value propositions for a Business Model Canvas. Use after
bmc-research is complete and brief.agreed.md exists." The second
version encodes preconditions that the agent can match against project
state.

## Context management

Token economics describes the cost of individual prompts. Context
management extends this to the full agent session — the accumulated
context across multiple tool calls, skill loads, and conversation
turns.

### Context rot

As a context window fills, model accuracy degrades. At N tokens, the
transformer maintains N² pairwise attention relationships. Each token
added dilutes the attention available to every existing token. This is
not a cliff — it is a gradient. The agent gets gradually worse at
tracking earlier instructions, honouring constraints, and maintaining
consistency.

Countermeasures: progressive disclosure (load only what is needed now),
compaction (summarise and discard intermediate reasoning), and bounded
subagent contexts (delegate subtasks to fresh context windows). All
three are structural — they are built into the skill architecture, not
applied ad hoc. The semantic waist is the most powerful countermeasure:
it replaces thousands of tokens of prose with a CLI call that returns
structured data at zero context cost.

### Context engineering

Context engineering is the successor to prompt engineering. Where prompt
engineering optimises a single prompt, context engineering optimises the
full information environment: system prompts, tool responses, skill
loading, long-horizon state, and cross-session memory.

The framing: find the smallest set of high-signal tokens that maximise
the likelihood of the desired outcome. Every architectural decision that
moves information from prose to structure — the CLI, the entity model,
the gate protocol, the SKILL.md progressive disclosure model — is a
context engineering decision.

### Scaling rules in prompts

Agents cannot self-judge appropriate effort. A research skill will
research indefinitely unless told to stop. An analysis skill will add
nuance until the context window fills. Tell agents explicitly how much
work a task warrants: research depth, iteration rounds, evidence
threshold, word count targets. These are scaling rules — they calibrate
agent effort to task importance.

Freedom levels (high/medium/low) are one expression of this. Another is
explicit instruction bounds: "identify 3-5 user needs" rather than
"identify user needs." The bound prevents both under- and over-delivery.

## Operational patterns

The skillset pipeline embodies several agent architecture patterns
identified in the Anthropic skills engineering literature.

### Prompt Chaining

A sequential pipeline where each step's output feeds the next step's
input. This maps directly to skillset pipelines: research → needs →
supply chain → evolution → strategy. Gate artifacts are the data
flowing between stages. Each skill reads its prerequisite gate and
proposes a new gate. The pipeline is a chain of prompts connected by
deterministic artifacts.

### Evaluator-Optimizer

One agent generates output, another evaluates it, and they loop until
a quality threshold is met. In Consultamatron, this maps to the
propose-negotiate-agree loop with the human operator as evaluator. The
agent proposes, the operator evaluates, and they iterate until the
operator agrees. The pattern is the same; the evaluator is human rather
than automated.

### Pipeline idempotency

Skills should be stateless transformations: read gates, propose new
gates. Running a skill twice against the same input should produce the
same proposal (modulo LLM nondeterminism). State lives in gate
artifacts, not in skill execution. A skill that modifies shared state
as a side effect of execution breaks this property and makes the
pipeline fragile — the order of re-execution matters, partial failures
corrupt state, and recovery requires manual intervention.

## Style as affordance

Everything above applies to the *input* side — information flowing
toward the LLM. The output side has different requirements, because
the audience changes.

The LLM's output crosses a boundary: from a system that processes
tokens to a human who processes meaning through socio-cultural
pattern matching. Style is the affordance that makes this boundary
crossing work.

### Why style is not decoration

Decoration is applied after the fact and can be removed without
information loss. Style is structural — it modifies how the payload
is received, processed, and retained by the human reader.

Consider two presentations of the same strategic finding:

> **Dense:** Component X is at evolution stage Custom (0.35) with
> 4 dependents and no commodity alternative. Recommend build,
> protect IP.

> **Styled:** Component X sits in the most dangerous quadrant of
> the map — custom-built, load-bearing, and irreplaceable. Four
> capabilities depend on it. There is no off-the-shelf alternative.
> This is not a component to outsource. This is a component to
> invest in and defend.

The semantic content is identical. The impact is not. The styled
version activates threat-assessment heuristics, loss aversion, and
protective instinct. These are not rational additions to the
argument — they are affordances for the cognitive architecture that
will process it. The styled version is received differently because
it engages different neural pathways on arrival.

Style warms up socio-cultural associated engrams. It primes the
wetware. A finding delivered in the right register lands in a
context of existing associations — professional identity, pattern
libraries built from experience, emotional valences attached to
strategic concepts — that the dense version does not activate.

### The directional model

The information flow through an LLM workload has two legs with
different optimisation targets:

```
Human intent                          Human understanding
     │                                       ▲
     ▼                                       │
  Compile                                 Style
     │                                       ▲
     ▼                                       │
  Semantic bytecode ──→ LLM ──→ Semantic payload
```

**Inbound (human → LLM):** Compile for the machine. Strip style,
maximise semantic density, structure for attention efficiency. The
LLM does not benefit from rhetorical framing, emotional resonance,
or narrative arc. It benefits from precise terms, explicit
constraints, and clean structure.

**Outbound (LLM → human):** Dress for the audience. Wrap the
semantic payload in style that provides affordance for human
cognition. The human benefits from rhetorical framing, emotional
resonance, and narrative arc — not because these add information,
but because they activate the cognitive infrastructure that
processes information.

This is not "make it pretty." It is a recognition that human
cognition is not a token processor. It is a pattern-matching system
that runs on association, affect, and narrative. Style is the
interface adapter between two fundamentally different information
processing architectures.

### Business before pleasure

The directional model implies an ordering discipline: semantic
bytecode first, style second. Get the payload right, then wrap it.

This is not a stylistic preference. It is an engineering
constraint. Style applied to a wrong conclusion is persuasive
misinformation. Style applied to a correct conclusion is effective
communication. The semantic content must be verified before the
style layer is applied.

In Consultamatron, this manifests as a pipeline:

1. **Research** produces claims with citations (semantic content)
2. **Analysis** produces structural findings (semantic content)
3. **Strategy** produces recommendations with evidence (semantic
   content)
4. **Tours** wrap findings in narrative for specific audiences
   (style layer)
5. **Editorial voice** applies the Consultamatron character (style
   layer)

Steps 1-3 are compiled to be machine-efficient: dense, structured,
cross-referenced. Steps 4-5 are styled to be human-effective:
narrative, contextualised, voiced. The pipeline enforces the
ordering — you cannot style what you have not yet established as
true.

### Style is audience-specific

Dense semantic content is audience-independent — a finding is a
finding regardless of who reads it. Style is audience-dependent —
the same finding needs different affordances for a board member, an
engineer, and an operations manager.

The Wardley Mapping skillset illustrates this: it has six narrative
presentations (executive, investor, technical, operations, onboarding,
competitive) but one atlas of analytical views. The atlas is the
semantic content. The presentations are the style layer, each tuned
to activate the right cognitive context for its audience.

## Implications for skill design

### Skill prompts should be semantic bytecode

A skill's `SKILL.md` is consumed by an LLM. It should be
engineered as semantic bytecode: precise instructions, explicit
constraints, structured context. No motivation, no encouragement,
no conversational framing. The LLM does not need to be told why
the task matters or how it should feel about the work.

### Skill outputs should carry style when human-facing

When a skill produces content that humans will read — tour prose,
atlas analyses, the synthesis in `resources/index.md` — style is
part of the deliverable. The editorial voice skill exists because
style is not a polish step but a functional requirement of
human-facing output.

### The waist separates the two concerns

Structured data (the semantic waist) carries the machine-readable
payload. Prose artifacts carry the styled human-readable output.
The waist never needs style — it is consumed by software. The
prose always needs style — it is consumed by humans. Mixing the
two (putting prose in the structured layer, or leaving the human
layer unstyled) degrades both.

## Summary

Prompt engineering has two faces, and they point in opposite
directions. Inbound: compile to semantic bytecode — dense,
structured, precise, stripped of everything the LLM does not
need. Outbound: dress the payload in style — narrative,
contextual, voiced, tuned to activate the cognitive affordances
of the human audience.

The semantic waist is the architectural embodiment of the inbound
principle. The editorial voice is the architectural embodiment of
the outbound principle. Between them, the LLM does what it is
good at: reasoning over structured input to produce analytical
conclusions. It is not asked to parse prose for buried facts
(that is the waist's job) and it is not asked to deliver findings
as data tables (that is the style layer's job).

Business before pleasure. Semantic bytecode before style. Both
are load-bearing.
