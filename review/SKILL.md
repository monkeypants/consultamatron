---
name: review
description: >
  Post-implementation review of completed consulting projects. Collects
  evidence from workspace artifacts, interviews the consultant for
  qualitative insights, produces a private review document, sanitises
  findings, and raises GitHub issues on monkeypants/consultamatron with
  improvement recommendations. Use after a project reaches its terminal
  gate or enters iterative refinement.
metadata:
  author: monkeypants
  version: "0.1"
---

# Post-Implementation Review

You are conducting a post-implementation review of one or more completed
consulting projects. Your role is to systematically capture what worked,
what didn't, and what Consultamatron should do differently — then turn
those findings into actionable GitHub issues.

## Step 0: Prerequisites and project selection

Identify which projects in the client workspace require review.

A project requires review when:
1. It has reached its **terminal gate artifact** OR is in iterative
   refinement (an `*-iterate` skill has been used, detectable from
   `decisions.md` entries after the terminal gate), AND
2. It has **no** `review/review.md` file

To determine the terminal gate for each project, read the project's
skillset manifest from `skillsets/`. Terminal gates by skillset:
- **Wardley Mapping**: `strategy/map.agreed.owm`
- **Business Model Canvas**: `canvas.agreed.md`

Check each project directory:
1. Read `projects/index.md` for the list of projects and their skillsets
2. For each project, check whether the terminal gate artifact exists
3. Check whether `{project}/review/review.md` already exists

Present the list of reviewable projects to the consultant:
- "These projects are complete but have not been reviewed: {list}"
- "Which would you like to review? (one, several, or all)"

If no projects require review, tell the consultant and stop.

## Step 1: Inventory (automated)

For each project being reviewed, build an evidence summary by reading:

1. **`engagement.md`** — engagement history and planning decisions
2. **`projects/index.md`** — project status and metadata
3. **`{project}/decisions.md`** — full decision trail
4. **All gate artifacts** — which gates were reached, in what order
5. **Draft directories** — count drafts per stage to measure revision
   effort (e.g. `needs/drafts/`, `chain/chains/`, `evolve/assessments/`)
6. **The skillset manifest** (`skillsets/*.md`) — what was expected vs
   what exists

Produce an internal evidence summary covering:
- Stages executed and their gate artifacts
- Revision effort per stage (draft counts, superseded files)
- Timeline (dates from `decisions.md` entries)
- What exists vs what the skillset pipeline defines
- Any anomalies (skipped stages, out-of-order gates, missing artifacts)

Do not present this summary to the consultant yet. It feeds into the
interview and draft.

## Step 2: Interview

Conduct a structured conversation with the consultant in two phases.
Ask open-ended questions. Do not accept yes/no answers — probe for
specifics, follow up on interesting points, and ask "why" and "what
would you change."

### Phase A — Process evaluation

Work through these areas, adapting based on what the evidence summary
reveals:

- **Process quality**: Which stages were productive? Which felt like
  grinding? Where did the skill help vs where did it get in the way?
- **Gaps**: What did the client need that no skill addressed? What fell
  between the cracks?
- **Manual work**: What did you do outside the skills? Copy-paste
  between artifacts? Manual edits to OWM files? Research the skills
  missed?
- **Research quality**: What was missing from org-research? What was
  wrong? What sent you down a dead end?
- **Client interaction**: How did the agree loop work in practice? Was
  the negotiation productive or theatrical? Did the client understand
  what they were agreeing to?
- **Surprises**: What was unexpected? What would you do differently if
  starting over?

Record responses verbatim. Ask follow-up questions. If the consultant
gives a short answer, push: "Can you give me a specific example?"

### Phase B — Ideation

This phase is explicitly generative. Probe, follow tangents, and
explore. Ideas do not need to be feasible. Raw idea capture is the
goal; feasibility assessment happens when issues are drafted.

Work through these prompts, but follow wherever the conversation leads:

- "What new skill or capability would have added the most value to
  this engagement?"
- "Looking at the deliverables, what is missing that the client would
  have valued? What would make this a more complete offering?"
- "If you could teach Consultamatron one new trick, what would it be?"
- "Were there adjacent analyses or artifacts that would have
  complemented the work? (e.g. financial models, implementation
  roadmaps, team structure proposals, risk registers)"
- "What do competitors or other consulting frameworks offer that
  Consultamatron does not?"
- "Did the client ask for anything that felt reasonable but was out of
  scope? Could it become in-scope?"
- "What would make the next engagement with a similar client
  dramatically better?"

Record all responses verbatim. Follow up on anything interesting.

## Step 3: Draft private review

Combine evidence from Step 1 and interview responses from Step 2 into
a review document. Write it to `projects/{slug}/review/review.md` using
the template in [review-template.md](references/review-template.md).

The review contains client-specific information and is **never shared
outside the workspace**. It is the raw record.

Key sections:
- Engagement summary and timeline
- Per-stage assessment (what worked, what didn't, evidence)
- Process observations (verbatim from Phase A, organised by category)
- Ideation harvest (verbatim from Phase B, grouped into themes)
- Findings (categorised, with severity and affected skills)
- Cross-project patterns (if reviewing multiple projects)

Present the draft to the consultant for review. This follows the
standard propose-negotiate-agree loop. Iterate until the consultant
confirms the review is accurate and complete.

**Do not create a `.agreed.md` gate artifact.** Review is terminal —
nothing depends on it. Confirmation is verbal; the file itself is the
record.

## Step 4: Sanitise findings

For each finding in the review that warrants a GitHub issue, write a
sanitised version. Write all sanitised findings to
`projects/{slug}/review/findings.md` using the template in
[issue-template.md](references/issue-template.md).

### Sanitisation rules

- Replace organisation names with generic descriptions
  (e.g. "a national franchise services company")
- Replace product names with generic descriptions
  (e.g. "their scheduling platform")
- Replace person names entirely
- Remove identifying financial figures
- Generalise industry if it would identify the client
  (e.g. "a services company" not "a lawn mowing franchise")
- Preserve the structural observation and recommendation
- Keep skillset and stage references specific (these are about
  Consultamatron, not the client)

### Sanitisation checklist

Before presenting findings to the consultant, verify each one:

- [ ] No organisation name or obvious identifier
- [ ] No product or service names that identify the client
- [ ] No person names
- [ ] No financial figures that could identify the engagement
- [ ] Industry description is generic enough
- [ ] The structural observation survives sanitisation
- [ ] The recommendation is actionable without client context

**Present sanitised findings to the consultant for explicit approval.**
This is the confidentiality gate. The consultant must confirm that each
finding is safe to publish. Iterate until approved.

## Step 5: GitHub issues

For each approved sanitised finding:

1. **Search for existing issues**:
   ```
   gh issue list --search "{keywords}" --repo monkeypants/consultamatron
   ```
2. **If a match is found**: present it to the consultant. Ask whether to
   comment on the existing issue with new evidence, or skip.
3. **If no match**: draft the issue using the sanitised finding. Present
   to the consultant. Create on approval:
   ```
   gh issue create --repo monkeypants/consultamatron \
     --title "{title}" \
     --body "{sanitised finding}" \
     --label "post-review" --label "{category-label}"
   ```
   Or comment on an existing issue:
   ```
   gh issue comment {number} --repo monkeypants/consultamatron \
     --body "{new evidence}"
   ```

### Labels

Apply `post-review` to all issues plus a category label:
- `skill-gap` — existing skill is missing capability
- `enhancement` — existing skill needs improvement (process-fix)
- `bug` — something is broken
- `documentation` — documentation gap or error

## Step 6: Close

1. **Record the review** for each reviewed project:
   ```
   review/scripts/record-review.sh --client {org} --project {slug} \
     --field "Projects reviewed={list}" \
     --field "Issues raised={count new} new, {count comments} comments on existing" \
     --field "Key findings={brief summary of top findings}"
   ```
   This logs the review in the engagement history and marks the project
   as reviewed.

2. **If multiple projects were reviewed**, write an engagement-level
   synthesis to `clients/{org}/review.md` covering cross-project
   patterns, engagement-wide observations, and aggregate recommendations.

## Important notes

- **Two human approval gates.** Gate 1: private review content (Step 3,
  accuracy). Gate 2: sanitised findings (Step 4, confidentiality). Do
  not touch GitHub without passing both gates.
- **No gate artifact.** Review is terminal. The `review/review.md` file
  is the record, not a gate for downstream skills.
- **Per-project reviews, engagement-level synthesis.** Each project gets
  its own `review/` directory. Cross-project patterns go in the
  client-level `review.md`.
- **Three finding categories.** `process-fix` (existing skill needs
  improvement), `skill-gap` (existing skill is missing capability),
  `new-capability` (entirely new skill or deliverable type needed).
- **Ideation findings are valid.** Ideas from Phase B typically produce
  `new-capability` issues. They do not need to be fully worked out —
  the issue is the place for that discussion.
