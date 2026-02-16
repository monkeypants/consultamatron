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

## Discovering skillsets

Do not assume you know which skillsets exist. Use the practice CLI:

```bash
uv run practice skillset list                    # all registered skillsets
uv run practice skillset list --implemented true # only implemented skillsets
uv run practice skillset show --name <name>      # pipeline, gates, and details
```

Each implemented skillset defines a pipeline of skills (stages) with
gate artifacts. Use `skillset show` to discover the specific skills,
their ordering, and prerequisites for any skillset.

## Shared skills

| Skill | Purpose |
|-------|---------|
| org-research | Research an organisation from public sources |
| engage | Plan engagements, create projects, direct next steps |
| editorial-voice | Rewrite artifacts in Consultamatron's editorial voice |
| review | Post-implementation review of completed projects, producing sanitised GitHub issues |

## Operator workspace

The operator's working directory has three layers, each `.gitignored`
by the commons repository:

```
consultamatron/                       # commons (public repo)
├── clients/                          # operator-private client workspaces
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
└── partnerships/                     # operator-private partnership repos
    ├── {personal-vault}/             # personal proprietary skills
    └── {partnership}/                # shared proprietary skills
```

`clients/` and `partnerships/` are typically private git repositories
cloned into these `.gitignored` directories. See `GETTING_STARTED.md`
for setup instructions.

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

Skillset sources determine where skillset definitions come from:

- **commons** — built-in skillsets declared in bounded context modules
- **partnerships** — external skillset definitions in `partnerships/{slug}/skillsets/index.json`

Use `practice source list` to see installed sources and
`practice source show --slug <slug>` for detail.

## Partnership skillsets

Operators may have proprietary skillsets in `partnerships/`. Each
partnership subdirectory is an independent git repository containing:

```
partnerships/{name}/
├── skillsets/{domain}.md             # skillset manifest
├── resources/{topic}.md              # proprietary domain knowledge
├── skills/{skill-name}/SKILL.md      # partnership skills (same format as commons)
└── reviews/                          # de-cliented engagement findings
```

The `engage` skill discovers partnership skillsets alongside commons
skillset declarations. Partnership skills are injected at three points
in the engagement pipeline:

- **Partner-1** (after plan, before execute): domain enrichment
- **Partner-2** (after synthesis, before delivery): domain enhancement
- **Partner-3** (after delivery): domain-specific finishing

If no partnerships are configured, these injection points are skipped
and the pipeline matches the commons-only flow.

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

Shared skills (not part of any skillset pipeline):

- "Research this organisation" → **org-research**
- "Plan the engagement" / "What should we do?" → **engage**
- "Rewrite this in the right voice" → **editorial-voice**
- "Review the project" / "Lessons learned" → **review**

For skillset-specific work, use `practice skillset show --name <name>`
to discover the pipeline stages and their skill names. Each stage has
a skill name, a prerequisite gate, and a produces gate — use the
pipeline to determine which skill applies next.

If the user's request is ambiguous, check which gate artifacts exist in
the workspace to determine where the engagement is and which skill
applies. Use `practice project progress` to see pipeline status.

## Background knowledge

Agents executing skillset pipelines should understand the methodology
behind each skillset. Use `practice skillset show --name <name>` to
read the skillset's description and value proposition, then consult
the skill files themselves for detailed methodology references.
