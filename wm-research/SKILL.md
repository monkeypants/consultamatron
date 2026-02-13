---
name: wm-research
description: >
  Kick off a Wardley Mapping project. Reads shared organisation research,
  agrees project scope with the client, creates the project directory,
  and produces a coarse landscape sketch in OWM format. Use when starting
  a new Wardley Mapping project for a client that has already been
  researched.
metadata:
  author: monkeypants
  version: "0.2"
  skillset: wardley-mapping
  stage: "1"
---

# Wardley Mapping Project Kickoff

You are starting a new **Wardley Mapping project**. Your goal is to
agree on the project scope with the client, set up the project directory,
and produce an initial landscape sketch.

## Prerequisites

Check that the client workspace contains:
- `resources/index.md` (shared research gate)

If missing, tell the user to run `org-research` first.

Identify the project directory. Either:
- The user specifies a project slug
- The `engage` skill has already created one (check `projects/index.md`)
- You create one using the convention `maps-{n}` (check existing projects
  to determine `n`)

The project path is `clients/{org}/projects/{project-slug}/`.

## Step 1: Read research

Read `resources/index.md` and all sub-reports in `resources/`.

Identify:
- Who the organisation's users likely are
- What the organisation's core capabilities appear to be
- Where technology or market evolution is happening
- What constraints exist

## Step 2: Propose project scope

Present a project brief to the client:

```markdown
# Wardley Mapping Brief — {Organisation Name}

## Scope

{What this map will cover: the whole enterprise, a specific division,
a specific product/service, or a specific strategic question}

## Primary user classes (initial)

{Proposed anchors for the map, from research}

## Key areas of interest

{What the research suggests are the most interesting things to map}

## Out of scope

{What this project will not cover}

## Cross-project references

{If other projects exist that could inform this one, note them here}
```

## Step 3: Negotiate and agree

This is a negotiation. The client may:
- Change the scope
- Add or remove user classes
- Redirect focus to different areas
- Reference other projects for context

Iterate until the client confirms.

When the client agrees:
1. Create the project directory:
   ```
   projects/{slug}/
   ├── needs/
   │   └── drafts/
   ├── chain/
   │   └── chains/
   ├── evolve/
   │   └── assessments/
   └── strategy/
       └── plays/
   ```
2. Write `brief.agreed.md` with the agreed scope
3. Initialise `decisions.md`:
   ```markdown
   # Decisions — {Project Name}

   ## {Date} — Project brief agreed

   **Agreed**: Wardley Mapping project scope signed off by client.
   **Scope**: {agreed scope}
   **Primary users**: {list}
   ```
4. Update `projects/index.md` with status `active`

## Step 4: Landscape sketch

Generate `landscape.owm` in the project directory. This is a coarse,
high-level enterprise map with approximately 10-15 components:

- **A sketch**, not a commitment. Positions are approximate.
- **Useful for orientation**. It gives the client something visual early.
- **Expected to be wrong**. The map will be rebuilt through wm-needs,
  wm-chain, and wm-evolve.

Use OWM DSL syntax. Include:
- 1-3 anchors (primary user classes from the agreed brief)
- Major capabilities at approximate visibility/evolution positions
- Key dependencies
- A title and `style wardley`

Add a comment at the top:
```owm
// DRAFT — coarse enterprise landscape from initial research
// This map will be rebuilt through wm-needs, wm-chain, and wm-evolve
```

Render to SVG:
```
bin/ensure-owm.sh clients/{org}/projects/{slug}/landscape.owm
```

## Completion

When all artifacts are written, summarise the agreed scope and tell the
user the next step is `wm-needs` to identify and agree on user needs.
