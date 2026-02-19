A semantic pack is a directory of markdown files with an `index.md` manifest, `type:` frontmatter on items, and a `_bytecode/` mirror of generated summaries. Two access paths: human (summary.md → item bodies) and agent (`_bytecode/` → selective full reads). Neither path is subordinate.

Items are pure content (minimal frontmatter, human-maintained). `_bytecode/` files are generated prose (no frontmatter, compressed summaries). The `_` prefix signals "generated, don't edit." Pack states: clean (all bytecode newer than sources), dirty (at least one item newer), absent (no `_bytecode/`), corrupt (orphan mirrors).

Packs nest recursively — composite items are sub-packs with their own `index.md`. Parent `_bytecode/` summarises child packs from their manifests and summaries, never descending into child source items. Bottom-up compilation.

Two lifecycle contexts: runtime packs (client workspaces, engagement-scoped) and design-time packs (source directories, version-controlled). Pack-and-wrap is protocol-agnostic — compresses any item regardless of type. Topic vs protocol is a separate concern. OCP at two levels: content open to extension, consumption open to extension, convention closed.
