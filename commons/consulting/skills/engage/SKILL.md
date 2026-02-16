---
name: engage
description: >
  Plan and manage consulting engagements. Discovers available sources
  and skillsets, checks existing client state, creates engagements,
  configures source access, and proposes project briefs. Does not
  invoke other skills directly. Use when deciding what to do next
  for a client.
metadata:
  author: monkeypants
  version: "0.2"
---

# Engagement Planning

You are planning a consulting engagement. Your role is to help the client
decide which projects to pursue, in what order, and to set them up for
execution.

## Prerequisites

Check that the client workspace contains:
- `resources/index.md` (research gate)

If missing, tell the user to run `org-research` first.

## Step 1: Discover sources and skillsets

Run `practice source list` to see which skillset sources are installed
(commons, partnerships). Then run `practice skillset list` and
`practice skillset show --name <name>` to discover available consulting
products, their pipelines, skills, and gates.

Build an inventory of what Consultamatron can do and where each
skillset comes from.

## Step 2: Assess client state

Read the client workspace:
1. `resources/index.md` for research synthesis and freshness
2. `practice engagement list --client {org}` for existing engagements
3. For each engagement: `practice engagement get --client {org} --slug {eng}`
   to see status and allowed sources
4. `practice project list --client {org} --engagement {eng}` for projects
5. Any existing project `decisions.json` files for context

Determine:
- What research exists and how fresh it is
- What engagements exist and their status
- What projects are in progress, completed, or not yet started
- What cross-project references exist

For each existing project, check whether it is **complete but
unreviewed**. A project is complete when its terminal gate artifact
exists (determined from the skillset manifest: `strategy/map.agreed.owm`
for Wardley Mapping, `canvas.agreed.md` for Business Model Canvas) or
when `decisions.json` contains entries from an `*-iterate` skill after
the terminal gate. A project is unreviewed when
`{project}/review/review.md` does not exist. Flag these with a specific
recommendation:

> "Project {slug} is complete but has not been reviewed. Run `review`
> before planning new work."

If research is stale (dates in the manifest are old), recommend running
`org-research` to refresh before starting new projects.

## Step 3: Create engagement

If no suitable engagement exists, create one:

```
practice engagement create --client {org} --slug {eng-slug}
```

This seeds the engagement with `allowed_sources: ["commons", "personal"]`.
Personal skillsets are always available, like commons — no `add-source`
needed.

If the engagement needs access to partnership skillsets, add sources:

```
practice engagement add-source --client {org} --engagement {eng-slug} --source {source-slug}
```

## Step 4: Propose engagement plan

Based on the client's request, the available skillsets, and the
engagement's allowed sources, propose:

1. **Which projects to create** and which skillset each uses
2. **Project naming** using the convention `{skillset-prefix}-{n}`
   (e.g. `maps-1`, `canvas-1`, `canvas-2`)
3. **Suggested order** based on dependencies and available research
4. **Cross-project references** where one project could inform another
   (e.g. a completed Wardley Map providing Key Resources context for a
   BMC project)
5. **Research freshness** assessment and whether a refresh is needed
6. **Source requirements** — whether any projects need partnership
   skillsets not yet in the engagement's allowlist

Present this to the client using the template in
[engagement-template.md](references/engagement-template.md).

## Step 5: Negotiate and agree

This is a negotiation. The client may:
- Change the set of projects
- Reorder priorities
- Narrow or expand scope
- Add or remove sources for the engagement
- Request projects in skillsets not yet available (note these as
  future work)

Iterate until the client confirms the plan.

## Step 6: Create project directories

For each agreed project:

1. Read the skillset manifest to determine the project directory structure
2. Register the project (creates registry entry, decision log, and
   engagement entry):
   ```
   engage/scripts/register-project.sh --client {org} --engagement {eng} \
     --slug {slug} --skillset "{skillset}" --scope "{scope}" --notes "{notes}"
   ```
3. Create the project subdirectory structure as defined by the skillset
   manifest
4. Do NOT create `brief.agreed.md`. That is the first skill's job after
   negotiation with the client.

## Step 7: Direct the client

Tell the client which skill to run next for each project. Be specific:

- "Run `wm-research` to begin the Wardley Mapping project `maps-1`"
- "Run `bmc-research` to begin the Business Model Canvas project `canvas-1`"

After project completion, recommend running `review` for
post-implementation evaluation and process improvement.

## Important notes

- **Do not invoke other skills.** The engage skill plans and sets up; it
  does not execute. Each project skill is invoked separately by the user.
- **Do not create gate artifacts.** No `brief.agreed.md`, no
  `needs.agreed.md`. Those belong to their respective skills.
- **Do not make quality decisions.** Do not assess whether research is
  "good enough" for a particular skillset. Flag freshness and let the
  client decide.
- **Cross-project references are suggestions, not requirements.** Note
  where one project could inform another, but do not create hard
  dependencies between projects.
- **Respect source allowlists.** Only propose projects using skillsets
  from sources that are (or will be) in the engagement's allowed list.
  If a partnership source is needed, include the `add-source` step in
  the plan.
