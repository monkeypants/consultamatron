---
name: iteration-2-worked-example-and-lifecycle
purpose: >
  Compressed output of iteration 2. Worked example validated the
  pattern against a realistic scenario. Operator refinements
  established needs guiding principle, storage format, needs
  lifecycle, evolution timescales, and hygiene model.
---

# Iteration 2 — Worked Example and Needs Lifecycle

Traced the full observation-routing pattern through a concrete
scenario, then deepened the needs protocol with lifecycle, evolution,
and hygiene models.

## Conversation arc

1. Operator chose worked example over implementation or article
   synthesis to pressure-test the model.
2. Traced a gatepoint scenario (fictional engagement with three
   projects: BMC, consulting, wardley-mapping) through all four
   stages of the pattern.
3. Worked example validated: routing table construction (deny-all),
   needs aggregation (type + instance, deduplication), observation
   extraction (three observations from one operator remark), routing
   to multiple destinations.
4. Client identity leaked into public documentation. Caught by
   operator, scrubbed immediately. Lesson: never use real client
   identifiers in repo-tracked artifacts — use fictional examples.
5. Closed two open questions from worked example: brief size at
   scale (wait and see — no evidence of a problem yet), observation
   granularity (no fixed granularity — route to whoever needs it).
6. Operator established guiding principle for needs: "what are we
   able to improve?" Needs are driven by the ability to act.
   Well-formed need test: "if the observer finds something, what
   improves?"
7. Storage format decided: markdown with structured YAML frontmatter,
   Pydantic entities in `src/practice/entities.py`, repository
   serialisation through the semantic waist. Use cases in Python
   land, not LLM land.
8. Sibling projects within an engagement cross-pollinate.
   The engagement is the trust boundary, not the project.
9. Operator asked "when are needs written?" — reframing from
   "who" to "when" as the more important question.
10. Needs lifecycle developed: each destination type has multiple
    declaration moments distributed across existing practice
    activities (research, planning, gatepoints, review, skillset
    engineering). No new activities invented.
11. Distributed authoring: who writes depends on the lifecycle
    phase — operator at planning, agent at gatepoints, both at
    review, skillset author at engineering.
12. Needs evolution at two timescales: within-engagement feedback
    loop (gatepoint N observations produce gatepoint N+1 needs)
    and cross-engagement promotion (instance → pattern → type,
    review is the promotion moment).
13. Needs hygiene: staleness, duplication, supersession, unserved
    needs. Unserved needs require diagnosis — wrong need (prune)
    or blind spot (investigate). Hygiene review moments align with
    declaration lifecycle.

## Key design decisions

**Guiding principle.** Needs are driven by actionability — "what
are we able to improve?" Not curiosity, not completeness, but the
ability to drive behaviour change.

**Storage format.** Markdown+frontmatter with Pydantic entities.
Same convention as existing practice infrastructure. Semantic waist
between LLM-facing prose and Python-facing structured data.

**Sibling project cross-pollination.** Engagement is the trust
boundary. All projects within an engagement share a confidentiality
context and can receive each other's observations.

**Needs lifecycle is distributed.** Not a single declaration event
per destination but multiple moments across the destination's
existing lifecycle. The observation system doesn't invent new
activities — it piggybacks on research, planning, gatepoints,
review, and skillset engineering.

**Self-feeding evolution.** Observations produce future needs.
The observation system's input (the needs brief) is refined by
its own output (observations). Within-engagement: fast feedback
at each gatepoint. Across-engagements: slower promotion from
instance to type at review.

**Needs hygiene as maintenance.** Needs degrade like any knowledge
artifact. Staleness, duplication, supersession, and unserved needs
are the four failure modes. Hygiene review piggybacks on the same
lifecycle moments as declaration.

## Closed questions

- Brief size at scale: wait and see. No evidence of a problem.
- Observation granularity: no fixed granularity. Route to whoever
  needs it.
- Instance-level needs authoring (who): depends on lifecycle phase.
- Instance-level needs authoring (when): distributed across
  destination's lifecycle moments.

## Accumulator items after this iteration

Seven items in the pack:
1. `general-pattern.md` — four-stage needs-driven pattern
2. `inflection-point-taxonomy.md` — four types, three cross-context
3. `observation-needs-protocol.md` — substantially expanded with
   lifecycle, evolution, hygiene, guiding principle, storage format
4. `observation-routing-split.md` — high/low freedom separation
5. `routing-security-model.md` — deny-all, three destination classes
6. `software-changes.md` — platform change specification sketch
7. `worked-example.md` — fictional gatepoint scenario

## Agreed summarisation strategies (for this compression)

- Preserve: guiding principle, storage format, needs lifecycle per
  destination type, evolution timescales, hygiene model, sibling
  cross-pollination, closed questions
- Compress: worked example to key conclusions, client identity
  incident to one-line lesson
- Drop: file creation mechanics, bytecode compilation rounds,
  hook/linter recovery
- Organisation: single document under `_history/iteration-2/`
