# Contributing Your Skillset to the Commons

Once you have a personal skillset that works and you want others to use
it, you can contribute it to the Consultamatron commons. This document
explains the process.

## The commons structure

The commons lives under `commons/` in the Consultamatron repository.
Each commons source is an external Git repository containing skillsets:

```
commons/
  monkeypants/
    public-skillsets/
      skillsets/
        wardley_mapping/     (one BC per skillset)
        business_model_canvas/
        ...
```

Your contribution is a new bounded context (BC) directory under a
`skillsets/` directory inside a repository you control.

## Branch progression: alpha → beta → master

Skillset contributions follow a three-stage quality gate:

**Alpha**: your skillset is declared in `commons/` but the CI conformance
tests only warn (not fail) on alpha-stage BCs. Use this stage while the
methodology is still being shaped. Contributors can install and use it
but should expect churn.

**Beta**: conformance tests run at full severity. Your pipelines, skills,
and knowledge packs must all pass doctrine. Use this stage when the
methodology is stable and you are seeking feedback from other operators.

**Master**: the skillset is considered production-quality. Breaking changes
require a major version bump.

You signal the stage by the branch of the hosting repository you reference
(or by a `stage:` field in the skillset metadata if you are in the same repo).

## What conformance tests check

```bash
uv run pytest -m doctrine
```

For a skillset BC, doctrine checks include:

- Every pipeline stage references a real skill (by name, resolvable in the BC)
- Every skill has valid `SKILL.md` frontmatter (name, description, metadata)
- Skill names match their directory names
- No cross-BC imports in Python source
- Knowledge packs are clean (no dirty bytecode)
- No pipeline skills appear in agent directories (use `practice skill link sync`)

Fix all failures before submitting a PR.

## Structuring a PR

1. Fork the `public-skillsets` repository (or the repo that hosts the
   commons skillsets you are targeting)
2. Create a branch: `add-{your-skillset-name}`
3. Add your skillset BC under `skillsets/{your_skillset_slug}/`
4. Add your BC to the `__all__` export in the hosting repository's
   `skillsets/__init__.py`
5. Run `uv run pytest -m doctrine` in the Consultamatron checkout with
   your local commons pointing at your fork
6. Open a PR against the hosting repository's `alpha` branch

Your PR description should include:

- What problem domain the skillset addresses
- Who the target operator is
- Which pipelines are included and what each accomplishes
- Links to any prior art or methodology references

## What review looks like

Reviewers will check:

- Does the problem domain make sense as a separate skillset?
- Is the pipeline structure coherent? (Are these actually distinct actor-goals?)
- Are the skills written for an agent, not a human? (Instructions must be
  specific enough for an LLM to follow without additional context)
- Do the gates make sense? (Can an operator actually produce these artifacts?)
- Is the knowledge pack useful? (Does the pantheon/patterns/references
  content genuinely support the skills?)

Expect iteration. The methodology will improve through use.

## Next steps

- [Collaborating on proprietary skillsets](howto-proprietary-skillsets.md)
- [Hacking on Consultamatron](howto-hacking-consultamatron.md)
