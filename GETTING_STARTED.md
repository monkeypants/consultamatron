# Getting Started

You are a human who has decided to operate a consulting practice with a
robot. This document explains how to set up your working environment.

## Prerequisites

- **Git** and a **GitHub** account
- An AI agent that supports the [Agent Skills](https://agentskills.io/)
  standard (Claude Code, OpenAI Codex, GitHub Copilot, Gemini CLI,
  Cursor, or similar)
- The agent requires web search capability and filesystem access

## Step 1: Clone the practice

```bash
git clone https://github.com/monkeypants/consultamatron.git
cd consultamatron
```

This gives you the commons: the open consulting methodology, all
generic skillsets, and the engagement lifecycle. It is the horizontal
bar of your T-shaped capability — the breadth that every operator
shares.

## Step 2: Set up your client workspace

Your client engagement artifacts — research, maps, canvases, decision
trails — live in `clients/`. This directory is `.gitignored` by the
consultamatron repository so your client work never leaks into the
public commons.

Create a private repository for your client workspaces and clone it
into the `clients/` directory:

```bash
# Create a private repo on GitHub (or your preferred host)
gh repo create my-consultamatron-clients --private

# Clone it into the gitignored clients/ directory
git clone git@github.com:you/my-consultamatron-clients.git clients
```

Your client workspaces are now versioned, backed up, and private.
When you run `org-research` or any engagement skill, artifacts are
written into `clients/` and you commit them to your private repo at
your own pace.

## Step 3: Set up your personal vault

Your personal vault is a private repository for your proprietary
skillsets, techniques, and accumulated engagement insights. It is the
vertical bar of your T-shape — the depth that makes you uniquely
valuable.

```bash
# Create a private repo for your personal vault
gh repo create my-consultamatron-vault --private

# Clone it into the gitignored partnerships/ directory
git clone git@github.com:you/my-consultamatron-vault.git partnerships/my-vault
```

The vault starts empty. Over time it accumulates:

- **Proprietary skillsets** — domain expertise encoded as
  Consultamatron skills, in `skillsets/` and `skills/`
- **Resources** — industry knowledge, frameworks, templates, and
  benchmarks that your skills draw on, in `resources/`
- **De-cliented review findings** — lessons from engagements with
  client identity removed, in `reviews/`
- **Cross-engagement patterns** — synthesised insights across your
  body of work, in `reviews/patterns.md`

See below for the partnership workspace structure.

## Step 4: Configure partnership repositories (optional)

Partnerships are shared collections of proprietary skillsets. They
might be:

- An **organisation** you work with that has its own domain expertise
  and methods
- A **collaborative group** of operators pooling complementary skills
  for joint engagements
- An **industry vertical** community maintaining shared benchmarks and
  frameworks

Each partnership is a private git repository cloned into
`partnerships/`:

```bash
# Clone a partnership repo you've been given access to
git clone git@github.com:some-org/consultamatron-partnership.git partnerships/some-org
```

You can have as many partnerships as you need:

```
partnerships/
├── my-vault/           # your personal vault (Step 3)
├── acme-corp/          # organisational partnership
└── strategy-guild/     # collaborative group
```

Each partnership contributes proprietary skills that enhance the
commons methodology for engagements where that domain applies. The
`engage` skill discovers all partnership skillsets automatically and
asks which ones are relevant to each engagement.

## Step 5: Start working

You are ready. Start a session with your agent:

> Research Acme Corp for me.

The `org-research` skill gathers public information about the
organisation and creates a client workspace at `clients/acme-corp/`.

When research is complete:

> Plan an engagement for Acme Corp.

The `engage` skill reads available skillsets — both commons and any
partnerships you have configured — and proposes projects. If
partnerships are present, it asks which are relevant and plans
partnership skill injection points alongside the commons pipeline.

Follow the recommended skill sequence. At each stage, the agent
presents output and waits for your agreement before proceeding.

## What you have

After setup, your working directory looks like this:

```
consultamatron/                       # commons (public repo)
├── skillsets/                        # commons skillset manifests
├── {skill-name}/SKILL.md             # commons skills
├── clients/                          # gitignored, your private repo
│   ├── .git/
│   └── {org-slug}/                   # one workspace per client
└── partnerships/                     # gitignored, one or more private repos
    ├── {your-vault}/                 # your personal vault
    │   ├── .git/
    │   ├── skillsets/                # your proprietary skillset manifests
    │   ├── resources/                # your domain knowledge
    │   ├── skills/
    │   │   └── {skill}/SKILL.md      # your proprietary skills
    │   └── reviews/                  # de-cliented engagement findings
    └── {partnership}/                # shared partnership
        ├── .git/
        ├── skillsets/
        ├── resources/
        ├── skills/
        │   └── {skill}/SKILL.md
        └── reviews/
```

The consultamatron repo provides methodology. Your private repos
provide content and context. The three layers — commons, partnerships,
personal vault — form your T-shaped capability.

## The engagement lifecycle

```
                     Commons pipeline
                     ─────────────────
org-research → engage → Plan
                           ↓
                        Partner-1  (enrichment: "what else can we do?")
                           ↓
                        Execute    (commons + partnership skills)
                           ↓
                        Synthesise
                           ↓
                        Partner-2  (enhancement: "how can we make this better?")
                           ↓
                        Deliver
                           ↓
                        Partner-3  (finishing: "how do we make this land?")
                           ↓
                        review → findings route to:
                                   → client stays (private)
                                   → your vault (de-cliented)
                                   → partnership repo (de-cliented)
                                   → commons GitHub (fully sanitised)
```

If no partnerships are configured, the Partner stages are skipped and
the pipeline matches the commons-only flow.

## Keeping up to date

```bash
# Pull commons updates
cd consultamatron && git pull

# Pull partnership updates
cd partnerships/some-org && git pull

# Your client workspace is yours to commit and push as you see fit
cd clients && git add -A && git commit -m "Progress on acme-corp maps-1"
```

Commons updates never touch your `clients/` or `partnerships/`
directories. Partnership updates never touch your client work. The
three layers are independent.

## Repository granularity

A single private repository for all clients is the recommended
starting point. As your practice grows, you may prefer finer-grained
separation:

- **Per-client repos**: useful when collaborators should see one
  client's workspace but not others, or when client contracts require
  isolated storage
- **Per-engagement repos**: for engagements with specific security or
  data residency requirements
- **Unversioned `clients/`**: some operators keep `clients/` as a
  plain local directory with no git repo, relying on the structured
  data files as the record of truth

The `partnerships/` directory supports the same granularity choices.
Start simple; split when you have a reason to.
