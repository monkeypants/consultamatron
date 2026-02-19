---
source_hash: sha256:0379bb70a5c6f5aff037222721fdab515b6dac77043e60c324513c736c73a2a2
---
Routing is information transfer — ineligible destinations are data leaks, not noise. Policy: deny-all, allow-some. Needs aggregation and routing are separate policies: aggregation can be permissive (no sensitive data moves), routing must be restrictive (every target explicitly allowed). In practice, both use the same allow list — no point aggregating needs from destinations that can't receive observations.

Three destination classes. Personal/: information-greedy, always allowed, no leak risk. Client workspace + engagement targets: allow-some scoped by engagement config (client workspace always, engagement's projects and permitted partnership skillsets yes, other engagements for same client denied — engagement boundaries are information barriers). Commons/: never direct routing — observations flow through private MCP dark channel (#23) where operator controls disclosure and provenance is untraceable.

Allow list: personal/ always; client workspace always; engagement projects when specified; partnership skillsets per engagement config; practice layer always (non-client-specific by construction); everything else denied.
