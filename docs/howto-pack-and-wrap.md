# How to compile a knowledge pack

## What `_bytecode/` is

Every knowledge pack directory has a `_bytecode/` mirror containing
compressed summaries of each item. These summaries are generated prose
— no frontmatter, no structured data. They exist so agents can navigate
the pack cheaply, reading full items only when summaries indicate
relevance. The `_` prefix signals "generated, don't edit."

## When to compile

Compile after any edit to a pack item (the markdown files alongside
`index.md`). The conformance test `pytest -m doctrine` fails on dirty
or corrupt design-time packs, so compilation is not optional for
version-controlled packs.

## Check freshness

Run `practice pack status --path <dir>` on the pack directory. The
command reports one of four states per item:

- **clean** — bytecode is newer than its source item
- **dirty** — source item is newer than its bytecode mirror
- **absent** — no bytecode file exists for this item
- **corrupt** — bytecode exists but no corresponding source item

A pack is CLEAN when every item is clean. Dirty and absent items need
compilation. Corrupt items need manual resolution (delete the orphan
mirror or restore the source item).

## Compile one item

For each dirty or absent item:

1. Read the full source item.
2. Generate a compressed summary in prose. No frontmatter. No
   structured data. Prose only.
3. Write the summary to `_bytecode/{item-name}.md`.

### Compression budget

Target ~10–20% of the source item's token count. A 2000-token article
produces a 200–400-token summary.

### What to preserve

- **Domain vocabulary** — use the same terms the source uses. Do not
  paraphrase domain-specific language into generic equivalents.
- **Structural fidelity** — if the source has three sections covering
  three concerns, the summary should reflect three concerns, not
  collapse them into one.
- **Progressive disclosure** — the summary is a routing aid. It tells
  the reader what the item contains and why it matters, so they can
  decide whether to read the full item.

### What to compress

- Examples, extended rationale, historical context, cross-references.
- Repeated explanations of concepts covered in other pack items.
- Code samples (summarise what they demonstrate, don't reproduce them).

### Quality bar

Compression over completeness. A summary that captures the item's
purpose and key claims in precise vocabulary is better than one that
tries to reproduce every detail at reduced fidelity.

## Nested packs

When a pack contains a child pack (a subdirectory with its own
`index.md`), compile bottom-up:

1. Compile the child pack first — its `_bytecode/` must be CLEAN.
2. Then compile the parent. The parent's `_bytecode/{child-name}.md`
   summarises the child pack as a whole — read the child's `index.md`
   manifest and skim its `_bytecode/` summaries to produce the parent-
   level summary.

The parent never descends into the child's source items. It trusts
the child's compilation.

## Verify

Run `practice pack status --path <dir>` again after compilation.
Every item should report clean. The pack state should be CLEAN.

Then run `pytest -m doctrine` to confirm the conformance test passes.
