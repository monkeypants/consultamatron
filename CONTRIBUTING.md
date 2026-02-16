# Contributing to Consultamatron

## Contributor Assignment Agreement

All contributions to this project require a signed Contributor
Assignment Agreement (CLA). The agreement is in [CLA.md](CLA.md).

By signing the CLA, you:

1. **Assign copyright** in your contribution to the project maintainer
2. **Attest** that you have the right to make that assignment
3. **Receive back** a perpetual, irrevocable licence to your own
   contribution, so you can continue to use your own code however you
   wish

The project is currently licensed under the GPL (version 3 or later).
The CLA does not restrict the maintainer's licensing choices — as the
copyright owner, the maintainer retains full discretion over how the
codebase is licensed.

## How to sign

When you open your first pull request, the CLA Assistant bot will
prompt you to sign the agreement. You sign by posting a comment in
the pull request with the exact text:

> I have read the CLA document and I hereby sign the Contributor
> Assignment Agreement.

This is recorded against your GitHub username. You only need to sign
once — all future contributions are covered.

### If your employer may own your work

If you are employed and your employer may have rights to intellectual
property you create (common for software developers), you should
either:

- Get written permission from your employer to contribute, or
- Have your employer waive their rights for contributions to this
  project, or
- Have your employer contact the maintainer to execute a separate
  corporate agreement

The CLA requires you to represent that you have handled this. Do not
sign if you are unsure — check with your employer first.

## What this means in practice

**For contributors**: You are giving away ownership of the code you
contribute. In return, you get a licence back to use your own code
for any purpose. The project will always be GPL. Your name remains in
the git history as the author of your contribution.

**For the project**: Consolidated copyright ownership means the
maintainer can enforce the GPL as a single entity, without needing to
coordinate with every contributor. This is the same model the FSF
used for GNU projects for decades.

**What the maintainer can do**: As copyright owner, the maintainer
has unrestricted licensing discretion. The project is currently GPL
but this is a choice, not a constraint. Section 2(d) guarantees your
licence-back regardless of what the maintainer does with the
codebase.

## Code contributions

### Branch workflow

- Fork the repository
- Create a feature branch from `master`
- Make your changes
- Open a pull request against `master`

### Commit style

Linux kernel style:

- Imperative mood: "Add feature" not "Added feature"
- First line is a directive summary (50 chars or less ideal)
- Blank line, then explanatory body if needed
- No conventional commit prefixes (`feat:`, `fix:`, etc.)

### Before submitting

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -m doctrine
```

All three must pass.

## Skill contributions

Skills are agent-native documents (`{skill-name}/SKILL.md`). If you
are contributing a new skill or modifying an existing one:

- Read existing skills to understand the structure and voice
- Follow the YAML frontmatter convention
- Respect the gate protocol — never create `.agreed.md` artifacts
  without describing the client agreement loop
- Test the skill by running it with an agent against a real or
  synthetic client workspace

## Questions

Open an issue if you have questions about the CLA or contribution
process.
