# Consultamatron

Agent-driven consulting practice. Skills execute methodologies; skillsets
bundle skills into pipelines; profiles bundle skillsets for activity types.

## Concepts

A **skill** is a single methodology step with a SKILL.md file, acceptance
criteria, and gate artifacts. Skills follow a propose-negotiate-agree loop
with the operator.

A **skillset** is a pipeline of skills that delivers a consulting product.
Each stage produces a gate artifact (`.agreed.md` or `.agreed.owm`) that
the next stage requires. Gates are only written after explicit operator
agreement.

A **profile** is a named collection of skillsets for a type of activity
(e.g. "strategic consulting" bundles the engagement lifecycle with
analytical skillsets).

## Discovery

Do not assume you know which skills, skillsets, or profiles exist.
Discover everything through the practice CLI:

```bash
uv run practice profile list                     # activity profiles
uv run practice profile show --name <name>       # skillsets in a profile
uv run practice skillset list                     # all registered skillsets
uv run practice skillset show --name <name>       # pipeline, gates, skill names
uv run practice skill path --name <name>          # filesystem path to a skill
uv run practice project progress                  # current pipeline position
uv run practice engagement status --client X --engagement Y  # pipeline position for all projects
uv run practice engagement next --client X --engagement Y    # recommended next skill
```

Read the SKILL.md file before executing any skill.

## Engagement steering

1. Check `clients/` for existing workspaces and engagements
2. If resuming: read the engagement log and decision logs
3. If new: run `org-research` then `engage` to plan work
4. Use `engagement status` to see pipeline position for all projects
5. Use `engagement next` for a recommendation on which skill to run
6. Execute projects through their skillset pipelines
7. Run `review` after all projects complete

If the user's request is ambiguous, use `engagement status` to derive
where the engagement is from gate artifacts on disk.

## Workspace

```
clients/{org-slug}/
├── resources/                 # org-research output
├── engagements/
│   ├── index.json             # engagement registry
│   └── {engagement-slug}/
│       ├── projects.json
│       └── {project-slug}/
│           └── decisions.json
├── engagement-log.json
└── review.md
```

`clients/`, `partnerships/`, and `personal/` are gitignored.

## Operator-in-the-loop

Every skill follows a propose-negotiate-agree loop. The agent proposes
output, presents it to the operator, incorporates feedback, and only
writes the gate artifact when the operator confirms. The agent never
decides that output is "good enough" on its own.

## Gates

The `.agreed.md` and `.agreed.owm` suffixes mean the operator has explicitly
confirmed the artifact. Never create a gate artifact without operator
agreement. Use `practice skillset show --name <name>` to see the gate
sequence for a specific skillset.
