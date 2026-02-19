---
type: article
---
# Needs: Jedi Council

## Invocation

Summon the SWE jedi council.

The subject is the jedi council use case itself. We have a
[content convention](../semantic-packs.md) for storing knowledge in
dual-fidelity packs. We have an [analysis of knowledge protocols](../knowledge-protocols.md)
establishing that protocols emerge when use cases consume pack items
structurally, and that the pantheon protocol is the first concrete
instance. We have an [engagement protocol](../engagement-protocol.md)
that orchestrates skillset pipelines through gate artifacts.

The jedi council is the use case that makes the pantheon protocol
real. Without it, luminaries are reference material. With it, they
are analytical instruments.

Consider the invocation semantics of `practice jedi <scope> <problem>`.
The problem is free text — the operator's question. The scope is the
subject of analysis: an artifact the operator has produced, a project
they are managing, an engagement they are steering, or a client they
are researching. The scope is not the knowledge domain — that is
resolved from context.

Two requirements constrain the design. First, the council must access
relevant knowledge token-efficiently: read `_bytecode/` summaries
to select luminaries, read full items only for those selected, load
subject context at the appropriate compression level. Second, the
output must be pedagogic: the operator should learn the domain
vocabulary by seeing named frameworks applied to their specific
subject, with citations that link back to the knowledge pack for
follow-up reading.

Deliberate on the domain model, the scope resolution, the output
format, and the architectural boundaries. Produce a deliberation
that serves as the specification for implementation.

---

## Deliberation

### 1. Domain model

The jedi council use case operates on four concepts:

**Subject** — the thing being analysed. The operator names it; the
system resolves it to a scope level and loads appropriate context.

```
AnalysisSubject:
  level: artifact | project | engagement | client
  reference: str        ← what the operator provided
  context: loaded material the council examines
```

Four scope levels form a containment hierarchy. Each includes
everything below it:

| Level | Operator provides | System loads |
|---|---|---|
| Artifact | File path | The artifact, pipeline position, skillset context |
| Project | Project slug | Gate artifacts, decisions, pipeline position |
| Engagement | Engagement slug | Projects (summarised), engagement log, research |
| Client | Client slug | Engagements (summarised), research pack |

Narrower scope means fewer tokens and sharper analysis. The operator
names the level by naming the subject.

**Problem** — free text. The operator's question about the subject.
No structure imposed.

**Knowledge domain** — which skillset's knowledge packs to draw on.
Resolved from the subject's skillset by default. A Wardley Mapping
project draws on the WM pantheon and patterns. An SWE project draws
on the SWE pantheon and patterns. Optional override via `--domain`
flag for cross-domain analysis.

**Council request** — the assembled input to the use case:

```
JediCouncilRequest:
  subject: AnalysisSubject
  problem: str
  knowledge_domain: Skillset    ← default: subject's skillset
```

### 2. Scope resolution

The scope argument is a slug or a path. Resolution follows
specificity order, mirroring how git resolves refs:

```
1. Is it a file path that exists?                → artifact scope
2. Is it a project slug in the active engagement? → project scope
3. Is it an engagement slug for the active client? → engagement scope
4. Is it a client slug?                           → client scope
5. Ambiguous                                      → ask the operator
```

Slash-qualified slugs disambiguate when needed:

```
practice jedi maps-1 "is the brief complete?"
practice jedi strat-1 "what should we do next?"
practice jedi holloway-group "summarise the state"
practice jedi holloway-group/strat-1/maps-1 "..."
practice jedi ./brief.agreed.md "did we miss anything?"
```

The resolution mirrors the workspace directory structure. The
operator already navigates `clients/{client}/engagements/{engagement}/{project}/`.
Slash-qualified slugs follow the same hierarchy without requiring
full paths.

The scope resolution module hides two decisions that will change:
what context to load for each level (today: read files; tomorrow:
use `_bytecode/` where available), and how to compress loaded
context (today: read full artifacts; tomorrow: progressive
disclosure through the bytecode mirror). The interface is stable;
the implementation behind it evolves.

```
resolve_scope(reference: str, workspace: Path) → AnalysisSubject
load_context(subject: AnalysisSubject) → AnalysisContext
```

### 3. Knowledge resolution

The council draws on all knowledge protocols available in the
subject's skillset docs pack. If the subject is an SWE project,
the council consults the SWE pantheon, patterns, principles, and
anti-patterns. Resolution:

1. Identify the subject's skillset (from project → engagement →
   skillset chain)
2. Find the skillset's docs pack (e.g. `personal/swe/docs/`)
3. Read `_bytecode/` for the pantheon to select luminaries
4. Read `_bytecode/` for patterns, principles, and anti-patterns
   to make the full domain vocabulary available during analysis

Luminary selection is the core structural operation. The council
reads pantheon `_bytecode/` summaries, matches invocation triggers
against the problem statement, and selects 5-7 luminaries. Only
selected luminaries are read in full. This is the token-efficiency
mechanism: 16 luminaries compressed to summaries, 5-7 expanded to
full items.

Patterns, principles, and anti-patterns are available as reference
during analysis but are not pre-selected. Each luminary perspective
draws on whichever domain vocabulary is relevant. Beck cites Simple
Design and YAGNI. Larman cites GRASP. The council does not load all
40 patterns — it cites them by name and the output links to the
pack items.

### 4. Council execution

The use case, once subject, problem, and knowledge are assembled:

1. **Frame the problem.** Restate the operator's problem in the
   context of the loaded subject. "The operator asks whether the
   brief for maps-1 is complete. The project is at stage 1 of the
   Wardley Mapping pipeline. The next gate is `brief.agreed.md`."

2. **Select the council.** From `_bytecode/` summaries, select
   luminaries whose invocation triggers match the problem domain.
   Architecture question → Parnas, Martin, Cockburn. Process
   question → Beck, DeMarco, Weinberg. Design question → Larman,
   Fowler, Liskov. Typically 5-7 members.

3. **Invoke each perspective.** For each selected luminary, read the
   full pantheon item and analyse the subject through that luminary's
   framework. Each perspective is grounded in the luminary's specific
   contribution, not generic advice.

4. **Synthesise.** Where does the council agree? Where does it
   diverge? What is the actionable recommendation? The synthesis
   identifies consensus, names dissent, and proposes a concrete
   path forward.

5. **Cite sources.** Every framework, pattern, principle, or
   anti-pattern mentioned in the deliberation is cited with its
   location in the knowledge pack. The operator can follow any
   citation to the full item.

### 5. Output format: the deliberation

The council's output is a deliberation. The format serves two
audiences simultaneously: the operator who needs an answer, and the
operator who is building their own domain understanding.

```
## Deliberation: {problem summary}

**Subject**: {scope level} — {reference}
**Council**: {selected luminaries, comma-separated}
**Knowledge domain**: {skillset name}

### {Luminary Name} ({framework})

{Analysis of the subject through this luminary's framework.
References specific patterns, principles, or anti-patterns by
name. Applies the framework to the specific subject, not to the
problem in the abstract.}

*Recommendation:* {one-line actionable recommendation}

### {Next luminary...}

...

### Synthesis

**Consensus:** {where the council agrees}

**Divergence:** {where it disagrees and why}

**Recommendation:** {actionable path forward}

### Council sources

| Source | Type | Location |
|---|---|---|
| Kent Beck | luminary | `docs/pantheon.md` |
| Simple Design | principle | `docs/principles.md` |
| Strategy | pattern | `docs/patterns.md` |
| God Object | anti-pattern | `docs/anti-patterns.md` |
```

The council sources table is the pedagogic mechanism. Each entry
names a concept the operator encountered in context and links to
the full reference. Over repeated invocations, the operator
accumulates domain vocabulary by seeing it applied to their own
work.

The deliberation header establishes what was analysed and who
analysed it. The per-luminary sections show distinct frameworks
applied to the same subject. The synthesis resolves disagreement
into action. The sources table converts the deliberation into a
learning aid.

### 6. Architectural boundaries

The jedi council use case sits at the use case layer. It depends
downward on entities (AnalysisSubject, Skillset, PackItem) and
upward on nothing. The CLI command is an adapter that parses the
operator's input and calls the use case.

```
[CLI adapter]          [use case]              [entities]

practice jedi          JediCouncilUseCase      AnalysisSubject
  parses scope    →      resolve_scope     →    PackItem
  parses problem         load_context           Skillset
                         select_luminaries
                         invoke_perspectives
                         synthesise
                    →    format_deliberation
```

The convention layer (semantic packs, pack-and-wrap) is
infrastructure. The use case reads packs through the PackItem
protocol. It does not know about `_bytecode/` file layout — that
is hidden behind context loading.

The knowledge protocol layer (pantheon contract, pattern contract)
is use case concern. The jedi council knows that a pantheon item
has contribution and invocation trigger. It does not know how the
item is stored or compressed.

The scope resolution module hides workspace topology. The knowledge
resolution module hides pack discovery. The context loading module
hides compression strategy. Each can evolve independently.

### 7. What to build first

The council's consensus on sequencing, applying Simple Design:

1. **CLI command**: `practice jedi <subject> "<problem>"`. One
   positional argument for scope, resolved by specificity. No
   flags in v1.

2. **Scope resolution**: path → project → engagement → client.
   Requires active workspace context. Ambiguity asks the operator.

3. **Context loading**: read files directly. No `_bytecode/`
   optimisation in v1 — that requires pack-and-wrap (#99) to be
   implemented first.

4. **Knowledge resolution**: find the skillset's docs pack. Read
   the pantheon. Select luminaries. Use patterns/principles/
   anti-patterns as reference vocabulary during analysis.

5. **Deliberation output**: the format described above. Council
   sources table included from v1 — the pedagogic mechanism is
   not optional.

Add later, when concrete need appears:
- `--domain` flag for cross-domain analysis
- `_bytecode/` optimised context loading (after #99)
- Engagement inference (omit scope, resolve from active project)
- Dot-qualified knowledge targeting (`swe.pantheon`)
- Progressive pedagogic disclosure (track what the operator has
  seen across invocations)
