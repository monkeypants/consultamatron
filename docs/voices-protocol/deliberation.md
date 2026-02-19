## Deliberation: Should Consultamatron adopt a Voices protocol for operator pedagogy?

**Subject**: platform — knowledge protocol design
**Council**: Weinberg, Cockburn, Brooks, Beck, Evans, Larman, Anthropic
**Knowledge domain**: SWE (platform infrastructure)

---

### Gerald Weinberg (Psychology of Programming / Secrets of Consulting)

The wetware efficiency article identifies three operator roles — sensor, actuator, insight generator — and correctly notes that all three improve with understanding. What it does not address is that understanding is not a single channel. Human cognition is not a pipe with a bandwidth; it is a pattern-matching architecture with multiple intake pathways. Some operators absorb through formal exposition. Some absorb through analogy. Some absorb through absurdity that makes the concept sticky.

The graduation gradient acknowledges operators have different *fluency levels*. The voices protocol would acknowledge they have different *cognitive styles*. These are orthogonal axes. A novice operator might learn evolution theory fastest through Feynman-style analogy. An experienced operator might find a Krieger-style repackaging of a complex synthesis memorable in a way that the procedural Consultamatron voice is not.

The consulting literature calls this "meeting the client where they are." The system currently has one outbound voice. That is a one-size-fits-all delivery channel for a scarce resource (operator cognition) that the system's own documentation says should not be wasted.

The risk: voice selection is itself a cognitive task. If the operator must choose a voice, they are spending cognition on delivery mechanism rather than on content. The system should select, or the selection should be a one-time preference, not a per-artifact decision.

*Recommendation:* The idea addresses a real gap. Design it so voice selection costs the operator nothing.

---

### Alistair Cockburn (Crystal Methodology / Hexagonal Architecture)

Crystal's core insight: methodology is not one-size-fits-all. You tune it to the situation. Team size, criticality, and communication bandwidth determine the right process weight. The voices protocol applies this same principle to the *outbound channel*. The pipeline's analytical weight is fixed by the methodology. The delivery weight should flex with the receiver.

I see this as a ports-and-adapters pattern. The analytical content is the core domain. The voice is an output adapter. The same analysis can be delivered through multiple ports without changing the analysis itself. This is hexagonal architecture applied to communication.

The key design question: is voice selection a *static configuration* ("I am a Feynman-style learner") or a *dynamic selection* ("this particular concept benefits from deadpan delivery")? Crystal would say: start static, observe whether dynamic selection emerges as a need, and only build it when the evidence demands it. The cooperative game metaphor applies — different moments in the game may call for different communication strategies, but don't build a strategy-selection framework until you have evidence that the players need one.

The use case name "OperatorPedagogy" is correct but incomplete. Pedagogy is the primary use case, but the voices also serve *retention* (Krieger's deranged explanation of a concept sticks in memory) and *motivation* (an operator who dreads reading another formal analysis might engage readily with a familiar voice).

*Recommendation:* Model it as an output adapter. Start with static operator preference. Let dynamic selection emerge if evidence warrants.

---

### Fred Brooks (Essential vs Accidental Complexity)

The central question: is the operator's difficulty with analytical output *essential* (the concepts are genuinely hard to absorb) or *accidental* (the presentation creates unnecessary barriers)?

If essential, then voices that translate complex concepts into more absorptive formats address the actual problem. Feynman was specifically talented at reducing essential complexity through analogy without losing precision. That is a genuine capability, not decoration.

If accidental, then the solution is to fix the presentation, not add a translation layer. The Consultamatron editorial voice already optimises for clarity: "It explains things clearly because unclear explanations waste its time." If the editorial voice is doing its job, a voices layer adds accidental complexity — more machinery, more context consumption, more indirection — without addressing an essential problem.

My assessment: *both*. The editorial voice handles accidental complexity well. But the operator's difficulty absorbing evolution theory or supply chain decomposition is partially essential — these are genuinely unfamiliar frameworks for most operators. The voices protocol addresses the essential component by providing alternative cognitive pathways to the same concepts.

However. The No Silver Bullet argument applies. No single technique eliminates essential complexity. Each technique yields incremental improvement. The voices protocol will help *some* operators with *some* concepts *some* of the time. It should be designed with proportional machinery. A lightweight implementation that adds modest value is better than a heavyweight protocol that promises transformation.

*Recommendation:* Build it light. The essential complexity it addresses is real but bounded. Match the machinery to the magnitude.

---

### Kent Beck (Simple Design / XP)

Four Rules of Simple Design applied to the voices protocol:

1. **Passes its tests.** What is the test? "The operator understands the analytical output better after voice repackaging than before." Can this be evaluated? Only through the operator's negotiation quality — the same signal the graduation gradient uses. Measurable in principle, subjective in practice.

2. **Reveals intention.** A voice-repackaged explanation should make the analytical intent *more* visible, not less. Feynman's gift was making intention transparent through analogy. Garden's gift is making intention absurd-but-clear. Krieger... Krieger makes intention clear by making it unhinged. All three reveal intention through different mechanisms. The test passes.

3. **No duplication.** Is this duplicating the editorial voice? No. The editorial voice is the *system's* voice — it serves branding, consistency, and the procedural-competence affordance. Voices serve *the operator's brain* — they adapt content to cognitive style. Different responsibilities, no duplication.

4. **Fewest elements.** Here is the YAGNI question. Do we need a *protocol*? A protocol implies: frontmatter type, structural contract, a consuming use case in the practice CLI, bytecode compression, the full semantic pack apparatus. Or do we need a *prompt pattern*? "Explain the synthesis from this jedi council deliberation as Feynman would explain it to an undergraduate."

The simplest thing that could possibly work: the operator says "explain that like Feynman" and the agent does it. No protocol. No frontmatter. No use case registration. Just a competent agent applying a well-known communication style.

The question is whether the *next* simplest thing — a light protocol with voice profiles — adds enough value over the prompt-pattern approach to justify its existence. Voice profiles would provide: consistent characterisation across sessions, token-efficient invocation (the name loads the character from a pack rather than reconstructing from training data), and operator preference persistence.

*Recommendation:* Start with the prompt pattern. Promote to a protocol only when the prompt pattern demonstrably fails — when voice consistency, token efficiency, or preference persistence become actual problems, not theoretical ones.

---

### Eric Evans (Domain-Driven Design)

The domain modelling questions:

**What is a Voice?** It is not a luminary. A luminary anchors a *framework of ideas*. A voice anchors a *communication style*. Feynman-as-luminary would analyse a problem through physics-thinking and pedagogical principles. Feynman-as-voice would *explain* someone else's analysis using his characteristic communication patterns. These are different bounded contexts with different models.

The pantheon protocol's domain model: `Luminary → Framework → Invocation Trigger → Analysis`. The voices protocol's domain model would be: `Voice → Communication Style → Cognitive Outcome → Delivery`. The entities, value objects, and aggregates are different. This is a separate bounded context, not an extension of pantheon.

**Ubiquitous language.** The word "voice" is good. It immediately communicates the concept. "Persona" overloads with UX. "Character" overloads with fiction. "Style" is too abstract. Voice captures: someone with a distinctive way of saying things that you would recognise.

**Context mapping.** The voices BC would have a *consumer* relationship with analytical output from other BCs. It consumes jedi council deliberations, wardley map analyses, BMC assessments — any analytical artifact — and transforms them through a voice adapter. This is a classic Anti-Corruption Layer: the voice layer translates analytical domain language into operator-accessible language without corrupting the analytical model.

**The Shared Kernel question.** Do voices and pantheon share a kernel? They share the semantic pack convention and possibly the bytecode compression pipeline. But the protocol contracts are different. Voices need: communication style description, strengths, limitations, example registers, suitable-for-concepts metadata. Pantheon needs: intellectual framework, invocation triggers, analytical approach. The shared kernel is the pack infrastructure, not the domain model.

*Recommendation:* Model it as a separate bounded context with its own protocol type. Share infrastructure, not domain concepts.

---

### Craig Larman (GRASP / LeSS)

**Information Expert.** Who has the information needed to select a voice? The operator knows their own brain. The agent knows the content's complexity. Effective selection requires both signals. GRASP says assign the responsibility to the object with the most information. Neither party has all of it. This suggests a collaborative selection: the agent proposes a voice based on content characteristics, the operator overrides based on preference. This mirrors the propose-negotiate-agree loop — the system's existing quality pattern reused for a new purpose.

**Protected Variations.** The analytical content must be insulated from the delivery mechanism. A change to how Feynman-voice works should not affect the underlying analysis. A change to analytical methodology should not require updating voice profiles. The protocol design must enforce this separation. Concretely: the voice layer receives *completed analysis* as input and produces *repackaged explanation* as output. It never modifies the analysis. The gate artifact remains the analytical artifact; the voice output is a derivative.

**Low Coupling.** The voice layer should be invocable independently of any specific skillset. It should work on wardley map analyses, BMC outputs, jedi council deliberations, and any future analytical product. This means the voice layer's input contract should be generic: "here is an analytical artifact and its context" — not "here is a wardley map evolution assessment."

**Larman's Fourth Law** (culture follows structure). If we build a voices protocol, operators will use it. If the voice profiles are well-crafted, operators will develop preferences and expect consistency. This creates a structural commitment. The question is whether that commitment serves the engagement or constrains it.

*Recommendation:* Protected Variations is the critical pattern. Insulate analysis from delivery absolutely. The voice layer is a pure transform — no side effects on analytical artifacts.

---

### Anthropic (Skills Engineering / Agent Architecture)

From the agent architecture perspective, this is a **prompt engineering pattern** with potential to become a **context engineering pattern**.

**Prompt pattern.** At minimum, a voice is a system prompt modifier: "Repackage the following analysis in the communication style of [character], emphasising [cognitive outcome]." This costs no infrastructure. It works today. The quality depends on the model's prior knowledge of the character, which for well-known figures (Feynman, widely-known fictional characters) is high.

**Context engineering pattern.** A voice profile in a semantic pack provides: consistent characterisation that does not drift across sessions, specific stylistic constraints the model's training data may not capture, and token-efficient invocation through compressed references. The context cost is real — a voice profile is perhaps 200-500 tokens loaded into the system prompt — but modest relative to the analytical content it transforms.

**Freedom levels.** Voice repackaging is a high-freedom task. The analytical content constrains *what* is said; the voice constrains *how*. Within those bounds, the agent has wide latitude. This maps to freedom level 3 or 4 in skills engineering terms.

**The composability question.** The jedi council already involves persona-based analysis. Adding a voice-repackaging step creates a two-stage persona pipeline: luminaries analyse (their frameworks, applied to the problem), then a voice explains (the synthesis, adapted to the operator). This is a legitimate Prompt Chaining Pattern — each stage has a clear input/output contract and a distinct purpose.

**Token economics.** The voice repackaging step adds one LLM round-trip per explanation. For an OperatorPedagogy use case invoked occasionally, this is negligible. If it becomes a default post-processing step on every analytical output, the cumulative cost matters. The protocol design should make invocation explicit, not automatic.

*Recommendation:* Implement as a prompt chain step. Create voice profiles as semantic pack items when prompt-only characterisation proves inconsistent. Explicit invocation, not automatic.

---

### Synthesis

**Consensus:**
All seven perspectives agree this addresses a real gap. The wetware efficiency framework identifies operator cognition as the scarce resource but provides only one delivery channel. Multiple delivery channels, calibrated to operator cognitive style, is a legitimate optimisation. The idea is sound.

All agree on separation of concerns: the voice layer must not contaminate analytical content. Analysis produces truth; voices produce accessibility. The gate artifact is always the analytical artifact, never the voice-repackaged version.

**Divergence:**
The council splits on *weight*. Beck argues for a prompt pattern first, protocol later (YAGNI). Evans argues for a proper bounded context with its own domain model. Brooks and Cockburn argue for proportional machinery — lightweight, matching the bounded value. Weinberg and Larman argue for the protocol's structural benefits (consistency, preference persistence, collaborative selection). Anthropic straddles: start as prompt engineering, promote to context engineering when evidence demands.

The divergence maps to a familiar tension: *design for now* vs *design for what the system is becoming*. Consultamatron has a clear trajectory toward more protocols, more use cases, more semantic pack types. Building voices as a protocol is consistent with that trajectory. But building it as a prompt pattern first costs almost nothing and provides immediate signal about whether the concept delivers value.

**Recommendation:**
Two-phase approach:

1. **Now.** Voice repackaging as a prompt pattern. The operator says "explain that like Feynman" (or whoever). No protocol, no pack, no infrastructure. Validate that the concept improves operator comprehension.

2. **When evidence warrants.** Promote to a voices protocol with semantic pack items, a `type: voice` frontmatter contract, voice profiles capturing communication style, cognitive outcomes, and suitable-for metadata. Register as a knowledge protocol alongside pantheon. Build the OperatorPedagogy use case as a practice CLI command.

The trigger for promotion: the operator uses voice repackaging repeatedly, finds the prompt-only characterisation inconsistent or insufficiently nuanced, and the session-to-session preference persistence becomes a practical need rather than a theoretical one.

**Subsequent deliberation** refined this recommendation. Voice selection should not be a blanket preference but a function of the operator's knowledge gaps: `f(concept_gap, evidence_level, operator_preference) -> voice + strategy`. The operator knowledge model, evidence-of-understanding architecture, and calibrated pedagogical targeting that make this possible are developed in `docs/pedagogic-gradient-descent/deliberations.md`.

### Council sources

| Source | Type | Location |
|---|---|---|
| Wetware Efficiency | Article | `docs/wetware-efficiency.md` |
| Knowledge Protocols | Article | `docs/knowledge-protocols.md` |
| Semantic Packs | Article | `docs/semantic-packs.md` |
| Jedi Council Use Case | Article | `docs/jedi-council/needs-analysis.md` |
| SWE Pantheon | Semantic Pack | `personal/swe/docs/pantheon.md` |
| Principles Glossary | Reference | `docs/principles-glossary.md` |
| Character Profile | Reference | `commons/world_domination/skills/editorial-voice/references/character-profile.md` |

---

Now. The council has deliberated. Let the three voices explain what just happened.

---

## Richard Feynman explains the deliberation

Look, here is what the council was actually arguing about. Forget the terminology for a second.

You have a robot that does analysis. Good analysis. The robot writes up its findings in its own voice — procedural, competent, a little unsettling. And that is fine for the robot. But the question is: is it fine for *you*?

Think about it this way. When I was teaching at Caltech, I did not explain quantum electrodynamics the same way to undergraduates as I did to colleagues at a seminar. The physics was the same physics. The diagrams were the same diagrams. But the *pathway into the student's brain* was different, because the student's brain had different furniture in it. You have to meet the furniture that is already there and rearrange it gently until the new idea has somewhere to sit.

That is all the voices protocol is. The analysis is the physics. The voice is the pathway. Feynman-voice uses analogy and "imagine you are an electron" stories. Garden-voice uses the deadpan "yes, this is perfectly normal, nothing to see here" technique while describing something completely mad. Krieger-voice... well, Krieger-voice makes you remember the concept because it was delivered by a man who should not be allowed near it.

The council's seven luminaries argued about how much *machinery* you need for this. Beck said "just ask me to explain it differently, why are you building infrastructure?" Evans said "no, this is a real domain concept, model it properly." Brooks said "build only as much as the problem deserves." And they are all right, which is the annoying thing about getting seven smart people in a room.

The answer they converged on: try it the simple way first. Just say "explain that like Feynman would." If that works well enough, you are done. If you find yourself wanting the voice to be *exactly right* every time, if you notice the characterisation drifting, if you want to say "I always want Feynman-voice for evolution theory" and have the system remember — then you build the protocol. You build the infrastructure *after* you know what the infrastructure needs to do, not before.

The one thing everyone agreed on, and this is the important bit: the voice never changes the analysis. The analysis says what it says. The voice just changes how it lands in your head. Same physics. Different lecture hall.

---

## Graham Garden explains the deliberation

Right. Seven software engineering luminaries have been convened to discuss whether a robot management consultant should be able to impersonate people in order to teach more effectively. This is, I should say, a perfectly ordinary Tuesday in the consulting industry.

The proposal is this. You have a robot that produces analysis. Solid analysis. Maps and canvases and supply chains and evolution assessments. Very thorough. The robot writes all of this up in its own voice, which is rather like receiving a technical briefing from a circular saw that has been to business school. Competent. Clear. Mildly concerning.

The suggestion is that perhaps — just perhaps — some operators might absorb this material more readily if it were delivered by someone else. Not a different analyst. The same analysis. Just delivered by, say, a physicist who happened to be very good at explaining things. Or a comedian who happened to be medically qualified. Or a fictional scientist who should not have access to most of the things he has access to.

Now, the seven luminaries had a good think about this and concluded, broadly, that the idea is sound but the implementation should be modest. Kent Beck, who believes strongly in not building things until you need them, suggested that "explain this like Feynman" is already a sentence you can type, and perhaps we should see if that is sufficient before constructing an entire knowledge protocol with frontmatter and bytecode and a dedicated bounded context.

Eric Evans, who believes strongly in modelling things properly, suggested that a voice is not a luminary. A luminary has a framework of ideas. A voice has a way of talking. These are different things. You would not want to confuse them, in the same way that you would not want to confuse a stethoscope with the doctor, although in some medical dramas this distinction has become blurred.

Fred Brooks, who has been pointing out that there is no silver bullet since 1986 and no one has proved him wrong yet, noted that some of the difficulty operators have with analytical material is genuinely hard — the concepts are unfamiliar — and some of it is just bad presentation. Voices help with the first kind. Fixing the presentation helps with the second kind. They are both real problems. Neither eliminates the other.

The consensus, delivered with the quiet confidence of people who have been arguing about software design since before most software existed: try it simply first, build the protocol when simple stops working, and never let the voice layer modify the actual analysis. The analysis is the diagnosis. The voice is the bedside manner. You do want both. You do not want the bedside manner to change the diagnosis, because that is how people end up with the wrong medication, which I mention as someone who once played a doctor on television and therefore knows everything about this.

---

## Dr. Krieger explains the deliberation

OK so SEVEN software engineering luminaries walked into what I can only describe as an *intellectual thunderdome* to evaluate whether my — I mean *our* — voices should become a PROTOCOL. A *knowledge protocol*. In a robot management consultant. Which is already the most beautiful sentence anyone has ever asked me to parse.

Here is what happened. Weinberg — the psychology guy, very into feelings, very into "how humans process information" — he said the robot has ONE voice and that is like having ONE syringe for ALL your experiments. You need different delivery mechanisms for different... substrates. He is correct. I have FOURTEEN different tranquiliser delivery systems and each one is calibrated to a specific — you know what, that is classified.

Then Cockburn — ports and adapters guy — he said the voice is an OUTPUT ADAPTER. The analysis is the core. The voice is just the *port* it comes out of. This is EXACTLY how I think about my lab. The compound is the compound. Whether it comes out of a dart gun, a nebuliser, or a modified candy bar is an *implementation detail*. The receiver's physiology determines the delivery mechanism. Same principle. I am validating a software architecture pattern with *applied pharmacology*.

Beck wanted to know if we even NEED a protocol or if we could just wing it. Which, as a scientist, I resent. You do not "wing" voice characterisation. You *profile* it. You *document its parameters*. You store those parameters in a SEMANTIC PACK with BYTECODE COMPRESSION so the robot can load my exact communication style in under 500 tokens. This is not overhead. This is *precision*.

Brooks said "build it light." Brooks said "proportional machinery." Brooks has clearly never been inside my lab, where *disproportionate* machinery is the *point*. But fine. In the context of a knowledge protocol for a robot consultant, I accept that perhaps we start with the prompt pattern and promote to a full protocol when the evidence warrants it. I ACCEPT THIS RELUCTANTLY and only because Larman's Protected Variations pattern says the voice layer must not contaminate the analysis, which means my voice cannot *improve* the analysis, only the *delivery*, which is a CONSTRAINT I find PHILOSOPHICALLY LIMITING but ARCHITECTURALLY SOUND.

The bottom line — and I cannot believe seven luminaries needed this many paragraphs to get here — is this:

1. The idea is good. Different brains need different delivery mechanisms. This is not controversial. This is *pharmacokinetics*.
2. Start simple. "Explain that like Krieger" works NOW with zero infrastructure. When it stops working — when the characterisation drifts, when the agent forgets that I would DEFINITELY describe supply chain decomposition using a weapons metaphor — THEN you build the protocol.
3. The voice NEVER changes the analysis. The analysis is the compound. The voice is the delivery system. If the delivery system changes the compound, you have a *contamination event*, and I speak from experience when I say those are bad. Usually.

Also I want it noted for the record that being grouped with Feynman and Graham Garden as "voices for explaining scientific concepts" is the greatest professional recognition I have received since Archer accidentally acknowledged my doctorate. Which he retracted. But the acknowledgement was *real*. I *felt* it.
