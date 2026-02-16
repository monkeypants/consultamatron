# Consultamatron: Multi-Product Consulting Practice

This repository contains agent skills for conducting strategic consulting
engagements. Skills are organised into **skillsets** (product lines) that
share a common client workspace and research base.

## Architecture

```
org-research → engage → {skillset pipeline} → review
```

1. **org-research** gathers information about a client organisation
2. **engage** plans which projects to run and in what order
3. Each project follows its skillset's pipeline
4. **review** captures lessons learned and raises improvement issues

Each bounded context declares its skillsets as Python data in its
`__init__.py` module. The skillset list is dynamic — new skillsets
can be registered as prospectuses (empty pipeline) or implemented
(with a pipeline of stages and gates).

## Discovering skills

Do not assume you know which skills or skillsets exist. Discover
everything through the practice CLI:

```bash
uv run practice skillset list                    # all registered skillsets
uv run practice skillset list --implemented true # only implemented skillsets
uv run practice skillset show --name <name>      # pipeline, gates, skill names
uv run practice source list                      # installed skillset sources
uv run practice project progress                 # current pipeline position
```

Each implemented skillset defines a pipeline of skills (stages) with
gate artifacts. Use `skillset show` to discover the specific skills,
their ordering, and prerequisites for any skillset.

### Loading a skill

The practice CLI gives skill names. To find the skill file, search
the repository:

```bash
find . -name SKILL.md | grep <skill-name>
```

Read the SKILL.md file before executing any skill. It contains the
methodology, acceptance criteria, and operational instructions.

### Shared skills

Some skills operate outside any skillset pipeline (org-research,
engage, editorial-voice, review). These are discoverable the same
way — their SKILL.md files live at the repository root.

## Operator workspace

The repository has three source containers for BC packages, plus
operator-private directories:

```
consultamatron/
├── commons/                          # committed BC packages
│   ├── wardley_mapping/              # BC package (skills/, presenter, tests)
│   ├── business_model_canvas/        # BC package
│   ├── skillset_engineering/         # BC package (ns-*, rs-*)
│   └── consulting/                   # engagement lifecycle BC
├── partnerships/                     # gitignored, per-engagement
│   └── {slug}/                       # each is a git repo with BC packages
│       └── {bc_package}/__init__.py  # has SKILLSETS
├── personal/                         # gitignored, always included
│   └── {bc_package}/__init__.py      # has SKILLSETS
├── clients/                          # gitignored client workspaces
│   └── {org-slug}/
│       ├── resources/                # Shared research (managed by org-research)
│       │   ├── index.md              # Manifest + synthesis (gate artifact)
│       │   └── {topic}.md            # Sub-reports with citations
│       ├── engagements/
│       │   ├── index.json            # Engagement registry
│       │   └── {engagement-slug}/    # One engagement = one unit of contracted work
│       │       ├── projects.json     # Project registry for this engagement
│       │       └── {project-slug}/   # One directory per project
│       │           └── decisions.json
│       ├── engagement-log.json       # Cross-engagement audit trail
│       └── review.md                 # Engagement-level review synthesis
├── src/practice/                     # shared infrastructure
├── bin/                              # CLI + scripts
└── tests/                            # root-level conformance/integration
```

`clients/`, `partnerships/`, and `personal/` are `.gitignored`.
See `GETTING_STARTED.md` for setup instructions.

Research is client-scoped (you research the org, not the engagement).
Projects are engagement-scoped. The audit log spans all engagements.

See `org-research/assets/workspace-layout.md` for the full client
workspace directory structure including per-skillset project layouts.

## Engagement lifecycle

An engagement is a unit of contracted work with a client. It scopes
which skillset sources are permitted and contains projects.

```
planning → active → review → closed
```

Each engagement has an `allowed_sources` list controlling which
skillset sources (commons, partnerships) can be used for projects
within that engagement. Commons is always present.

Before starting any skill, check `clients/` for existing engagements.
If work already exists for an organisation, resume from where it left
off. Read the engagement log and project decision logs to understand
what has already been agreed.

## Source discovery

Skillset sources determine where skillset definitions come from. All
three use the same BC package structure (Python package with
`__init__.py` exporting `SKILLSETS`):

- **commons** — committed BC packages in `commons/` (always included)
- **personal** — operator-private BC packages in `personal/` (always included)
- **partnerships** — per-engagement BC packages in `partnerships/{slug}/`

Use `practice source list` to see installed sources and
`practice source show --slug <slug>` for detail.

## Partnership and personal skillsets

Operators may have proprietary skillsets in `partnerships/` or
`personal/`. Each is a full BC package — same structure as commons
packages, with `__init__.py` exporting `SKILLSETS`, skill files,
presenter, and tests. The conformance test suite applies uniformly
to all source containers.

Personal skillsets are always available (like commons). Partnership
skillsets require explicit `add-source` on the engagement.

## Gate protocol

The `.agreed.md` and `.agreed.owm` suffixes mean the client has explicitly
confirmed the artifact. Skills create these only after the client says the
output is acceptable. Never create a gate artifact without client
agreement.

Each skillset defines its own gate sequence. Gates are relative to the
project directory. Use `practice skillset show --name <name>` to see
gates for a specific skillset.

## OWM rendering

Some skillsets produce `.owm` map files. To render to SVG:
```
bin/ensure-owm.sh path/to/map.owm
```

This script checks for `cli-owm`, installs it via npm if missing, and
writes an SVG next to the OWM file. Node.js (npx) is required. Always
render after writing or updating an OWM file so the client can see the
visual map.

## Artifact format discipline

- **Organisation research**: Markdown with citations.
- **OWM maps**: Only produce `.owm` files when both axes (visibility
  and evolution) have grounded meaning. Early pipeline stages that
  lack evolution data use markdown only. Each skillset's pipeline
  documents which stages produce OWM output.
- **Presentations and tours**: Markdown prose in the Consultamatron
  editorial voice. Tours reference analytical content, not duplicate it.
- **General rule**: Use the simplest format that honestly represents
  what is known. Do not impose false precision.

## Site generation

After any skill completes (or after manual edits to workspace artifacts),
regenerate the deliverable site:

```
bin/render-site.sh clients/{org-slug}/
```

This produces a self-contained static HTML site in the workspace's `site/`
directory, suitable for sharing with stakeholders. The site renderer
detects which projects exist and dispatches to per-skillset renderers.

## Client-in-the-loop

Every skill follows a propose-negotiate-agree loop. The agent proposes
output, presents it to the user, incorporates feedback, and only writes
the gate artifact when the user confirms. The agent never decides that
output is "good enough" on its own.

## Choosing the right skill

Use the practice CLI to determine what to do next:

1. Check workspace state: look in `clients/` for existing engagements
2. Run `practice project progress` to see where active projects stand
3. Run `practice skillset show --name <name>` to see the pipeline
4. Find and read the SKILL.md for the next stage

If the user's request is ambiguous, check which gate artifacts exist
in the workspace to determine where the engagement is and which skill
applies.

Before executing any skill, read its SKILL.md to understand the
methodology, acceptance criteria, and operational instructions.
