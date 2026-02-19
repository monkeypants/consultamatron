Knowledge packs provide dual-audience knowledge management through the semantic pack convention. Skillsets supply directories with `index.md` manifests (name, purpose, actor_goals, triggers), items with `type:` frontmatter, and `_bytecode/` mirrors with generated summaries.

Two access paths: human path (summary.md then item bodies) and agent path (`_bytecode/` mirror for token-efficient progressive disclosure). Design-time packs live in BC source directories; runtime packs in client workspaces.

The `type:` field bridges to knowledge protocols — the pack stores the type, use cases give it meaning. OCP at two levels: pack content open to extension (add a file), pack consumption open to extension (write a new use case).

Verification tiers: shape (Tier 0, zero-token doctrine test), contract (Tier 1, token-conservative structure check), fitness (Tier 2, full progressive disclosure test). Maturity: established.
