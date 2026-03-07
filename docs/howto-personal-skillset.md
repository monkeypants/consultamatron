# Creating Your First Personal Skillset

The personal vault is your safe space. Skills and skillsets you create
there are yours — they are gitignored by the commons repository and
won't affect anyone else until you choose to contribute them.

## What you're building

A skillset is a consulting methodology packaged for machine use. It lives
in a bounded context directory and declares:

- What it is and who it helps (`__init__.py` metadata)
- One or more **pipelines** — sequences of skills for distinct actor-goals
- The skills themselves — methodology steps with agent instructions

## Step 1: Scaffold a new skillset

```bash
practice skillset add --name my-methodology
```

This creates `personal/my_methodology/` with:

```
personal/my_methodology/
  __init__.py           BC metadata (name, description, pipelines)
  skills/               pipeline skill directories
  docs/                 knowledge packs for this methodology
```

The scaffold emits a `SKILLSET` comment block in `__init__.py` that
documents what you need to fill in.

## Step 2: Define your pipelines

Open `personal/my_methodology/__init__.py`. You will see:

```python
PIPELINES = [
    Pipeline(
        slug="create",
        actor_goal="...",
        stages=[
            PipelineStage(order=1, skill="my-skill-1", description="...", gate="..."),
        ],
    ),
]
```

Fill in the `actor_goal` (what does the operator accomplish?), the stages
(what skills are needed, in what order?), and the gate artifact for each
stage (what does the operator produce that proves the stage is done?).

A pipeline is one use case — one thing the operator wants to accomplish
with this methodology. If you have multiple distinct use cases (create,
iterate, analyse), declare multiple pipelines.

## Step 3: Write your first skill

```bash
mkdir personal/my_methodology/skills/my-first-skill
```

Create `personal/my_methodology/skills/my-first-skill/SKILL.md`:

```markdown
---
name: my-first-skill
description: What this skill does in one sentence.
metadata:
  author: your-name
  version: "0.1"
  freedom: medium
  skillset: my-methodology
  stage: "1"
---

# My First Skill

[Agent instructions go here. Tell the agent what to do, what output
to produce, and what the gate artifact looks like.]
```

The `skillset` and `stage` fields mark this as a pipeline skill — it
belongs to your methodology and will never be auto-linked into agent
directories. It is served by the CLI.

## Step 4: Verify conformance

```bash
uv run pytest -m doctrine
```

This checks that your pipeline stages refer to real skills, that skill
names match their directory names, and that your BC metadata is valid.
Fix any failures before moving on.

## Step 5: Test it

Register a project using your skillset:

```bash
practice project init --client test-client
practice engagement create --client test-client --slug test-1
practice project register \
  --client test-client \
  --engagement test-1 \
  --slug first-test \
  --skillset my-methodology \
  --scope "Testing my new methodology"
```

Then advance through the pipeline:

```bash
practice engagement next --client test-client --engagement test-1
```

The CLI will tell you which pipeline and which stage to run next.

## Generic vs pipeline skills

If you want a skill that is always in the agent's context (not part of
a methodology pipeline), create it in `personal/skills/` with no
`skillset:` in its metadata:

```
personal/skills/my-generic-skill/SKILL.md
```

Then sync the agent directories:

```bash
practice skill link sync
```

The skill will appear as a symlink in `.agents/skills/`, `.claude/skills/`,
and so on.

## Next steps

- [Contributing your skillset to the commons](howto-contribute-to-commons.md)
