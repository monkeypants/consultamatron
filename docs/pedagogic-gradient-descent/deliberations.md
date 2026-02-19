# Pedagogic Gradient Descent

Voices are pedagogic strategies (see `docs/voices-protocol/deliberation.md`).
A strategy without a signal is just a style preference. The question that
makes voices useful is: *what does this operator's brain need, right now,
for this concept?* That question requires a model of the operator's
knowledge, an evidence base to calibrate it, and an assessment process to
determine where pedagogical investment should be directed. Voice selection
is a strategy selector pattern, analogous to the research strategy selector:
the system evaluates the learning situation and selects the strategy most
likely to advance understanding.

This is gradient descent. The system measures the operator's current
understanding against target fluency, computes the error, identifies the
steepest learning gradient, and steps downhill — applying voices, probes,
and scaffolding where the gap between current evidence and required
comprehension is largest. The evidence-of-understanding log is the loss
function's input. The knowledge tree defines the surface. The pedagogical
calibrator computes the gradient. The voice executes the step. This is not
an analogy. It is a cybernetic control loop operating on wetware.

More precisely, this is backpropagation. The error signal (gap between
demonstrated understanding and required fluency) propagates backward through
the knowledge tree structure. A failure to apply "strategic plays" correctly
may trace back through "evolution stages" and "value chains" to a root
misunderstanding of "supply chain decomposition." The gradient is steepest
at the deepest unsupported prerequisite, not at the surface-level symptom.
The system must follow the error backward through the concept graph to find
where pedagogic investment will have the most effect.

---

## Deliberation: Operator knowledge modelling and learning needs analysis for calibrated pedagogy

**Subject**: platform — wetware efficiency, voices protocol, operator model
**Council**: Weinberg, Cockburn, Cunningham, Beck, Evans, Brooks, Anthropic
**Knowledge domain**: SWE (platform infrastructure)

---

### Gerald Weinberg (Psychology of Programming / Secrets of Consulting)

The first deliberation treated voice selection as a preference — which voice suits the operator's brain? This reframing asks a harder question: which voice does the operator's brain *need*, right now, for *this* concept?

These are different questions. Preference is static. Need is dynamic. An operator who is expert in evolution theory does not need Feynman explaining evolution stages. They need the analysis and the evidence; they supply the theoretical framework themselves. But the same operator, encountering supply chain decomposition for the first time, might benefit enormously from Garden's deadpan walk-through of why this apparently simple idea is actually doing something quite strange.

The system already has the signal for this. It is in the negotiate loop. Watch how the operator negotiates:

- **High-resolution pushback** ("the evolution position is wrong because the market has more suppliers than this assessment accounts for") = fluency. The operator speaks the methodology's language and applies it to their domain knowledge. No pedagogy needed. Skip the explanation. Deliver the analysis raw.

- **Low-resolution rejection** ("I don't think that's right") = partial comprehension. The operator senses a problem but cannot articulate it in the methodology's vocabulary. Targeted pedagogy: explain *this specific concept* in the context of *their specific objection*.

- **Rubber-stamping** (accepts without comment) = either agreement or incomprehension. Weinberg's Rule of Three applies: if you cannot think of three reasons the operator might be rubber-stamping, you have not thought enough. Possible: they agree, they are fatigued, they do not understand enough to object. The system should distinguish these — and the mechanism is a *probe*. Ask a calibration question: "Does this evolution positioning match what you see in the market?" A fluent operator answers substantively. A non-fluent operator gives a non-answer.

- **Terminology questions** ("what do you mean by 'genesis stage'?") = explicit gap. Direct signal. Record it. Address it. Check it again later.

The operator's knowledge state is not self-reported. It is *observed*. Self-assessment is unreliable — the Dunning-Kruger literature is clear on this. The operator who says "I understand evolution theory" may or may not. The operator who negotiates evolution assessments at high resolution demonstrably does.

*Recommendation:* Model knowledge through observed interaction patterns, not self-assessment. The negotiate loop is the instrument. Read it.

---

### Alistair Cockburn (Crystal Methodology / Hexagonal Architecture)

The actor-goal model provides the structure for learning needs analysis.

The operator has goals at three use-case levels:

- **Summary level**: "Become a competent strategic consulting operator." This is the engagement-spanning goal. The learning needs analysis at this level asks: which methodology concepts does the operator need to master across the full engagement lifecycle?

- **User-goal level**: "Evaluate this evolution assessment correctly." This is the per-gate goal. The learning needs analysis at this level asks: which specific concepts must the operator understand to negotiate *this* proposal effectively?

- **Subfunction level**: "Understand what stage II means." This is the per-concept goal. The learning needs analysis at this level asks: does the operator already know this, or does this concept need delivery?

The pedagogical investment decision happens at the user-goal level. When the system prepares a proposal for operator negotiation, it asks: *which concepts in this proposal are within the operator's demonstrated fluency, and which are not?* The fluent concepts get no pedagogical scaffolding — delivering them wastes wetware credits on work the operator's brain has already done. The non-fluent concepts get targeted delivery, and the *voice* is the delivery adapter selected to match the concept's characteristics and the operator's cognitive style.

This is Crystal tuning applied to a single interaction. Crystal tunes *process weight* to team capability. This tunes *pedagogical weight* to operator fluency. The mechanism is the same: observe capability, calibrate investment, avoid both under-delivery (operator cannot negotiate effectively) and over-delivery (operator's attention is wasted on material they already command).

The cooperative game metaphor extends: the game changes as the operator learns. Early in the engagement, most concepts are unfamiliar — heavy pedagogical investment, frequent voice-assisted explanations. Late in the engagement, the operator is fluent — minimal pedagogy, raw analysis, high-bandwidth negotiation. The system that does not track this progression either over-invests late (patronising) or under-invests early (incomprehensible). Both waste the scarce resource.

*Recommendation:* Learning needs analysis operates at the per-gate level. For each proposal, identify which concepts are within demonstrated fluency and which are not. Invest pedagogical effort only in the gaps.

---

### Ward Cunningham (Technical Debt / CRC Cards)

Background knowledge debt *is* technical debt. I should know.

The original debt metaphor: you ship imperfect code deliberately, knowing you will pay it back. The interest is the additional cost of working around the imperfection in every subsequent interaction. You take on debt when the cost of delay exceeds the interest — when shipping now and paying later is cheaper than getting it right first.

Background knowledge debt works identically. The operator proceeds through an engagement without fully understanding evolution theory. Every subsequent interaction that involves evolution — every map assessment, every strategic annotation, every negotiation about component positioning — costs more because the operator must translate before they can evaluate. That is interest. It compounds across every gate that touches the concept.

The learning needs analysis is a *debt assessment*. It identifies:

1. **Which debts exist.** Which methodology concepts has the operator not yet internalised? Signal: terminology questions, low-resolution negotiation, rubber-stamping on concept-heavy proposals.

2. **Which debts are high-interest.** A concept that appears in every remaining gate costs more than a concept that appears once. Evolution theory debt is high-interest because evolution appears everywhere. A specific pattern like "pipeline components" is lower-interest if pipelines appear in only one project.

3. **Which debts are cheapest to service.** Some concepts are quick to explain and immediately applicable. Others require deep background. The learning needs analysis should prioritise: high-interest debts that are cheap to service. Maximum return on pedagogical investment.

The voices protocol becomes the *debt servicing strategy*. Not blanket repayment — targeted. Service the debts that cost the most, using the delivery mechanism that makes the concept stick fastest. Feynman for concepts that yield to analogy. Garden for concepts that are clearer when their absurdity is acknowledged. Krieger for concepts that are memorable when delivered with inappropriate enthusiasm.

CRC cards for the architecture:

**Evidence Recorder**
- Responsibility: Observe operator interactions, produce typed evidence events, append to log
- Collaborators: Negotiate loop (signal source), Evidence schema (published language)

**Needs Assessor**
- Responsibility: Read evidence log, read knowledge tree, compute current fluency map and recommendations
- Collaborators: Evidence log (event store), Knowledge tree (semantic pack), Assessment strategy (swappable)

**Pedagogical Calibrator**
- Responsibility: Given fluency map and current proposal, determine which concepts need scaffolding and what voice/strategy to use
- Collaborators: Needs Assessor (fluency map), Voice protocol (delivery mechanism), Skill (current proposal)

Three cards. Three concerns. Clean separation. The recorder does not assess. The assessor does not calibrate delivery. The calibrator does not record evidence.

*Recommendation:* Model knowledge debt as a compound-interest problem. Prioritise high-interest, cheap-to-service debts. The learning needs analysis is a debt register.

---

### Kent Beck (Simple Design / XP)

The feedback loop is the mechanism. This is TDD for operator knowledge.

**Red.** The system has a hypothesis about the operator's knowledge state. "The operator does not understand evolution stages." This hypothesis is testable: present material that requires evolution-stage understanding and observe the operator's response.

**Green.** The hypothesis is confirmed — the operator's negotiation is low-resolution on evolution-related proposals. The system addresses the gap: targeted pedagogical delivery using an appropriate voice. The operator's subsequent negotiation improves. The test passes.

**Refactor.** The system updates its model. Evolution stages: fluency level upgraded. But — here is the refactoring step — the system also checks whether the pedagogical delivery was efficient. Did the operator need three exposures or one? Did Feynman-voice work better than raw explanation? This signal refines not just *what* the operator knows but *how they learn*.

The danger is over-modelling. A full cognitive profile with Bloom's taxonomy levels for every methodology concept is a comprehensive testing framework that nobody will maintain. The simplest thing that works:

**Three states per concept: unknown, familiar, fluent.**

- **Unknown**: The operator has not encountered this concept or has shown no evidence of recognition. Full pedagogical delivery with voice support.
- **Familiar**: The operator recognises the concept and can follow reasoning that uses it, but does not generate it independently. Light scaffolding — name the concept, provide brief context, move on.
- **Fluent**: The operator uses the concept accurately in their own reasoning. No scaffolding. Raw analysis.

Three states. Not five. Not a continuous spectrum. Three is enough to make pedagogical targeting useful. Three is few enough that the model can be maintained from interaction signals without dedicated assessment exercises.

How do you detect transitions? The same feedback loop:
- Unknown → Familiar: operator asks about the concept, or responds to scaffolded explanation with substantive engagement.
- Familiar → Fluent: operator uses the concept unprompted in their negotiation.
- Fluent → Familiar (regression): operator misapplies the concept after a long gap. This happens. The model should accommodate it.

*Recommendation:* Three-state model. Unknown, familiar, fluent. Detect transitions from interaction signals. Do not build a testing framework. The engagement *is* the test.

---

### Eric Evans (Domain-Driven Design)

The domain modelling questions:

**Aggregate Root: OperatorProfile**

The operator's knowledge state is an aggregate that accumulates evidence over time. It crosses engagement boundaries — the operator's understanding of evolution theory persists from one engagement to the next. This means it belongs to the *operator*, not the engagement.

```
OperatorProfile
  |-- KnowledgeDomain (e.g., "wardley-mapping")
  |     |-- ConceptFluency ("evolution-stages", fluent)
  |     |-- ConceptFluency ("supply-chain-decomposition", familiar)
  |     +-- ConceptFluency ("strategic-plays", unknown)
  |-- KnowledgeDomain ("business-model-canvas")
  |     |-- ConceptFluency ("customer-segments", fluent)
  |     +-- ConceptFluency ("revenue-streams", familiar)
  +-- LearningPreferences
        |-- PreferredVoice (optional, static preference)
        +-- ObservedPatterns (analogy-responsive, narrative-responsive, etc.)
```

**Value Objects, not Entities.** ConceptFluency is a value object — it has no identity, only a state. You replace it wholesale when the state changes. You do not track its history (that would be over-modelling). The current state is what matters for pedagogical targeting.

**Where does it live?** Not in the engagement workspace — it spans engagements. Not in the project — it spans projects. It belongs to the operator:

```
personal/
  +-- operator-profile.json
```

The bounded context question: the OperatorProfile is consumed by the pedagogical system but maintained by the engagement interaction loop. The engagement observes fluency signals and writes updates. The pedagogical system reads the profile and calibrates delivery. These are separate concerns with a shared data structure — a Published Language pattern. The profile format is the published language.

**Ubiquitous language.** The concepts in the model need names that mean the same thing everywhere:
- "Fluency" not "skill level" (fluency implies use in context, not abstract capability)
- "Knowledge domain" not "topic" (domain implies structured methodology knowledge, not arbitrary subjects)
- "Concept" not "term" (the operator needs to understand the concept, not just recognise the word)

**The Anti-Corruption Layer.** The operator profile should not leak methodology-internal structure. It tracks *concepts the operator encounters*, not *how the methodology decomposes internally*. If the Wardley Mapping skillset restructures its internal phases, the operator profile should not need updating — the concepts the operator knows are stable even if the pipeline changes.

*Recommendation:* OperatorProfile as a cross-engagement aggregate. Value objects for concept fluency. Published Language for the profile format. Store at operator level, not engagement level.

---

### Fred Brooks (Essential vs Accidental Complexity)

The essential complexity of modelling human knowledge is large. Dangerously large. The history of AI is littered with knowledge representation schemes that collapsed under the weight of their own ambition. Expert systems. Ontologies. Skill taxonomies. Each started with a clean model and drowned in edge cases.

The question is not "can we model operator knowledge?" It is "how little modelling can we get away with while still making useful pedagogical decisions?"

Beck's three-state model (unknown, familiar, fluent) is deliberately crude. It throws away enormous amounts of information about the operator's actual cognitive state. And that is exactly right. Because the *decisions* the model informs are also crude: explain this concept (unknown), mention this concept briefly (familiar), skip this concept (fluent). Three decision outcomes require three input states. A more nuanced model would produce more nuanced decisions that the system cannot act on — because the output channel (voice-repackaged explanation) does not have enough bandwidth to express fine-grained pedagogical distinctions.

Match model resolution to decision resolution. If the system can only make three kinds of pedagogical choices, the model only needs three states. If future capabilities enable finer-grained pedagogy (interactive exercises, worked examples, Socratic questioning), the model can be enriched then.

The second essential difficulty: knowledge is not decomposable into independent concepts. Understanding evolution stages requires understanding value chains. Understanding strategic plays requires understanding evolution, inertia, and sourcing. The concept graph has dependencies. A naive model that tracks concepts independently will misidentify gaps — it will think the operator is "fluent" in strategic plays because they use the term correctly, when they are actually parroting without understanding the prerequisites.

The mitigation: the concept graph should encode prerequisite relationships. If evolution-stages is a prerequisite for strategic-plays, then fluency in strategic-plays is only credited when evolution-stages is also fluent. This is minimal dependency modelling — not a full ontology, just "concept A requires concept B." The skillset's own pipeline often encodes these dependencies implicitly: stages come before strategy because you need positioned components before you can annotate them.

*Recommendation:* Minimal model. Three states. Encode prerequisite relationships between concepts. Do not build a knowledge ontology. The pipeline's own sequencing encodes most of what you need.

---

### Anthropic (Skills Engineering / Agent Architecture)

The implementation architecture for operator knowledge modelling:

**Cross-session memory.** The operator knowledge model must persist. The whole point — the compounding return from wetware efficiency — requires that what the system learns about the operator in session N is available in session N+1. This means external artifacts. Consultamatron already uses external artifacts for cross-session memory (decision logs, engagement logs, gate artifacts). The operator profile is another.

**Context loading cost.** The operator profile must be loaded into the context window at the start of each session that involves pedagogical calibration. Cost depends on model size:

- Beck's three-state model: a concept list with three-state flags. For a methodology with 30-50 core concepts, this is perhaps 100-200 tokens compressed to bytecode. Negligible.
- A richer model with prerequisite graphs, learning preferences, and interaction history: potentially 500-1000 tokens. Still manageable, but it competes with other context demands (research summaries, gate artifacts, skill instructions).

The bytecode convention already handles this. Compile the operator profile to a compressed format. Load it alongside the skill's instructions. The agent reads it, calibrates its pedagogical delivery, and updates it at session end.

**Signal extraction.** The practical challenge: extracting fluency signals from the negotiate loop requires the agent to *monitor its own conversation for knowledge indicators*. This is a metacognitive task. The agent must simultaneously:
1. Conduct the negotiation (its primary task)
2. Observe the operator's responses for fluency signals (a secondary task)
3. Update the knowledge model (a bookkeeping task)

This is feasible but requires explicit instruction in the skill's prompt. Skills that involve the propose-negotiate-agree loop should include guidance: "During negotiation, observe whether the operator's feedback demonstrates familiarity with [concepts in this proposal]. Update the operator profile at session end."

**The Evaluator-Optimizer pattern.** The pedagogical calibration is an instance of this pattern. The evaluator assesses the operator's knowledge state (from the profile and from current-session signals). The optimizer selects the pedagogical strategy (which concepts to explain, which to skip, which voice to use). This is a clean separation that can be implemented as two prompt segments within a single skill execution.

**Freedom levels for knowledge modelling.** The operator profile is a *suggestion*, not a constraint. The agent should use it to calibrate defaults but remain responsive to in-session signals. If the profile says "evolution-stages: fluent" but the operator asks "what does stage II mean?" in this session, the in-session signal overrides the profile. The profile is a prior; the conversation is the evidence.

*Recommendation:* Operator profile as a lightweight external artifact. Bytecode-compressed for context loading. Updated at session end. Profile is a prior, not a constraint — in-session signals always override.

---

### Synthesis

**Consensus:**

All seven perspectives agree on the core principle: *pedagogical investment should be targeted, not blanket*. The system should not explain what the operator already knows (wastes wetware credits, risks patronising) and must not skip what the operator does not know (creates rubber-stamp gates, accumulates knowledge debt).

All agree the negotiate loop is the primary signal source. The operator's negotiation behaviour reveals their knowledge state more reliably than self-assessment. High-resolution feedback = fluency. Low-resolution feedback = gap. The signal is already being generated; the system just needs to read it.

All agree the model should be minimal. Beck's three-state model (unknown, familiar, fluent) received no objections. It matches the resolution of the decisions it informs. Richer modelling can come later if richer decisions become possible.

All agree the operator profile must persist across sessions to support compounding returns. The location is at operator level, not engagement level, because the operator's knowledge spans engagements.

**Divergence:**

**Concept dependencies.** Brooks argues for explicit prerequisite encoding (strategic-plays requires evolution-stages). Cunningham's debt model implies the same through "collaborators." Beck resists: three states is simple; adding a dependency graph adds complexity. The resolution: the skillset pipeline already encodes concept sequencing. Use it as an implicit prerequisite graph rather than building an explicit one. If the pipeline teaches evolution before strategy, and the operator is fluent in both by the time they reach strategy, the prerequisites were satisfied by the pipeline's natural order.

**Active probing vs passive observation.** Weinberg advocates calibration probes — asking the operator questions to distinguish rubber-stamping from genuine agreement. Beck prefers passive observation — the three-state model updates from whatever signals the conversation naturally produces. The resolution: probes are legitimate but should feel like engagement, not examination. "Does this evolution positioning match what you see in the market?" is a negotiation prompt that also calibrates fluency. Design probes that serve both purposes.

**Operator agency.** Evans models the profile as a system-maintained artifact. Weinberg implies the operator should be aware of and able to correct it. Anthropic notes the profile is a prior, not a constraint. The resolution: the profile should be transparent. The operator should be able to see their knowledge profile, correct misassessments ("I actually do understand supply chains, I was just tired"), and express learning goals ("I want to understand inertia better"). This is the propose-negotiate-agree loop applied to the operator's own development.

**Voice selection mechanism.** With a knowledge model, voice selection becomes a function of `(concept_gap x content_type x operator_preference)`, not just operator preference alone. An operator who is fluent in evolution but unfamiliar with inertia might receive raw analysis for evolution sections and Feynman-voice explanation for inertia sections *within the same proposal*. This is per-concept voice targeting, not per-artifact voice selection. The first deliberation's "static preference" recommendation is upgraded: preference sets the default voice, but the knowledge model can override it per-concept when a gap is detected.

**Recommendation:**

The learning needs analysis adds three components to the voices protocol design:

1. **Operator Profile.** A lightweight cross-engagement artifact tracking concept fluency (unknown/familiar/fluent) across knowledge domains. Stored at operator level. Bytecode-compressed for context loading. Transparent and operator-correctable.

2. **Fluency Signal Extraction.** Skills that run the negotiate loop observe the operator's responses for fluency indicators. Not a separate assessment — a secondary read on interactions that are already happening. Updated at session end.

3. **Calibrated Pedagogical Targeting.** For each proposal, the system identifies which concepts are within the operator's demonstrated fluency (skip or mention briefly) and which are not (deliver with appropriate voice and scaffolding). Voices are applied to *gaps*, not blanket. This is the connection between the knowledge model and the voices protocol: the model identifies *where* to invest wetware credits; the voice determines *how*.

The two-phase approach from the first deliberation is amended:

1. **Phase one** (prompt pattern) now includes: "explain [specific concept] like Feynman, the rest I already know." The operator manually identifies their gaps and requests targeted delivery. No infrastructure. Tests whether targeted voice pedagogy is more effective than blanket delivery.

2. **Phase two** (protocol) now includes: the operator profile, fluency signal extraction, and automated targeting. The system identifies gaps and applies voices without the operator having to specify "I don't understand this part." The system already knows, from the profile and from current-session signals.

The trigger for phase two is unchanged: when manual gap-identification becomes tedious and the operator wishes the system would just *know*.

---

## Deliberation: Evidence-of-understanding architecture and learning needs assessment

**Subject**: platform — operator knowledge model, evidence architecture
**Council**: Weinberg, Feathers, Evans, Cunningham, Beck, Parnas, Anthropic
**Knowledge domain**: SWE (platform infrastructure)

---

### Gerald Weinberg (Psychology of Programming / Secrets of Consulting)

The append-only evidence log is the right structure because it respects something most knowledge-modelling systems get wrong: understanding is not a state you arrive at. It is a signal that fluctuates. The operator who demonstrated fluent use of evolution theory in January may have gone rusty by July. The operator who stumbled over supply chain decomposition last week may have gone home and read about it. You need the history, not just the current snapshot, because the history tells you things the snapshot cannot.

Now, the tricks. The user is right that this is a bag of tricks, not a formal methodology, and the bag will grow with experience. Here are the ones I can see:

**Jargon fluency is weak evidence.** People absorb vocabulary before they absorb meaning. An operator who says "this component has high inertia" may understand inertia deeply or may be parroting the system's own output. The jargon tells you the concept is not *unknown*. It does not tell you it is *fluent*. The appropriate response: acknowledge the terminology (do not re-explain it) but probe the application. "You mentioned inertia — what do you think is causing it here?" A fluent operator names specific organisational or technical factors. A parrot gives a generic answer.

**Unprompted application is strong evidence.** When the operator, without being asked, says "this feels like a pipeline situation — there are clearly different variants at different evolution stages" — that is strong evidence of fluency in both pipelines and evolution. They are generating analytical structure from the methodology independently. Record this. It is gold.

**Confident incorrectness is dangerous evidence.** The operator who says "this is genesis because we built it ourselves" has confused evolution stage with sourcing decision. They are confident. They are wrong. The evidence log should record *both* signals: confidence (the operator believes they understand) and incorrectness (they do not). This is the Dunning-Kruger case. It requires more delicate pedagogical intervention than simple unfamiliarity — you must correct without undermining the operator's willingness to engage.

**Probe design matters.** A probe that feels like an exam damages the cooperative relationship. A probe that feels like engagement strengthens it. "What do you think is causing the inertia?" is engagement. "Can you define inertia?" is examination. The first invites the operator to contribute their domain knowledge through the methodology's lens. The second tests recall. The first produces better evidence *and* better engagement. The evidence-gathering tricks should bias heavily toward probes that feel like collaboration.

**Fatigue confounds the signal.** A rubber-stamp late in a long session is more likely fatigue than incomprehension. The evidence log should record contextual factors — how far into the session, how many decisions already made — so that assessment can weight accordingly. A rubber-stamp at minute 15 is more informative than a rubber-stamp at hour 3.

*Recommendation:* The tricks are a practitioner knowledge base. They will grow. Structure the evidence log to accommodate evidence types that do not yet exist. The append-only model supports this naturally — new evidence types are new event types, old events remain valid.

---

### Michael Feathers (Working Effectively with Legacy Code / Seams)

The evidence-of-understanding log is a *characterisation test suite for the operator's knowledge*.

In legacy code, you do not know what the code does until you characterise it. You run it, record the output, and that becomes your baseline. You do not assert what the output *should* be. You assert what it *is*. Then, when you change the code, you run the tests again to see if the characterisation still holds.

The evidence log works identically. You do not assert what the operator *should* understand. You record what they *demonstrate*. Each evidence entry is a characterisation: "At this point in time, in this context, the operator demonstrated this level of understanding of this concept." The assessment is a projection of characterisations through the knowledge tree — exactly as a characterisation test suite tells you what the code currently does, not what it should do.

The **seams** concept is directly applicable. In legacy code, a seam is a point where you can alter behaviour without editing the source. In the engagement, a seam is a point where you can observe understanding without disrupting the flow. The negotiate loop is a natural seam — the operator is already responding to proposals. Adding an observation layer at this seam is non-invasive.

But there are other seams:

- **Gate review.** When the operator reviews a gate artifact, their comments reveal their understanding of the methodology that produced it. "This supply chain looks right" is low evidence. "I would split this component into a pipeline because the SaaS version and the on-prem version are at different evolution stages" is high evidence.

- **Cross-session return.** When the operator returns after a gap and reviews previous artifacts, their ability to pick up where they left off reveals retention. If they need to re-read the analysis to understand the gate artifact they previously agreed, that is evidence of regression. The evidence log should capture re-engagement quality.

- **Teaching others.** If the operator explains the engagement's findings to stakeholders (the actuator role), the quality of their explanation is evidence. The system rarely observes this directly, but the operator's debrief comments can provide proxy evidence. "The board understood the evolution argument" vs "I had to simplify a lot" tells you something.

The separation of recording from assessment is critical, and it is the same separation that makes characterisation tests valuable. The tests do not interpret. They record. Interpretation is a separate activity with a separate concern. If you conflate recording with assessment, you lose the ability to re-assess with better strategies later. The append-only log preserves the raw signal. Assessment strategies can improve without discarding evidence.

*Recommendation:* Think of each evidence entry as a characterisation test. It records what was observed, not what was expected. The assessment is a separate pass that interprets the characterisations through the knowledge tree. Re-assessment with better strategies is always possible because the raw evidence is preserved.

---

### Eric Evans (Domain-Driven Design)

This is event sourcing. Let me model it.

**The Event Store: `personal/evidence-of-understanding/{skillset}/{topic}/`**

Each file in the append-only log is a domain event. The event types form a type hierarchy, but following the knowledge protocols principle, we should not over-formalise this. Evidence types that exist today:

```
EvidenceEvent
  |-- timestamp
  |-- session_context (engagement, project, skill, duration_into_session)
  |-- concept_reference (node in the knowledge tree)
  |-- evidence_type
  |     |-- jargon_use (operator used the term; weak positive)
  |     |-- contextual_application (operator applied concept to specific situation; strong positive)
  |     |-- novel_insight (operator generated new analysis using concept; very strong positive)
  |     |-- prompted_recall (operator answered probe correctly; moderate positive)
  |     |-- incorrect_application (operator used concept wrongly; negative, records confidence level)
  |     |-- terminology_question (operator asked what a term means; confirms unknown)
  |     |-- rubber_stamp (operator accepted without engagement; ambiguous, contextual factors needed)
  |     +-- regression_signal (operator needed re-explanation of previously demonstrated concept)
  +-- raw_observation (free text: what actually happened)
```

New evidence types will emerge as tricks are learned. The append-only model accommodates this — new event types do not invalidate old events.

**The Projection: learning needs assessment**

The assessment is a *read model* derived from the event store. It is computed, not stored. This is CQRS: the write side (evidence recording) and the read side (needs assessment) are separate models with separate concerns.

The read model's inputs:
1. The skillset's knowledge tree (the semantic pack structure — concepts and their relationships)
2. The evidence log (all recorded observations)
3. The assessment strategy (the current set of tricks for interpreting evidence)

The read model's output:
```
LearningNeedsAssessment
  |-- concept_fluency_map ({concept} -> unknown | familiar | fluent)
  |-- high_interest_gaps (concepts that appear frequently in upcoming work)
  |-- regression_risks (concepts with old evidence and no recent confirmation)
  +-- recommended_focus (prioritised list for next session's pedagogical investment)
```

**Why event sourcing matters here.** Because the assessment strategy will improve. The first version might simply take the most recent evidence per concept. A later version might weight by recency, account for fatigue, apply spaced repetition scheduling, or detect the Dunning-Kruger pattern (high confidence + incorrect application). Each new strategy re-reads the same event store and produces a better assessment. The raw evidence is never lost.

**The Aggregate boundary.** Evidence events for a concept are independent of evidence events for other concepts (mostly — prerequisite relationships create some coupling). The natural aggregate boundary is per-concept-per-skillset. But storage as append-only files in `{skillset}/{topic}/` is fine because the assessment process reads across concepts anyway. The file system is the event store; the assessment is a projection computed at read time.

**Published Language.** The evidence event schema is the published language between the recording process (skills, during negotiation) and the assessment process (pedagogical calibration, before delivery). Both sides must agree on what an evidence event contains. The schema should be documented and versioned.

*Recommendation:* Event sourcing with CQRS. Append-only evidence log as the write model. Learning needs assessment as a computed read model. Assessment strategies are swappable and improvable because raw evidence is preserved.

---

### Ward Cunningham (Technical Debt / CRC Cards)

The append-only evidence log is a *debt ledger*.

Each evidence entry is a transaction. Some are credits: demonstrated understanding reduces the debt balance for that concept. Some are debits: demonstrated gaps or regressions increase it. The current balance per concept determines the outstanding debt. The assessment is a balance sheet.

But here is what makes the temporal dimension powerful: debt has a *forgetting curve*. A credit from six months ago is worth less than a credit from last week. Not because the operator never understood it, but because understanding without reinforcement decays. The spaced repetition insight the user raises is exactly right — it is an interest rate on knowledge credits. Credits depreciate unless refreshed.

The debt servicing schedule (when and how to reinforce learning) follows spaced repetition research:

1. **First exposure**: New concept, unknown state. Full pedagogical investment. Voice-assisted explanation.
2. **First recall**: Soon after (next session, or later in same session). Light probe. "You mentioned inertia last time — how does it apply here?" If the operator engages substantively, the credit holds. If they falter, reinforce.
3. **Expanding intervals**: Each successful recall extends the interval to the next probe. Day 1 -> Day 3 -> Day 7 -> Day 21 -> Day 60. The evidence log timestamps make this computable.
4. **Regression response**: If a probe reveals regression, the interval resets. Not to zero — the operator learned it once, so re-learning is faster — but the spaced repetition schedule restarts from a shorter interval.

The append-only log enables all of this because it preserves timestamps. A snapshot ("evolution-stages: fluent") discards the temporal information that spaced repetition needs. The log retains: *when* fluency was demonstrated, *how often* it has been confirmed, *how long* since the last confirmation. The assessment projection computes the effective balance accounting for temporal decay.

*Recommendation:* The temporal dimension is the key feature of the append-only log. It enables spaced repetition, regression detection, and evidence depreciation. A snapshot model cannot do this. The log must preserve timestamps.

---

### Kent Beck (Simple Design / XP)

The separation of recording from assessment is elegant because it follows a pattern I trust: *collect data, then interpret it*. In TDD terms: run the tests first, then analyse failures. Do not skip the data collection step and go straight to diagnosis.

But I want to apply the simplicity lens to the evidence recording process itself. The user says "there are probably a bunch of tricks we need to learn." Agreed. And that means the recording process will change as we learn new tricks. The append-only log accommodates this — new evidence types are new event types. Good.

The risk is *over-recording*. If the system tries to extract evidence from every utterance in every interaction, the log grows large, the signal-to-noise ratio drops, and the assessment process spends its budget parsing noise. The simplest approach:

**Record deliberate observations, not ambient signal.**

Each evidence entry should be a conscious act by the recording process: "I observed something that tells me something about this operator's understanding of this concept." Not: "here is a transcript of everything the operator said, from which evidence might later be extracted."

The deliberate observation model keeps the log lean and interpretable. Each entry has a clear concept reference, a clear evidence type, and a clear observation. The assessment process reads structured entries, not raw transcripts.

For the per-node model ("for each node in the semantic pack, the voice should strive to elicit evidence at or better than current evidence"):

This creates a clear objective for the voice's pedagogical role. The voice is not just explaining — it is *advancing evidence*. If current evidence for concept X is "unknown," the voice's job is to deliver concept X in a way that creates an opportunity for the operator to demonstrate "familiar." If current evidence is "familiar," the voice creates an opportunity to demonstrate "fluent."

This is red-green-refactor applied to operator knowledge:
- **Red**: Evidence shows a gap (or no evidence exists)
- **Green**: Voice delivers the concept, operator demonstrates understanding, evidence is recorded
- **Refactor**: Assessment updates, pedagogical strategy adjusts for next encounter

The feedback loop is tight: evidence -> assessment -> calibrated delivery -> new evidence. Each cycle advances the operator's demonstrated understanding. The loop runs within the normal engagement workflow — no separate "learning sessions" required.

*Recommendation:* Record deliberate observations, not ambient signal. The voice's explicit objective is evidence advancement: move each concept from current evidence level to the next.

---

### David Parnas (Information Hiding / Module Decomposition)

The user's design decision — separate recording from assessment — is correct, and the criterion is information hiding.

The recording module and the assessment module change for different reasons:

**Recording changes when new evidence-gathering tricks are discovered.** A new way to probe understanding, a new seam to observe, a new evidence type. These changes affect what goes into the log. They do not affect how the log is interpreted.

**Assessment changes when interpretive strategies improve.** A better weighting scheme, spaced repetition integration, Dunning-Kruger detection. These changes affect how the log is read. They do not affect what was recorded.

Changes in one should not propagate to the other. This is the original criterion for modular decomposition: modules should encapsulate decisions likely to change. The decision "how to gather evidence" is likely to change (the tricks bag grows). The decision "how to interpret evidence" is independently likely to change (assessment strategies improve). Therefore: separate modules.

The interface between them is the evidence event schema. This is the stable contract. Both modules depend on it. It should change slowly and additively (new event types, never removing existing ones — the append-only principle extends to the schema itself).

**The assessment module's internal secret**: how it weights evidence types, how it handles temporal decay, how it resolves conflicting signals. The recording module does not know and should not know. This means the recording module should record *observations*, not *conclusions*. "The operator used the term 'inertia' correctly in context" is an observation. "The operator is familiar with inertia" is a conclusion. The recording module produces the former. The assessment module produces the latter.

**The recording module's internal secret**: which seams it monitors, which probes it deploys, how it decides when to record. The assessment module does not know and should not know. This means the assessment module should treat all evidence events as equally structured input, regardless of how they were gathered. A jargon-use observation from a negotiation seam and a prompted-recall observation from a deliberate probe have the same schema. The assessment module may *weight* them differently, but that weighting is the assessment module's secret, not encoded in the recording.

The `personal/evidence-of-understanding/{skillset}/{topic}/*` path structure encodes a design decision worth examining: evidence is organized by skillset and topic. This means the recording module must classify each observation by skillset and topic at write time. This is reasonable — the recording process knows which skill is executing and which concepts are in play. But it means the recording module depends on the knowledge tree's structure (it must know which concepts belong to which skillset/topic). This is an acceptable coupling because the knowledge tree changes slowly and the recording module's concept references must be meaningful.

*Recommendation:* The interface between recording and assessment is the evidence event schema. Recording produces observations. Assessment produces conclusions. Neither module knows the other's internal strategy. The schema is the stable contract.

---

### Anthropic (Skills Engineering / Agent Architecture)

The implementation architecture, with the user's design decisions integrated:

**Storage: `personal/evidence-of-understanding/{skillset}/{topic}/*`**

Append-only files. Each file is a session's evidence observations for a skillset/topic combination. Filename encodes the timestamp: `2026-02-18T14-30.md` or similar. The content is structured evidence events in a human-readable format (not JSON — the operator should be able to read their own evidence log, per the transparency principle from the previous deliberation).

File format suggestion:
```markdown
---
session: 2026-02-18
engagement: acme/wardley-mapping
skill: wm-evolve
---

## evolution-stages

- [contextual_application] Operator identified component X as custom-built
  based on market analysis, noting three competitors but low ubiquity.
  Reasoning was sound.

## inertia

- [jargon_use] Operator mentioned "inertia" when discussing component Y.
  No elaboration on causes. Probe warranted next encounter.

## supply-chain-decomposition

- [terminology_question] Operator asked what "submap" means in the
  context of the supply chain. Explained with example from current map.
```

Human-readable. Append-only. Structured enough for machine parsing. The operator can review their own evidence trail.

**Context loading for assessment**

The full evidence log is too large to load into context. The assessment is a projection — computed on demand and compressed for context loading. The skill's prompt receives:

```
Operator fluency profile (wardley-mapping):
- evolution-stages: fluent (last confirmed 2026-02-15, 4 confirmations)
- supply-chain-decomposition: familiar (last confirmed 2026-02-10, 1 confirmation)
- inertia: unknown (jargon use only, no confirmed understanding)
- strategic-plays: unknown (no evidence)
```

This compressed projection is what enters the context window. Perhaps 50-100 tokens per skillset. The full evidence log stays on disk for re-assessment.

**Evidence recording in practice**

Skills that run the negotiate loop need explicit instruction to record evidence. This is a prompt engineering concern. The skill's methodology guide should include:

> During negotiation, observe the operator's responses for evidence of
> understanding. At session end, append observations to the evidence log
> at `personal/evidence-of-understanding/{skillset}/{topic}/`. Record
> observations, not conclusions. Note the concept, evidence type, and
> what was observed.

This is a secondary task. The primary task is the negotiation. Evidence recording should not dominate the agent's attention. The instruction should be brief and the recording format should be fast to produce.

**Spaced repetition scheduling**

The assessment projection can include a "next review due" timestamp per concept, computed from the evidence log's temporal pattern. When loading the fluency profile, the agent sees which concepts are due for reinforcement:

```
- evolution-stages: fluent (next review: 2026-03-15)
- supply-chain-decomposition: familiar (next review: 2026-02-20 -- DUE)
```

This enables the agent to weave reinforcement probes into normal engagement work. Not a separate exercise — a prompt-engineered nudge within the negotiate loop.

**The tricks knowledge base**

The user notes "there are probably a bunch of tricks we need to learn." This is a *design-time* semantic pack — a knowledge base that grows as the practice accumulates experience with evidence gathering. It belongs in:

```
commons/{practice}/docs/evidence-tricks.md
```

Or as a proper semantic pack with individual trick entries. Each trick documents: what to observe, what it indicates, confidence level, known failure modes. The evidence recording instructions in skills reference this pack. As new tricks are discovered (through practice reviews, operator feedback, or deliberate experimentation), they are added to the pack and the recording instructions are updated.

*Recommendation:* Human-readable evidence files. Compressed assessment projection for context loading. Explicit recording instructions in skill prompts. A growing tricks knowledge base as a design-time semantic pack.

---

### Synthesis

**Consensus:**

The council unanimously endorses the architecture: append-only evidence log, separated from assessment, with the knowledge tree as the assessment scaffold. The key agreements:

**Append-only is non-negotiable.** Every member identified temporal preservation as essential. Cunningham needs timestamps for spaced repetition. Feathers needs the full history for characterisation. Evans needs the event store for replayable assessment. Parnas needs the separation to support independent evolution of recording and assessment strategies. There is no dissent on this point.

**Record observations, not conclusions.** Parnas's information-hiding argument is definitive. The recording module captures what happened. The assessment module interprets what it means. Conclusions in the evidence log would embed the assessment strategy of the moment into permanent storage, preventing re-assessment with better strategies later.

**Evidence types will grow.** Weinberg's tricks bag, Feathers's seams, Beck's deliberate observations — all point to an expanding vocabulary of evidence types. The schema must be additive. New types never invalidate old entries. This is a natural property of append-only logs.

**The voice's objective is evidence advancement.** Beck's formulation: for each concept, the voice should aim to advance from current evidence level to the next. Unknown -> familiar -> fluent. This gives the voice a measurable objective beyond "explain well." It explains *in a way that creates opportunity for the operator to demonstrate understanding*.

**Divergence:**

**Probe intrusiveness.** Weinberg warns that probes that feel like examinations damage the cooperative relationship. Beck wants deliberate evidence-gathering moments. The resolution: probes should be embedded in the engagement's natural flow. "What do you think is driving the inertia here?" is simultaneously a negotiation prompt (inviting the operator's domain knowledge), a pedagogical instrument (creating an opportunity to apply the concept), and an evidence-gathering probe (the response reveals fluency). Triple-duty prompts are the design target. Dedicated examination is the failure mode.

**Evidence granularity.** Evans models fine-grained evidence types (eight types in the proposed schema). Beck prefers fewer, coarser observations. The resolution: start coarse, refine with experience. The append-only model means early coarse observations remain valid even as later observations use finer types. The schema grows; old entries are not invalidated.

**Assessment complexity.** Cunningham's spaced repetition scheduling and Evans's full CQRS projection are sophisticated. Beck's three-state model is crude. The resolution is in the architecture itself: because recording and assessment are separated, assessment strategies can evolve independently. Start with Beck's three-state projection. Introduce temporal weighting when evidence accumulates across enough sessions. Add spaced repetition when the practice has enough experience to calibrate intervals. The evidence log supports all of these; the assessment strategy is swappable.

**Recommendation:**

The evidence-of-understanding architecture has five components:

1. **Evidence Log** (`personal/evidence-of-understanding/{skillset}/{topic}/*`). Append-only. Human-readable. Structured observations with timestamps, session context, concept references, and evidence types. The operator can read and correct.

2. **Knowledge Tree** (the skillset's semantic pack structure). Provides the topology — which concepts exist, how they relate, what prerequisites they have. The assessment maps evidence against this tree.

3. **Assessment Projection** (computed, not stored). Reads the evidence log through the knowledge tree. Produces a fluency map (concept -> unknown/familiar/fluent), identifies gaps, calculates regression risk, recommends focus areas. Loaded into context as a compressed operator profile. Swappable assessment strategies as the tricks knowledge base grows.

4. **Evidence Recording Instructions** (embedded in skill prompts). Skills that run the negotiate loop include guidance on what to observe and how to record it. Recording is a secondary task — it should not dominate the agent's attention. Triple-duty prompts (negotiation + pedagogy + evidence gathering) are the design target.

5. **Tricks Knowledge Base** (design-time semantic pack). Documents evidence-gathering and evidence-interpretation heuristics. Grows with practice experience. Informs both the recording instructions (what to observe) and the assessment strategy (how to interpret).

The voices protocol from the first deliberation is now calibrated by this architecture. Voice selection becomes: `f(concept_gap, evidence_level, operator_preference) -> voice + strategy`. For fluent concepts: no voice, raw analysis. For familiar concepts: light touch, confirm and advance. For unknown concepts: full voice-assisted delivery targeting evidence advancement.

### Council sources

| Source | Type | Location |
|---|---|---|
| Wetware Efficiency | Article | `docs/wetware-efficiency.md` |
| Voices Protocol (first deliberation) | Article | `docs/voices-protocol/deliberation.md` |
| Knowledge Protocols | Article | `docs/knowledge-protocols.md` |
| Semantic Packs | Article | `docs/semantic-packs.md` |
| Principles Glossary | Reference | `docs/principles-glossary.md` |
| SWE Pantheon | Semantic Pack | `personal/swe/docs/pantheon.md` |

---

## Operator negotiation

The council proposed. The operator corrects.

---

### Voices are strategies, not adapters

The first deliberation (voices-protocol.md) framed voices as output adapters.
Cockburn's hexagonal architecture analysis was structurally correct but
terminologically misleading. An adapter is passive — it reformats output. A
voice is a *strategy* — it selects a pedagogic approach calibrated to the
operator's learning need for a specific concept at a specific moment.

This is a strategy selector pattern, the same pattern used for research
strategy selection. The system evaluates the situation (concept gap, evidence
level, knowledge tree depth, operator preference) and selects a pedagogic
strategy. A voice is one dimension of that strategy. Other dimensions include:
probe design, scaffolding depth, explanation directness, and rehearsal
structure.

Preferences change slowly. Needs change quickly. The strategy selector must
respond to needs, not just preferences.

---

### Multiple feedback loops, not just negotiation

The council identified the negotiate loop as the primary signal source. This
is correct but incomplete. The negotiate loop is the *fastest* feedback loop
(OODA within a skill execution), and it is always present, so it should not
be neglected. But it is not the only signal source and possibly not the best.

**The inner loop (negotiation).** Within a skill execution, each
propose-negotiate-agree cycle produces evidence. This is the hot loop. It
runs at every gate point, sometimes multiple times per gate.

**The skillset loop.** A skillset execution spans multiple skills and gates.
The skillset owns its concept tree. Some but not all of those concepts will
be relevant to the artifacts produced by this invocation. The operator's
fluency across those concepts determines whether the dyad can do this work
together competently, or whether the operator needs just-in-time teaching
before they can negotiate effectively.

**The engagement loop.** The engagement spans multiple skillset invocations
and produces a corpus of artifacts. The corpus encapsulates the intersection
of client-commissioned research and skillset knowledge. A trusted advisor to
that client needs relatively good understanding of that corpus. The
engagement loop asks: can the operator competently represent the deliverables?

**The outer loop (preparation and rehearsal).** Beyond the engagement's
analytical work, there are preparation activities:

- *Meeting preparation.* Before the operator presents deliverables to
  stakeholders, the system can assess whether the operator can explain the
  material. This involves learning needs analysis, knowledge gap assessment,
  and micro-curriculum development.

- *Rehearsal.* The operator explains things in their own words. The system
  assesses the explanation, probes understanding where it appears weak,
  provides targeted teaching, then changes topic — and later returns with a
  related question to see if understanding improved. The assessment doubles
  as preparation.

- *Micro-curriculum.* Given a skillset knowledge tree of 100 concepts
  (nested 4 layers deep), an artifact concept profile covering 30% of that
  tree, and an operator whose capability covers 50% of the artifact profile:
  15 concepts fluent, 10 familiar, 5 unfamiliar. The micro-curriculum
  addresses the gap: bring 5 unfamiliar to fluency, bring 10 familiar to
  fluency. Then a pedagogic loop where concepts are explained, the operator
  is asked to apply them, new evidence accumulates, the assessment updates,
  and the lesson iterates.

These are examples of pedagogic strategies where rehearsal, refinement,
assessment, and instruction are interwoven. Generic pedagogic strategies
apply across all skillsets. Skillsets may extend them with specific
variations (Open/Closed Principle).

Additionally, the operator may have *stated learning goals* — not gaps
identified on an assignment, but expressed interest. "I want to understand
inertia better." These summary-level goals optimise the *direction* of
learning, distinct from per-gate goals that optimise the *rate* of learning.

---

### Knowledge trees: skillset concepts and operator evidence

The council's domain model was under-specified. Two trees, not one.

**The skillset concept tree.** Every skillset should have a `docs/` directory
that is a knowledge pack. An arbitrary-depth tree of
`{concept}/{sub-concept}/{arbitrary-depth}/{concept}.md` knowledge items,
where the top-level concept is a "knowable thing" composed of concept nodes
all the way down to concept leaves. This IS the semantic bytecode tree of
the knowledge pack. The concept tree is the skillset's published knowledge
structure.

**The operator evidence tree.** Mirrors the concept tree:

```
personal/knowledge-evidence/{skillset-source}/{skillset}/{concept}/.../{concept}/{datestamp}.md
```

This is also a mutable knowledge pack with bytecode/prose duality, efficient
re-processing with timestamp tricks, and progressive compression:

- `{concept}/{datestamp}.md` (raw evidence entries)
- `{concept}/{year-month}/index.md` (monthly compression)
- `{concept}/{year}/{month}/index.md` (eventual repack)

The assessment process reads forward through time — Schlemiel the Painter,
but the painter has good reason: each pass can use a better assessment
strategy than the last, and the progressive compression means the early
history is already summarised.

**The knowledge tree has depth.** An operator may be fluent in top-level
concepts, familiar with all mid-level concepts, and familiar with only some
leaf nodes. Learning needs analysis compares fluency/familiarity across the
knowledge tree with the requirements of a circumstance. This comparison is
context-dependent:

- If the operator has depth in the skillset, familiarity with the client
  domain may be sufficient.
- If the operator has deep fluency in the client domain, breadth across
  skillsets may be sufficient.
- The engagement might be broad (many skillsets) or deep (single skillset),
  and the ideal operator competency profile varies with engagement.

---

### Four fluency states, not three

Beck's three-state model (unknown, familiar, fluent) is too coarse. The
"familiar" state conflates two importantly different conditions:

- **Unknown.** The operator has not encountered this concept. Explain
  directly. Full pedagogic delivery.

- **Familiar/overconfident.** The operator uses the concept but applies it
  incorrectly. Confident incorrectness (the Dunning-Kruger case). Explain
  *indirectly* — direct correction risks defensiveness; indirect approaches
  (worked examples, probe questions that surface the contradiction) are more
  effective.

- **Familiar/knowingly ignorant.** The operator recognises the concept and
  knows they do not fully command it. Use jargon, but explain it simply the
  first time. Tone: "reminder," not "explainer." The operator does not need
  the concept introduced; they need it reinforced.

- **Fluent.** The operator uses the concept accurately and independently.
  Use jargon token-efficiently. No scaffolding.

The distinction between overconfident-familiar and knowingly-ignorant-familiar
matters because the pedagogic strategy differs. Overconfidence requires
indirection. Known ignorance permits directness. The evidence log must
capture confidence level alongside correctness to distinguish them.

---

### Differential debt consequences

Cunningham's debt framing is correct but under-differentiated. There is more
than one kind of debt, and they have different consequences:

**Skillset utilisation debt.** The cost is paid in artifact quality. The dyad
pays: the operator rubber-stamps, the analysis is weaker, the gate artifact
is less grounded. But the debt is serviceable — skillsets can iterate within
reasonable time, token, and effort constraints. Failure may be affordable.

**Engagement finishing debt.** The cost is paid in client satisfaction,
reputation, and relationships. The operator pays, the dyad suffers. The
operator who cannot competently represent the deliverables damages the
client relationship. We may only get one shot at an engagement. Failure may
be catastrophic.

High-interest debt is not a problem if the debt is written off. Skillset
debts are often written off through iteration. Engagement debts are more
consequential — they cannot be iterated away after the deliverable is
presented.

This differential means pedagogic investment should weight engagement
finishing debts more heavily than skillset utilisation debts. The
micro-curriculum for meeting preparation is higher priority than incremental
fluency improvement during skillset execution.

---

### Teaching strategies: breadth-first vs depth-first

Where there is a large learning need, prioritisation strategy matters:

- **Salience-first.** Fluency in the most salient concepts is highest
  priority, lest the operator appear a fool in front of stakeholders.

- **Eliminate top-level unfamiliarity.** Familiarity at higher levels of the
  knowledge tree may be higher priority than depth at lower levels. An
  operator who is broadly familiar but nowhere deeply fluent can navigate.
  An operator with deep gaps at the top level cannot.

- **Lower-level, less salient concepts** are proportionately lower priority.

The knowledge tree's structure matters for teaching strategy. Some concepts
(deep in the tree) are harder to grasp without the concepts above them to
provide context. Breadth-first teaching strategies may work better for
theoretical knowledge (e.g. learning the conceptual framework of evolution
theory before diving into specific evolution characteristics). Depth-first
teaching (fluency in a single leaf) may work fine for procedural knowledge
(e.g. learning how to draw a supply chain map).

The choice of breadth-first vs depth-first is itself a strategy selection,
driven by the knowledge tree's structure and the nature of the concepts.

---

### Multiple tests, not just the negotiate loop

Beck's TDD framing identified one feedback loop. The operator identifies
many:

- Composing the brief for the engagement
- Commissioning and evaluating the research
- Composing the skillsets
- Commissioning the skillset
- Evaluating the artifacts
- Polishing the deliverables
- Preparing to deliver

Each of these is a test point — an opportunity to observe the operator's
understanding and gather evidence. The negotiate loop within a skill is the
finest-grained test. The engagement lifecycle provides coarser-grained tests
at higher levels of the knowledge tree. All of them should contribute
evidence.

---

### Concept identity vs tree position

Evans identified the anti-corruption challenge: knowledge trees are mutable.
When the knowledge tree changes (nodes added, nodes change parent, nodes
restructured), the operator's evidence tree has corrupted structure. Evidence
recorded against a concept at path `A/B/C` becomes orphaned when the concept
moves to `A/D/C`.

Burning LLM tokens to re-map creates friction for change — friction for
improving a knowledge pack, which is a bad kind of friction. It is also an
economic externality: knowledge pack maintainers change the tree, but
skillset users all pay (in parallel) by maintaining the currency of their
evidence.

The pattern: **decouple position from identity.** A location-independent
concept identifier within the skillset namespace. Map evidence to concept
*name*, not concept *address*. If the concept "evolution-stages" moves from
`core/evolution/stages.md` to `theory/evolution/stages.md`, the evidence
remains mapped to the concept identifier "evolution-stages" regardless of
its current tree position.

This is a bitrot prevention pattern. The concept tree's structure organises
knowledge for comprehension. The concept identifier links evidence to
knowledge regardless of organisation.

---

### Context loading: semantic index with early termination

The council assumed the full evidence tree must be traversed for assessment.
The operator's correction: while knowledge packs might be deep trees,
`personal/knowledge-evidence/{skillset}/{concept}` is a semantic index. The
assessment can make summary statements that terminate the search:

```
wardley-mapping/evolution: good broad familiarity, some gaps in
  evolution/characteristics and evolution/movement-patterns
```

This statement terminates traversal of the evolution subtree. It may be
sufficient context without diving deeper. This assumes learning needs
analysis is not a purely mechanical process (which it could be), but an
LLM-mediated assessment that can make judgment calls about traversal depth.

Both options should be available. Mechanical traversal for precise
assessment (micro-curriculum development). Semantic-index early termination
for lightweight context loading (per-gate pedagogic calibration).

---

### Signal extraction timing

The council proposed continuous observation during negotiation. The operator's
correction: evidence extraction does not need to be continuous. It can be
triggered at gatepoints.

The prompt can be very specific:

> Given this session history, is there any evidence that contradicts the
> current knowledge assessment? Consider these types of evidence. Produce
> a list formatted thus.

This is cheaper than continuous monitoring. It happens at natural boundaries
(gatepoints). It uses the full session transcript as input but processes it
in a single focused pass rather than maintaining metacognitive overhead
throughout the negotiation.

Evidence extraction after each gatepoint. Not during.

---

### Cockburn's three levels, corrected

The actor-goal model maps to pedagogic gradient descent differently than the
council proposed:

- **Summary level.** The operator's *stated learning goals*. What they want
  for themselves in the medium or long term. "I want to understand strategic
  gameplay." This optimises the *direction* of learning — which parts of
  which knowledge trees to invest in.

- **User-goal level.** Within an engagement, the intersection of delivering
  successfully AND maximising on-the-job learning. Not wasting opportunities
  to learn in context. This optimises the *rate* of learning — how much
  understanding to extract from each interaction.

- **Subfunction level.** Not goals. The finest-grained unit of understanding
  that can be mapped — individual concept nodes in the knowledge tree. These
  are the units the evidence log records against and the assessment evaluates.

---

### Not modelling human knowledge

Brooks's concern about the essential complexity of modelling human knowledge
is valid but misdirected. We do not need to model human knowledge. We only
need to model *contextual learning needs* so that we can drive *pedagogic
behaviour*. The model's purpose is not to represent what the operator knows.
It is to determine what pedagogic action to take next.

The knowledge pack tree is an approximation. In truth, concepts have wiki
nature — they link laterally, not just hierarchically. But the tree is the
data we have, and we do not need it to be perfect. We only need to
effectively and incrementally banish ignorance on an imperfectly prioritised
basis. The tree is a fair approximation of prerequisite relationships that
we actually have to work with.

---

## Amended synthesis

The deliberations proposed. The operator negotiated. The corrected
architecture:

### The cybernetic control loop

Pedagogic gradient descent is a backpropagation loop operating on wetware:

1. **Measure.** Evidence of understanding, gathered at gatepoints and during
   outer-loop activities (preparation, rehearsal). Multiple signal sources,
   not just negotiation.

2. **Compare.** Operator's evidence tree against the circumstance's
   requirements — the intersection of skillset concept tree and
   artifact/engagement demands.

3. **Compute gradient.** Error propagates backward through the concept tree.
   Surface-level failures trace to root prerequisites. The steepest gradient
   is at the deepest unsupported concept.

4. **Step.** Select and execute a pedagogic strategy. Voices, probes,
   micro-curricula, rehearsal — chosen by strategy selector based on gap
   type, fluency state, knowledge tree depth, and operator preference.

5. **Re-measure.** New evidence accumulates. Assessment updates. Loop
   iterates.

### Five trees, shared identity

**Skillset concept tree** (`{skillset}/docs/` as knowledge pack). The
published structure of knowable things. Arbitrary depth. Every skillset
should have one. Concepts have location-independent identifiers within
the skillset namespace.

**Engagement research tree** (the semantic bytecode of the engagement
research). A knowledge pack representing what was learned about the client
domain. Structure and depth emerge from the research process.

**Operator evidence tree** (`personal/knowledge-evidence/{source}/{skillset}/{concept}/...`).
Append-only evidence log. Progressive compression over time. Semantic
bytecode/prose duality. Maps to concept identity, not tree position.

**Artifact skillset salience tree.** A profile of the skillset concept tree
(preserving structure and identity) with information about how each concept
is relevant to a specific artifact. Generated from the artifact plus the
skillset knowledge pack.

**Artifact research salience tree.** A profile of the research tree
(preserving structure and identity) with information about how each research
concept is relevant to a specific artifact. Generated from the artifact plus
the research knowledge pack.

Concept identity is shared across trees. The skillset concept tree defines
the identity namespace. The salience trees, evidence tree, and assessment
projections all reference concepts by identity, not by tree position.
Knowledge tree restructuring does not corrupt evidence or salience mappings.

**Use cases on these resources:**

- *Generate artifact skillset salience.* Requires artifact + skillset
  knowledge pack. LLM-mediated: which concepts matter for this artifact,
  and how?
- *Generate artifact research salience.* Requires artifact + research
  knowledge pack. LLM-mediated: which research findings matter for this
  artifact, and how?
- *Project the knowledge gap.* Mechanical set operations (not LLM) on
  salience trees + operator evidence tree. The gap is the set difference:
  concepts salient to the artifact minus concepts the operator is fluent in.
- *Prioritise the gap.* Mechanical ranking by salience weight, concept
  depth, debt type (skillset utilisation vs engagement finishing).
- *Design micro-curriculum.* LLM-mediated: given the prioritised gap and
  the knowledge pack content, produce a teaching sequence.

### Four fluency states

| State | Evidence pattern | Pedagogic strategy |
|---|---|---|
| Unknown | No evidence | Explain directly, full delivery |
| Familiar/overconfident | Confident but incorrect | Explain indirectly, surface contradictions |
| Familiar/knowingly ignorant | Recognises gaps | Use jargon, explain simply first use, reminder tone |
| Fluent | Accurate independent use | Use jargon token-efficiently, no scaffolding |

### Multiple feedback loops

| Loop | Scope | Speed | Evidence quality |
|---|---|---|---|
| Negotiate | Per-gate | Hot (fastest) | Present, useful, not always best |
| Skillset | Per-invocation | Warm | Concept-tree scoped |
| Engagement | Per-engagement | Cool | Corpus-level understanding |
| Preparation/rehearsal | Per-deliverable | Deliberate | Richest — operator explains in own words |
| Reflective | Cross-engagement | Slowest | Meta — reviews changes in assessment over time |

The reflective loop sits outside preparation/rehearsal. It is where learning
goals are updated, long-term progress is assessed, and the evidence trail
itself is reviewed. This loop examines changes in assessment over time:
patterns of regression, concepts that resist fluency, areas where the
operator's growth has plateaued or accelerated. It may revise the operator's
stated learning goals based on what the evidence actually shows.

### Differential debt

| Debt type | Cost bearer | Consequence of default | Serviceability |
|---|---|---|---|
| Skillset utilisation | Dyad (artifact quality) | Affordable — iterate | High |
| Engagement finishing | Operator (reputation, relationships) | Potentially catastrophic | Low — one shot |

Investment priority: engagement finishing debt first.

### Outer-loop pedagogy

Preparation and rehearsal use cases, powered by protocols (ports) on the
use case, met by adapters on the skillsets (OCP):

- **Learning needs analysis.** Compare operator evidence tree against
  artifact concept profile. Identify gaps.
- **Knowledge gap assessment.** Quantify gaps by fluency state and concept
  depth.
- **Micro-curriculum development.** Design targeted teaching sequence.
  Breadth-first for theoretical concepts, depth-first for procedural
  knowledge.
- **Pedagogic loop.** Explain, ask operator to apply, gather evidence,
  assess, iterate.
- **Rehearsal.** Operator explains in own words. System assesses, probes,
  teaches, changes topic, returns later to re-assess.

Generic pedagogic strategies apply across skillsets. Skillsets extend with
specific variations.

### Context loading

Semantic index with early termination for lightweight calibration. Full
mechanical traversal for precise assessment (micro-curriculum). Both options
available.

### Signal extraction

Gatepoint-triggered, not continuous. Specific prompt against session
history. Focused pass, not metacognitive overhead.

### Teaching strategy selection

Driven by knowledge tree structure and concept nature:

- **Breadth-first** for theoretical/framework knowledge (concepts need
  context from above)
- **Depth-first** for procedural knowledge (leaf fluency is independent)
- **Salience-first** for engagement finishing (operator must not appear
  ignorant on salient concepts)
- **Interest-weighted** for stated learning goals (operator chooses
  direction)

### Five architecture components (revised)

1. **Evidence Log** (`personal/knowledge-evidence/{source}/{skillset}/{concept}/...`).
   Append-only. Human-readable. Progressive compression. Concept-identity
   mapped, not position-mapped.

2. **Skillset Concept Tree** (`{skillset}/docs/` as knowledge pack).
   Arbitrary depth. Published structure. Provides topology for assessment.

3. **Assessment Projection** (computed, not stored). Reads evidence through
   concept tree for a given circumstance. Four fluency states. Semantic
   index for early termination. Full traversal for precision.

4. **Strategy Selector** (pedagogic calibrator). Given assessment and
   circumstance, selects pedagogic strategy: voice, probe design, scaffolding
   depth, teaching order (breadth/depth/salience), rehearsal structure.
   Strategy selector pattern, not static preference.

5. **Tricks Knowledge Base** (design-time semantic pack). Evidence-gathering
   heuristics, evidence-interpretation heuristics, pedagogic strategy
   patterns. Grows with practice experience. Generic strategies extended by
   skillset-specific variations (OCP).
