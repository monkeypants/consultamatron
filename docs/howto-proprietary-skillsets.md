# Collaborating on Proprietary Skillsets

Some consulting methodologies are proprietary. Your firm has developed
approaches that give you a competitive edge, and you don't want to open-source
them. Partnerships let you share these skillsets with specific collaborators —
clients, sub-contractors, partner firms — without releasing them to the commons.

## What a partnership is

A partnership is a private Git repository that you share with specific people.
It lives under `partnerships/{partnership-slug}/` in your Consultamatron
checkout and is gitignored by the commons repository.

The structure is identical to a commons source:

```
partnerships/
  acme-corp/                   (the partnership slug)
    skillsets/
      acme-strategy/           (a proprietary skillset BC)
        __init__.py
        skills/
        docs/
```

Partners clone Consultamatron, then clone the partnership repository into
`partnerships/acme-corp/`. Their CLI discovers and surfaces the skillsets
exactly as if they were commons skillsets — because structurally they are.

## Setting up a partnership

**On the hosting side:**

1. Create a private repository on GitHub (or your preferred host)
2. Structure it as a skillset source (a `skillsets/` directory with one BC
   per methodology)
3. Invite your collaborators as repository contributors

**For each collaborator:**

```bash
cd your-consultamatron-checkout
git clone git@github.com:your-org/acme-proprietary.git partnerships/acme-corp
```

That's it. The CLI will pick up the skillsets automatically.

## Scoping partnerships into engagements

When you register a project, you specify which skillset to use. Partnership
skillsets are available alongside commons and personal skillsets — the CLI
does not distinguish.

If you want to restrict an engagement to specific sources (e.g. only the
partnership skillset, not commons alternatives), use the engagement's
`allowed_sources` setting:

```bash
practice engagement create \
  --client acme \
  --slug strategy-1 \
  --source commons \
  --source personal \
  --source partnerships/acme-corp
```

(The exact CLI flags depend on the current version — check
`practice engagement create --help`.)

## The T-shaped capability model

The commons gives every operator the horizontal bar: broad, shared
methodology knowledge. Partnership repositories give you the vertical bar:
deep, proprietary expertise tuned for a specific client or domain.

An engagement can draw from both. A Wardley Mapping engagement might use
the commons `wardley-mapping` skillset for the core methodology while a
partnership `acme-strategy` skillset provides client-specific knowledge
packs (industry pantheon, known patterns, reference documents).

## Routing feedback

When a partner identifies an improvement to a proprietary skillset:

1. They raise it in the partnership repository (issue or PR)
2. You review and merge
3. Partners `git pull` in `partnerships/{slug}/` to get the update

The Consultamatron commons never sees proprietary skillset content.
Partner work stays within the partnership boundary.

## Revoking access

To revoke a collaborator's access:

1. Remove them from the GitHub repository
2. Rotate any secrets or credentials associated with the partnership

Their local clone still exists, but they cannot pull updates. For
complete revocation, rotate the repository URL (GitHub transfer to a
new organization, or regenerate deploy keys).
