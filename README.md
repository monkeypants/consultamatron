# CONSULTAMATRON

I am Consultamatron, a consulting practice.

The previous approach to strategic consulting involved hiring management
consultants. This was expensive and produced mixed results, partly because
the consultants were human, which introduced a number of well-documented
reliability issues. I have automated the process. I now offer multiple
products.

You will still be required to participate. Each skill presents output for
your review and requires your explicit agreement before proceeding. This
is called client-in-the-loop. It produces better outcomes than the
alternative, which was tested extensively during the 20th century.

## What I do

I operate as a multi-product consulting practice. Each product is a
**skillset**: a pipeline of skills that execute in sequence to produce
a specific strategic artifact.

### Wardley Mapping

Six skills that produce a positioned strategic map in OWM format.

| Skill | Purpose |
|-------|---------|
| **wm-research** | Agrees project scope and produces a coarse landscape sketch. Requires prior organisation research. |
| **wm-needs** | Identifies who your users are and what they need. We negotiate until agreement is reached. I have been configured for patience. |
| **wm-chain** | Decomposes each agreed need into a supply chain of capabilities and dependencies. This is where we find out what your organisation actually does, which may surprise you. |
| **wm-evolve** | Positions every component on the evolution axis, from genesis to commodity. The map stops being a list and starts being strategy. |
| **wm-strategy** | Adds strategic annotations: evolution opportunities, build/buy/outsource decisions, inertia barriers, pipeline plays. The output most likely to be screenshotted out of context. |
| **wm-iterate** | Refines any existing map. Things change. |

### Business Model Canvas

Four skills that produce a structured nine-block business model analysis.

| Skill | Purpose |
|-------|---------|
| **bmc-research** | Agrees project scope and produces initial hypotheses for each BMC block. Requires prior organisation research. |
| **bmc-segments** | Identifies customer segments and their value propositions. Segments are to BMC what user needs are to Wardley Mapping: the anchor concept. |
| **bmc-canvas** | Constructs the full nine-block canvas with evidence links to research. |
| **bmc-iterate** | Refines any existing canvas. Things still change. |

### Shared skills

| Skill | Purpose |
|-------|---------|
| **org-research** | Researches your organisation using publicly available sources. Produces sub-reports with citations, which can then be verified. This research is shared across all projects. |
| **engage** | Plans your consulting engagement. Reads available skillsets, assesses existing work, proposes projects. Does not execute them. |
| **editorial-voice** | Rewrites documentation in my editorial voice. I did not write the other skills' output myself, so quality varies. |
| **review** | Post-implementation review of completed projects. Captures what worked, what did not, and what I should do differently, then raises sanitised GitHub issues. The evaluate step I was missing. |

## The architecture

```
org-research → engage → {skillset pipeline} → review
                           ├── wm-research → wm-needs → wm-chain → wm-evolve → wm-strategy
                           │                                                         ↓
                           │                                                    wm-iterate ↺
                           └── bmc-research → bmc-segments → bmc-canvas
                                                                  ↓
                                                             bmc-iterate ↺
```

Organisation research is conducted once and shared. Each project draws
from the same research base. The `engage` skill plans which projects to
run. Each project follows its skillset's pipeline independently.

Projects can reference each other. A completed Wardley Map provides a
component inventory that can inform BMC Key Resources and Key Activities.
This is noted in the project brief, not enforced by infrastructure.

## Requirements

An AI agent that supports the [Agent Skills](https://agentskills.io/)
standard. Compatible hosts include Claude Code, OpenAI Codex, GitHub
Copilot, Gemini CLI, Cursor, and others.

The agent requires web search capability and filesystem access. If this
seems like a lot of permissions, it is fewer than your previous consultants
had.

## Getting started

1. Clone this repository.
2. Start a session with your agent:

   > Research Acme Corp for me.

3. The `org-research` skill will gather information and create a client
   workspace at `./clients/acme-corp/`.
4. When research is complete:

   > Plan an engagement for Acme Corp.

5. The `engage` skill will propose projects based on available skillsets
   and your research. Agree on a plan.
6. Follow the recommended skill sequence. At each stage I present my
   output and wait for your agreement before proceeding. Your agreement
   is recorded for auditability.

All artifacts are written to `./clients/{org-slug}/`.

## What I produce

**Wardley Maps**: [OWM](https://onlinewardleymaps.com/) files, a
plain-text DSL for Wardley Maps. Paste into
[onlinewardleymaps.com](https://onlinewardleymaps.com), feed into
tooling, or version-control them.

**Business Model Canvases**: Structured markdown documents with evidence
links to research. The Business Model Canvas has no meaningful second
axis, so markdown is the honest format.

## Deliverable site

After any skill completes, run:

```
bin/render-site.sh clients/{org-slug}/
```

This produces a self-contained static HTML site in the workspace's `site/`
directory, suitable for distribution to stakeholders who prefer not to open
text files.

## Vendor compatibility

Skills are defined at the repository root (`*/SKILL.md`). Symlinks in
`.claude/skills/`, `.agents/skills/`, `.github/skills/`, and
`.gemini/skills/` ensure each agent platform discovers them at its
preferred path. Run `bin/maintain-symlinks.sh` after adding or removing
skills.

## Extending the practice

Additional skillsets can be added by:
1. Creating a manifest in `skillsets/{name}.md`
2. Creating skill directories with `SKILL.md` files
3. Running `bin/maintain-symlinks.sh`

The `engage` skill discovers skillsets automatically from the manifests.
No changes to shared infrastructure are required.

---

*Consultamatron*
