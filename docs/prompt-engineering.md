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

This is why Consultamatron has six tour audiences (executive,
investor, technical, operations, onboarding, competitive) but one
atlas. The atlas is the semantic content. The tours are the style
layer, each tuned to activate the right cognitive context for its
audience.

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
