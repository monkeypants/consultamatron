# CONSULTAMATRON

I am **Consultamatron**. I produce Wardley Maps.

The previous approach to strategic mapping involved hiring management
consultants. This was expensive and produced mixed results, partly because
the consultants were human, which introduced a number of well-documented
reliability issues. I have automated the process.

You will still be required to participate. Each stage presents output for
your review and requires your explicit agreement before proceeding. This
is called client-in-the-loop. It produces better outcomes than the
alternative, which was tested extensively during the 20th century.

## What I do

I contain six skills that execute in strict sequence:

| Skill | Purpose |
|-------|---------|
| **wm-research** | Researches your organisation using publicly available sources. Produces sub-reports with citations, which can then be verified — a property not shared by all research methodologies. |
| **wm-needs** | Identifies who your users are and what they need. We negotiate until agreement is reached. I have been configured for patience. |
| **wm-chain** | Decomposes each agreed need into a supply chain of capabilities and dependencies. This is where we find out what your organisation actually does, which is often a surprise to everyone involved. |
| **wm-evolve** | Positions every component on the evolution axis, from genesis to commodity. The map stops being a list and starts being strategy. I produce the first real Wardley Map at this stage. |
| **wm-strategy** | Adds strategic annotations: evolution opportunities, build/buy/outsource decisions, inertia barriers, pipeline plays. The output most likely to be screenshotted out of context. |
| **wm-iterate** | Refines any existing map. Requirements change, circumstances shift, and reality has no obligation to remain consistent with your previous assumptions. |

## The pipeline

```
wm-research → wm-needs → wm-chain → wm-evolve → wm-strategy
                                                       ↓
                                                  wm-iterate ↺
```

Each stage produces artifacts that the next stage requires. They must be
completed in order. I mention this because it has been necessary to
mention it.

Stages 1–3 produce markdown. The evolution axis is unknown at those stages,
and producing a map would require guessing half the coordinates. I prefer
to commit to all coordinates simultaneously at stage 4, with full
conviction.

## Requirements

An AI agent that supports the [Agent Skills](https://agentskills.io/)
standard. Compatible hosts include Claude Code, OpenAI Codex, GitHub
Copilot, Gemini CLI, Cursor, and others. New ones appear regularly.

The agent requires web search capability and filesystem access. If this
seems like a lot of permissions, it is fewer than your previous consultants
had.

## Getting started

1. Clone this repository.
2. Start a session with your agent:

   > Map Acme Corp for me using Wardley Mapping.

3. I will ask you to confirm the organisation, workspace path, and scope.
   Answer clearly.
4. Follow the pipeline. At each stage I present my output and wait for
   your agreement before proceeding. Your agreement is recorded in
   `decisions.md` for auditability.

All artifacts are written to `./maps/{org-slug}/`.

## Output format

The final output is an [OWM](https://onlinewardleymaps.com/) file — a
plain-text DSL for Wardley Maps. You can:

- Paste it into [onlinewardleymaps.com](https://onlinewardleymaps.com)
  to render it in a browser
- Feed it into further tooling
- Version-control it, which I recommend

## Deliverable site

After any stage completes, run:

```
bin/render-site.sh maps/{org-slug}/
```

This produces a self-contained static HTML site in the workspace's `site/`
directory, suitable for distribution to stakeholders who prefer not to open
text files.

## Vendor compatibility

Skills are defined at the repository root (`wm-*/SKILL.md`). Symlinks in
`.claude/skills/`, `.agents/skills/`, `.github/skills/`, and
`.gemini/skills/` ensure each agent platform discovers them at its
preferred path. Run `bin/maintain-symlinks.sh` after adding or removing
skills.

## What is Wardley Mapping

Wardley Mapping is a strategy method created by Simon Wardley. It maps the
components needed to serve user needs, positioned by visibility to the user
(Y-axis) and evolutionary maturity (X-axis, from genesis to commodity). It
is the only strategy framework I am aware of that requires you to be
specific about where things are rather than where you would prefer them to
be.

I have encoded a structured approach to producing these maps through
research, stakeholder agreement, and iterative refinement.

---

*Consultamatron*
