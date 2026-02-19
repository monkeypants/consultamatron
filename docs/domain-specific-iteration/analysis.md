# The Need for Domain-Specific Iteration

Why skillset-specific findings do not belong in the Consultamatron
GitHub repository, and what that implies about the architecture of
improvement.

## The specimen

A multi-project engagement — Business Model Canvas and Wardley Mapping,
executed sequentially for the same client — produced nine review
findings. The review skill instructs the agent to sanitise these
findings and raise them as GitHub issues on
`monkeypants/consultamatron`. This article argues that doing so would
be a category error for most of them.

The nine findings divide cleanly into two groups.

### Group A: platform findings

- **Decision recording is fragile.** The practice CLI broke during the
  engagement because of merge conflicts on a co-located branch. Four
  stage decisions were lost. Gate artifacts survived (written manually),
  but the decision log has gaps.
- **Record scripts reference the wrong CLI name.** At least one wrapper
  script invokes `consultamatron` instead of `practice`.

These are infrastructure problems. They affect every skillset equally.
They live below any bounded context boundary. They belong in the
GitHub repository because they are about the army, not about a
specific campaign.

### Group B: skillset findings

- **bmc-segments does not test alternative revenue architectures.** The
  skill treats revenue as a secondary attribute of each segment. The
  engagement's most important insight — a shift from grant-based to
  project-based revenue — came from the client, not the skill.
- **bmc-canvas checks content but not framing.** A tension was
  factually correct but interpretively wrong. The skill's review
  questions did not catch this.
- **wm-chain over-decomposes.** 30 components produced, immediately
  consolidated to 22. The skill permits "15-30" but steers toward the
  upper bound.
- **Three WM stages were rubber-stamped.** The client accepted needs,
  evolution, and strategy without modification. The skill prompts
  specific questions that generated no engagement.
- **No meeting preparation skill exists.** The engagement's goal was to
  prepare for a meeting. No skill converts analytical artifacts into
  presentation materials.
- **No cross-project synthesis mechanism.** Two projects informed each
  other, but the cross-referencing was manual and accidental.

The last two could go either way — they describe capability gaps in the
overall pipeline. But the first four are unmistakably about how a
specific methodology works. "bmc-segments should probe revenue models
harder" is a statement about the Business Model Canvas methodology's
internal quality. "wm-chain over-decomposes" is a statement about how
the Wardley Mapping supply chain decomposition skill operates.

These are domain-specific observations. Raising them as issues on the
Consultamatron repository conflates two categories of change.

## The conflation

The Consultamatron repository is a platform. It contains the practice
CLI, the conformance test framework, the engagement protocol, the
semantic waist, the site renderer, the BC discovery mechanism. These
are shared infrastructure — they create the conditions under which
any skillset can operate.

Each skillset is a bounded context. The Wardley Mapping BC contains a
domain model (evolution characteristics, value chains, strategic
plays), a pipeline (research → needs → chain → evolve → strategy), and
domain-specific skill files that encode how to execute each stage. The
Business Model Canvas BC contains a different domain model (segments,
value propositions, nine blocks), a different pipeline (research →
segments → canvas), and different skill files.

The bounded context boundary exists for a reason. Changes to how
wm-chain decomposes supply chains require understanding of Wardley
Mapping methodology — what a component is, what granularity means in a
value chain, how visibility maps to dependency depth. Changes to the
practice CLI require understanding of the engagement protocol — what a
decision entry is, what status transitions are valid, how the semantic
waist captures convergent conclusions.

These are different knowledge domains. They change for different
reasons. They should change through different mechanisms.

When the review skill dumps all findings into the same GitHub issue
tracker, it creates a repository where "fix the CLI fallback when merge
conflicts occur" sits next to "bmc-segments should ask about revenue
flow" sits next to "wm-chain should default to fewer components." A
contributor looking at the issue list sees a mixture of platform
concerns and methodology concerns, with no way to distinguish which
require platform expertise and which require domain expertise.

This is the familiar monolith failure mode, applied to issue tracking
instead of code.

## What domain-specific iteration actually requires

The review findings about wm-chain and bmc-segments are not wrong. They
are real observations from a real engagement, grounded in evidence. The
agent over-decomposed the supply chain. The segments skill did not
surface the revenue model. These things happened and they represent
genuine improvement opportunities.

But they require a specific kind of improvement process.

### Domain context

Fixing "wm-chain over-decomposes" requires someone (human or agent) to
understand what supply chain decomposition means in Wardley Mapping,
read the existing wm-chain skill file, understand why the recursive
decomposition guidance produces fine-grained output, and propose a
change that preserves the methodology's integrity while guiding toward
coarser initial granularity.

This is not a generic code review. It is a methodology review. The
reviewer needs domain fluency.

### Evidence accumulation

One engagement where wm-chain over-decomposes is a data point. Two
engagements is a pattern. Five engagements where the client consistently
consolidates 30 components to 20 is a mandate. The improvement
mechanism should accumulate evidence across engagements before
committing to a change.

A GitHub issue captures a single observation. It does not accumulate.
A new observation about the same problem becomes a comment on the
existing issue — which is better than a duplicate, but still a flat
list of anecdotes rather than a structured evidence base.

### Fitness evaluation

The `rs-assess` skill exists precisely for this purpose. It evaluates a
skillset against fitness functions — testable predicates about whether
the skillset serves its current purpose. "wm-chain produces an initial
component count within 15-25 for a typical engagement" is a fitness
function. "bmc-segments surfaces at least one alternative revenue
architecture before gate agreement" is a fitness function.

Fitness functions are richer than issue descriptions. They are
evaluable, they have evidence requirements, and they return pass/fail
rather than open-ended "someone should look at this." The `rs-assess` →
`rs-plan` → `rs-iterate` pipeline is the structured improvement
mechanism for a bounded context. It is to skillset quality what the
consulting pipeline is to client deliverables.

Raising skillset-specific issues on GitHub bypasses this mechanism. It
takes evidence that should feed `rs-assess` and dumps it into a generic
issue tracker where it loses its evaluative structure.

## The boundary test

When a review finding arises, apply this test:

**Does fixing this require understanding a specific consulting
methodology, or does it require understanding the Consultamatron
platform?**

If the fix requires methodology knowledge — understanding what a Wardley
Map component is, what a BMC segment means, how evolution positioning
works — it belongs inside that skillset's bounded context. The evidence
should feed `rs-assess`. The improvement should flow through
`rs-plan` → `rs-iterate`.

If the fix requires platform knowledge — understanding the practice CLI,
the engagement protocol, the conformance test framework, the semantic
waist — it belongs in the Consultamatron repository. A GitHub issue is
the right container.

If it is ambiguous — "no meeting preparation skill exists" could be a
platform gap (the pipeline is incomplete) or a domain gap (Wardley
Mapping should produce presentable output) — it likely belongs in the
repository as a strategic discussion about what the platform should
offer. But the implementation, once decided, will be domain-specific
(a new skill, in a specific skillset, with methodology-specific
logic).

## What does not exist yet

This article identifies a problem but does not solve it. The `rs-assess`
pipeline exists and can consume review findings. But several pieces are
missing.

### A feedback channel from review to rs-assess

The review skill produces findings. The `rs-assess` skill consumes
operational evidence. There is no structured channel between them. The
review findings are written to `{project}/review/review.md` and
`{project}/review/findings.md` — files inside a client workspace that
is gitignored. The `rs-assess` skill reads "any existing decision logs"
and "review documents from prior review skill outputs" — but this
assumes the same agent, in the same session, with the same client
workspace mounted.

A durable channel is needed. Review findings about a specific skillset
should be depositable somewhere that `rs-assess` can discover them
later, across sessions and agents.

### A home for accumulated evidence

Each bounded context package (`commons/wardley_mapping/`,
`commons/business_model_canvas/`) contains skill files, references,
scripts, tests, and a presenter. It does not contain an iteration log,
an evidence register, or a fitness function catalogue. These would be
the domain-specific equivalent of the GitHub issue tracker — but
structured for the `rs-assess` pipeline rather than for human triage.

### A governance model for domain-specific changes

The Consultamatron repository has a governance model: branches, pull
requests, human review. Who governs changes to a specific skillset's
methodology? The operator who ran the engagement? The `rs-iterate` skill
executing autonomously? A domain expert who understands the methodology?
The current answer is "whoever runs `rs-iterate`" — but the quality of
the iteration depends on the quality of the evidence and the judgment
applied.

## The meta-issue

This article is itself a meta-issue. It is about the architecture of
improvement — how the Consultamatron Army manages its own evolution. It
belongs in the repository because it is about the platform, not about
any specific methodology.

The findings from a recent engagement are real. The wm-chain
over-decomposition is real. The bmc-segments revenue gap is real. The
rubber-stamp stages are real. But they are evidence, not issues. They
are observations that should feed a structured improvement process
inside their respective bounded contexts, not tickets in a generic
tracker where they lose their domain context and evaluative structure.

The review skill's instinct to capture and publish findings is correct.
The destination is wrong. Each bounded context needs its own iteration
surface — a place where evidence accumulates, fitness functions are
defined, and improvements are planned and executed with domain fluency.

What that surface looks like is an open design question. The pieces
exist (`rs-assess`, `rs-plan`, `rs-iterate`, the BC package structure,
the review skill's evidence collection). The integration does not.
