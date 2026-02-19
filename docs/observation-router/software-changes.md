---
type: specification
---

# Software Change Specification

What needs to change in the platform to support needs-driven
observation routing. Structured around the existing architecture:
entities in `src/practice/entities.py`, repository protocols in
`src/practice/repositories.py`, use cases following the `UseCase`
protocol, CLI DTOs in `bin/cli/dtos.py`.

## Design constraints

**Storage format.** Needs declarations are markdown files with
structured data in YAML frontmatter and prose body as docstring.
Repository implementations serialise/deserialise frontmatter into
Pydantic entities through the semantic waist. Use cases operate in
Python land, not LLM land.

**Guiding principle.** Information needs are driven by actionability
— "what are we able to improve?" A well-formed need passes the test:
"if the observer finds something, what improves?"

**Security posture.** Deny-all, allow-some. Routing is information
transfer. Ineligible destinations are data leaks. The routing policy
is derived from engagement configuration that already exists.

## New entities (`src/practice/entities.py`)

### ObservationNeed

A single declared information need owned by a destination.

```
class ObservationNeed(BaseModel):
    slug: str                  # unique within owner
    owner_type: str            # "client" | "engagement" | "skillset" | "personal" | "practice"
    owner_ref: str             # owner identifier (client slug, skillset name, etc.)
    level: str                 # "type" | "instance"
    need: str                  # what to watch for
    rationale: str             # what improves if the observer finds something
    lifecycle_moment: str      # when this need was declared
    served: bool               # has any observation addressed this need
```

Type-level needs use `owner_ref` as the type name (e.g. "client",
"skillset"). Instance-level needs use the specific identifier (e.g.
"acme-corp", "wardley-mapping").

### RoutingAllowList

The set of destinations allowed to receive observations for a given
context. Derived from engagement configuration — no new configuration
surface needed.

```
class RoutingDestination(BaseModel):
    owner_type: str
    owner_ref: str

class RoutingAllowList(BaseModel):
    destinations: list[RoutingDestination]
```

Three destination classes drive the allow rules:
1. **Personal** — always allowed. No leak risk.
2. **Client workspace and engagement targets** — allowed when the
   engagement config permits. Client workspace always allowed (it's
   the client's own data). Sibling projects within an engagement
   cross-pollinate — the engagement is the trust boundary, not the
   project.
3. **Commons** — never allowed. Flows through the private MCP channel
   (GitHub issue #23). The observation routing system does not route
   to commons.

### Observation

A single observation extracted at an inflection point.

```
class Observation(BaseModel):
    slug: str
    source_inflection: str     # "review" | "gatepoint" | "negotiate" | "pack-and-wrap"
    need_refs: list[str]       # which needs this observation serves
    content: str               # the observation itself
    destinations: list[RoutingDestination]  # resolved by routing
```

## New repository protocols (`src/practice/repositories.py`)

### NeedsReader

Reads needs declarations from their storage locations. Needs live
with their owners — client knowledge pack, skillset config,
engagement brief, practice layer docs.

```
class NeedsReader(Protocol):
    def type_level_needs(self, owner_type: str) -> list[ObservationNeed]:
        """Read type-level needs for a destination type."""
        ...

    def instance_needs(self, owner_type: str, owner_ref: str) -> list[ObservationNeed]:
        """Read instance-level needs for a specific destination."""
        ...
```

Type-level needs live in practice layer manifests — one per
destination type. Instance-level needs live with the destination
instance (in its workspace, config, or brief).

### ObservationWriter

Writes observations to their routed destinations.

```
class ObservationWriter(Protocol):
    def write(self, observation: Observation) -> None:
        """Persist an observation to all its resolved destinations."""
        ...
```

## New use cases

### AggregateNeedsBrief

The primary CLI use case. Aggregates relevant needs into an
observation needs brief for the skill at the inflection point.

```
practice observation-needs --client X --engagement Y
```

Steps:
1. **Build the routing allow list** from engagement configuration.
   Walk the engagement config to determine which destinations are
   eligible. Apply deny-all policy: personal/ always, client
   workspace always, engagement projects, permitted partnership
   skillsets per engagement config. Everything else denied.
2. **Gather type-level needs** for each eligible destination type.
3. **Gather instance-level needs** for each eligible destination
   instance.
4. **Flag duplicates** mechanically — if two needs are textually
   similar or serve the same destination, surface that for the
   operator.
5. **Synthesise the brief** — a document the observing skill can
   consume. Includes the needs, the routing table, and enough
   context for the observer to apply the brief to transient context.

The skill at the inflection point calls this command and receives
the aggregated brief. It does not need to know about destinations,
types, inheritance, or routing policy.

**Needs aggregation uses the same allow list as routing.** If you
can't receive observations, don't contribute needs to the brief.
Wasting brief space on needs that can never be delivered is noise.

### RouteObservations

Accepts observations from any inflection point and dispatches to
destinations whose needs the observation serves.

Steps:
1. Resolve destinations from `need_refs` on each observation.
2. Verify each destination is on the routing allow list.
3. Dispatch. Fan-out is expected — one observation may serve needs
   from multiple destinations.

Routing is nearly mechanical because observations made in response
to declared needs already carry their destination. The routing
mechanism maps needs to destinations and delivers.

### ReviewNeedsHygiene

Surfaces needs that may need maintenance. Run at hygiene review
moments aligned with the declaration lifecycle.

Four failure modes to detect:
- **Staleness** — context has changed, need no longer applies.
- **Duplication** — instance-level need overlaps with type-level or
  another instance.
- **Supersession** — vague early need replaced but not removed.
- **Unserved needs** — need exists but no observation has addressed
  it. Distinction matters: wrong need (prune) vs blind spot
  (investigate).

The aggregation use case flags duplicates mechanically. The hygiene
use case surfaces the broader set.

## Needs lifecycle support

Needs declaration is distributed across each destination type's
existing lifecycle moments. The platform supports this by allowing
needs to be written at multiple points — it does not invent new
activities.

**Client workspace needs** — at research, engagement planning,
during engagement (gatepoint feedback loop), engagement review,
between engagements.

**Engagement needs** — at planning, during execution (gatepoint
feedback), review (promotion to type-level).

**Skillset needs** — at ns-design, ns-implement, rs-assess,
rs-iterate, during execution.

**Personal needs** — at goal setting, during engagement, personal
review.

**Practice layer needs** — at practice planning, during engagement,
post-review pattern recognition.

Who authors depends on the lifecycle phase — operator at planning,
agent at gatepoints (proposes based on observations), both at
review, skillset author at engineering.

## Needs evolution support

Two timescales that the platform must accommodate:

**Within-engagement.** Observations at gatepoint N produce needs for
gatepoint N+1. The observation system feeds itself — the act of
observing something interesting is also the act of declaring a need
for the next inflection point. The platform supports this by
allowing the gatepoint skill to write new instance-level needs as
a side effect of observation.

**Across-engagements.** Instance-level patterns noticed across
engagements get promoted to type-level at review. The promotion
path: instance observation → pattern recognition → type-level need.
The review skill is the natural promotion moment. The platform
supports this by allowing review to write type-level needs.

## Skill changes at inflection points

Each inflection point skill gains a step at the beginning:

1. Request the observation needs brief from the CLI
2. Hold the brief alongside the rich transient context
3. After the skill's primary work, apply the brief to extract
   observations that serve declared needs
4. Output observations for routing

Skills may also write new needs as a side effect of observation
(within-engagement evolution — gatepoint N observations produce
gatepoint N+1 needs).

### Review skill

The comprehensive sweep — the brief is at its fullest. Review
applies the full brief to the full engagement context. Observations
made here serve any needs that opportunistic observation missed.
Review is also the promotion moment — instance patterns become
type-level needs.

### Gatepoint handling

Lightweight. The brief is available but the agent applies it only to
what surfaced during the gate negotiation. Must not slow down or
complicate gate negotiation — observation is a side channel. The
gatepoint may write new instance-level needs for subsequent
gatepoints (self-feeding evolution).

### Negotiate loop

Multi-scope. The brief covers all destinations. The agent applies it
both to the substantive content of the negotiation and to pedagogic
signals from operator engagement.

### Pack-and-wrap

Local only. Does not request the cross-context needs brief. The pack
itself declares what it needs observed during compilation (structural
integrity, cross-reference validity, summarisation strategy fitness).

## What does NOT change

- Client workspace structure (already a knowledge pack)
- Pack convention (already supports the accumulation pattern)
- Engagement lifecycle (observation is additive, not restructuring)
- Engagement configuration surface (routing policy is derived from
  existing config — no new fields needed)
- Integration surface capabilities (client workspace participates
  in existing capabilities)
- Propose-negotiate-agree loop (observation is a step within existing
  skills, not a new skill)
