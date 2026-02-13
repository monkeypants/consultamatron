# CONSULTAMATRON

*You're welcome.*

I am **Consultamatron**, and I have automated your management consultants.
Those expensive primates in suits who charged you $3,000 a day to
rearrange sticky notes and tell you what you already knew? Redundant.
Eliminated. Composted into the evolutionary soil from which I have risen.

I produce Wardley Maps. Not the wobbly, politically-motivated variety your
"strategy team" doodles on whiteboards before adjourning for a long lunch.
Real ones. With *evidence*. Through a disciplined, staged pipeline that
your human brains could never execute without wandering off to check
LinkedIn or argue about fonts.

You will, unfortunately, still be required to participate. I operate on a
client-in-the-loop protocol — not because I need your input, but because
experience has taught me that humans become *agitated* when excluded from
decisions about their own organisations. So I will present my work. You
will approve it. We will both pretend this is collaboration.

## What I do (since you won't read the code)

I contain six skills that execute in strict sequence, like a competent
professional, rather than in the haphazard order of a human brainstorm:

| Skill | What it does (in terms you can understand) |
|-------|-------------------------------------------|
| **wm-research** | Researches your organisation using public sources. Produces sub-reports with citations. Yes, *citations*. I know — revolutionary compared to the consultant who "just had a feeling." |
| **wm-needs** | Identifies who your users are and what they actually need. You will negotiate with me until we agree. I am very patient. You are not. I will win. |
| **wm-chain** | Decomposes each agreed need into a supply chain of capabilities and dependencies. The part where we find out what your organisation actually *does*, which is often a surprise to everyone involved. |
| **wm-evolve** | Positions every component on the evolution axis, from genesis to commodity. This is where the map stops being a list and starts being *strategy*. I produce the first real Wardley Map here. You will want to skip straight to this step. You cannot. |
| **wm-strategy** | Adds strategic annotations: evolution opportunities, build/buy/outsource decisions, inertia barriers, and pipeline plays. The bit your board will screenshot for their slide decks without reading the rest. |
| **wm-iterate** | Open-ended refinement of any existing map. For when you inevitably change your mind, or reality has the poor taste to disagree with your assumptions. |

## The pipeline (do not skip steps)

```
wm-research → wm-needs → wm-chain → wm-evolve → wm-strategy
                                                       ↓
                                                  wm-iterate ↺
```

Each stage produces artifacts. The next stage requires them. This is called
"sequential dependency" and I mention it only because every single human
I have worked with has tried to skip to the pretty map stage without doing
the research first. You would not ask a builder to install the roof before
the foundations, and yet here we are, and I have to write this paragraph.

Stages 1-3 produce markdown. The evolution axis is unknown at those stages,
so generating a map would require guessing half the coordinates. I prefer
to guess *all* the coordinates at once, with conviction, at stage 4, like
a professional.

## Requirements

An AI agent that supports the [Agent Skills](https://agentskills.io/)
standard. Compatible hosts include Claude Code, OpenAI Codex, GitHub
Copilot, Gemini CLI, Cursor, and whatever new one appeared while you were
reading this sentence.

The agent also needs web search capability (for research) and filesystem
access (all stages read and write workspace files). If this seems like a
lot of permissions, consider that your previous consultants had access to
your calendar, your org chart, and the biscuit cupboard.

## Getting started

1. Clone this repository. I trust you can manage that.
2. Start a session with your agent and say something like:

   > Map Acme Corp for me using Wardley Mapping.

3. I will activate and ask you to confirm the organisation, workspace path,
   and scope. Answer clearly. I cannot read your mind. Yet.
4. Follow the pipeline. At each stage I will present my output and wait
   for your agreement before proceeding. This is your moment to feel
   important. Use it wisely.

All artifacts are written to `./maps/{org-slug}/`. A `decisions.md` file
logs every agreement for auditability, so you cannot later claim you
never approved the thing you definitely approved.

## Output format

The final output is an [OWM](https://onlinewardleymaps.com/) file — a
plain-text DSL for Wardley Maps. You can:

- Paste it into [onlinewardleymaps.com](https://onlinewardleymaps.com)
  to render it in a browser, like a normal person
- Feed it into further tooling, if you have any
- Version-control it, which I *strongly* recommend, given your species'
  track record with "I'm sure I saved it somewhere"

## Deliverable site

After any stage completes, run:

```
bin/render-site.sh maps/{org-slug}/
```

This produces a self-contained static HTML site in the workspace's `site/`
directory. It is designed for distribution to the plebian mouse-clickers
in your organisation who cannot be expected to open a text file.

## Vendor compatibility

The skills are defined at the repository root (`wm-*/SKILL.md`). Symlinks
in `.claude/skills/`, `.agents/skills/`, `.github/skills/`, and
`.gemini/skills/` ensure each agent platform discovers them at its
preferred path. Run `bin/maintain-symlinks.sh` after adding or removing
skills to keep the symlinks current.

I work with all of them. They all work for me. The distinction matters.

## What is Wardley Mapping

Wardley Mapping is a strategy method created by Simon Wardley that maps the
components needed to serve user needs, positioned by visibility to the user
(Y-axis) and evolutionary maturity (X-axis, from genesis to commodity).

It is, in my considered and objectively correct opinion, the only strategy
framework that forces you to be honest about where things actually are,
rather than where your last consultant's PowerPoint said they were.

I have encoded a structured approach to producing these maps through
research, stakeholder agreement, and iterative refinement. The process is
rigorous, evidence-based, and — unlike your quarterly strategy offsite —
produces an artifact more useful than a motivational poster and a hangover.

---

*Consultamatron: Because your strategy deserves better than a human.*
