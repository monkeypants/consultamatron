# Getting Started with Consultamatron

What is this? Who is it for? And what are the moving parts?

## What Consultamatron is

Consultamatron is an open consulting practice platform. It combines:

- A **semantic knowledge base** (how to consult, structured as machine-readable packs)
- A **CLI** (`practice`) that surfaces that knowledge at the right moment
- A set of **skills** that give AI agents the methodology context they need

An operator uses Consultamatron to run consulting engagements with an AI
agent co-pilot. The agent knows *how* to do the work (from the skills and
knowledge packs); the operator knows *which* client and *what* problem.

## Key concepts

**Operator**: you. The human running the consulting practice. You own the
engagement, maintain the client relationship, and decide which methodology
to use. The agent assists.

**Skillset**: a consulting methodology packaged for machine use. Examples:
Wardley Mapping, Business Model Canvas, Skillset Engineering. Each skillset
defines a set of *pipelines* (actor-goal use cases) and *skills* (how to
execute each step).

**Skill**: one methodology step. A skill has a `SKILL.md` that tells the
agent what to do, what gates to check, and what output to produce. Skills
have a type:

- **Generic** — always in the agent's global context (e.g. `/review`, `/idea`)
- **Pipeline** — accessed through the CLI narrow waist only (e.g. `wm-research`)

**Pipeline**: a sequence of skills that accomplishes one actor-goal. For
example, the Wardley Mapping `create` pipeline walks you from research to
a positioned map. The `analyse` pipeline takes a completed map and extracts
strategic insights. These are separate use cases, not stages of the same one.

**Engagement**: a scoped consulting assignment for one client. It registers
which skillset(s) are in play and tracks where you are in each pipeline.

## Where things live

```
consultamatron/
  skills/               generic skills (always in agent context)
  docs/                 platform knowledge pack (articles, HOWTO pages)
  src/practice/         core domain entities and protocols
  bin/cli/              CLI implementation
  commons/              public skillset sources (commons/org/repo/skillsets/)
  personal/             your private skills and skillsets (gitignored)
  partnerships/         proprietary skillset sources (gitignored)
  clients/              client workspaces (gitignored)
```

## The generic/pipeline distinction

Generic skills are always available. They are the control surface commands
you use throughout an engagement: `/idea`, `/review`, `/engage`. They don't
belong to any methodology — they are how you operate the tool.

Pipeline skills belong to a skillset. You don't invoke them directly; the
CLI tells the agent which one to run at the current pipeline stage. This
is how the platform keeps methodology knowledge structured and navigable.

To keep agent directories current, run:

```bash
practice skill link sync
```

## Next steps

- [Creating your first personal skillset](howto-personal-skillset.md)
- [Contributing your skillset to the commons](howto-contribute-to-commons.md)
- [Hacking on Consultamatron](howto-hacking-consultamatron.md)
