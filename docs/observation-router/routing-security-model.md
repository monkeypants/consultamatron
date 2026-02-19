---
type: concept
---

# Routing Security Model

Observation routing is information transfer. Routing an observation
to an ineligible destination is a data leak — not a noise problem
but a trust-destroying, system-ending failure. The routing policy
is deny-all, allow-some.

## Two separate policies

**Needs aggregation** (who contributes to the brief) and **routing**
(who receives observations) have different security postures.

Needs aggregation can be relatively permissive. Asking a destination
"what do you want to know?" does not move sensitive information. The
same client and same skillset across engagements collapse their needs
to a distinct set — the large-table problem is imaginary because of
natural deduplication.

Routing must be restrictive. Every routing target must be explicitly
allowed. The allow list is specific, simple, and testable policy.

## Three destination classes

### Personal — information-greedy, always allowed

The operator's own space. No leak risk. Safe to receive everything.
`personal/` skillsets are always eligible to receive observations
regardless of engagement context. This is the operator's learning
channel.

### Client workspace and engagement targets — allow-some, scoped

The engagement configuration defines the allow list:
- **Client workspace:** always allowed (it's the client's own data
  returning to the client's own knowledge pack)
- **Engagement's own projects:** allowed
- **Engagement's permitted partnership skillsets:** allowed, per
  engagement configuration
- **Other engagements for the same client:** denied. Engagement
  boundaries are information barriers even within the same client.
  An observation from engagement A must not leak to engagement B's
  skillsets or project context.

The allow rules are derived from the engagement configuration that
already exists — no new configuration surface needed. The engagement
already knows its client, its projects, and its permitted skillsets.

### Commons — dark channel only

Observations cannot route directly to shared infrastructure.
Commons skillsets serve multiple operators and potentially multiple
clients. Direct routing would make observation provenance traceable,
violating client confidentiality.

Commons improvements flow through the private MCP channel (see
GitHub issue #23). The operator decides what to share, in a form
that is not traceable to source. This is the "good consultant"
pattern — internalise lessons from confidential engagements, apply
them generally, never leak provenance.

The observation routing system does not route to commons. The review
skill and the private feedback channel handle that boundary.

## Deny-all, allow-some

The default routing policy is deny. A destination receives
observations only if an explicit allow rule includes it. The allow
rules are:

1. `personal/` — always allowed
2. Client workspace for the specified client — always allowed
3. Engagement's projects — allowed when engagement is specified
4. Engagement's partnership skillsets — allowed per engagement config
5. Practice layer — allowed (practice-level observations are
   non-client-specific by construction)
6. Everything else — denied

The allow list is short, specific, and testable. Each rule maps to
a verifiable property of the engagement configuration.

## What the council got wrong

The jedi council deliberation optimised for observation quality —
minimising noise in the brief. The real risk is not noise but
information leakage. "Start permissive and tighten later" is the
wrong default for a system that moves information between trust
boundaries. The correct default is deny-all, with simple allow rules
that are specific enough to test.

## Relationship to needs aggregation

The needs aggregation policy can be more permissive than the routing
policy because aggregation does not transfer sensitive information.
However, the routing allow list constrains which destinations'
observations will actually be delivered. A destination may contribute
needs to the brief but never receive observations if the routing
policy excludes it. In practice, including needs from a
routing-ineligible destination wastes brief space — the observer
extracts observations that can never be delivered.

The pragmatic approach: the needs aggregation uses the same allow
list as routing. If you can't receive observations, don't contribute
needs.
