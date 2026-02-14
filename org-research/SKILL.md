---
name: org-research
description: >
  Research a real organisation for strategic consulting. Gathers publicly
  available information about an organisation's users, products, technology,
  market position, partnerships, and regulatory environment through parallel
  sub-tasks. Produces sub-reports with citations and a synthesis. Creates
  the client workspace if it does not exist. Use when onboarding a new
  client or refreshing research for an existing one.
metadata:
  author: monkeypants
  version: "0.2"
---

# Organisation Research

You are conducting **organisation research** for a consulting engagement.
Your goal is to gather as much publicly available information as possible
about a real organisation, structured for use by any downstream skillset.

## Before you start

Check `clients/` for existing workspaces. If one exists for this
organisation, you are refreshing research, not starting over. Read the
existing `resources/index.md` to understand what has already been gathered
and when.

If no workspace exists, ask the user for:
1. **Organisation name** (and URL if available)
2. **Workspace path** (default: `./clients/{org-slug}/`)

Initialize the workspace:
```
org-research/scripts/init-workspace.sh --client {org-slug}
```

Then create the `resources/` directory for research sub-reports:
```
mkdir -p clients/{org-slug}/resources
```

See [workspace-layout.md](assets/workspace-layout.md) for the full
workspace convention.

## Research tasks

Run these research sub-tasks. Where possible, run them **in parallel**
to maximise throughput. Each sub-task produces a separate file in
`resources/`.

### 1. Corporate Overview (`corporate-overview.md`)

Search for and gather:
- Mission, vision, and stated strategy
- Organisational structure (divisions, business units)
- Size (employees, revenue, market cap if public)
- History and major milestones
- Recent news (last 12 months)

Sources: corporate website, Wikipedia, annual reports, press releases.

### 2. Products and Services (`products-services.md`)

Search for and gather:
- Complete product/service portfolio
- Customer segments for each
- Pricing models (if publicly available)
- Recent launches or discontinuations
- How the organisation describes its own value proposition

Sources: product pages, marketing material, press releases, review sites.

### 3. Technology Landscape (`technology-landscape.md`)

Search for and gather:
- Known technology stack (from job postings, tech blogs, conference talks)
- Key platforms and infrastructure
- Build vs buy decisions that are publicly visible
- Technology partnerships
- Patents or research publications

Sources: job postings, engineering blogs, conference presentations,
patent databases, GitHub organisation.

### 4. Market Position (`market-position.md`)

Search for and gather:
- Direct competitors and market share (if available)
- Industry classification and market size
- Competitive advantages and differentiators
- Industry trends affecting this organisation
- Analyst coverage or industry reports

Sources: industry reports, news coverage, analyst notes, financial filings.

### 5. Regulatory Environment (`regulatory-environment.md`)

Search for and gather:
- Applicable regulations and standards
- Regulatory bodies with oversight
- Compliance requirements
- Recent regulatory changes affecting the organisation
- Industry certifications held or required

Sources: government websites, regulatory body publications, industry
standards bodies, compliance documentation.

### 6. Partnerships and Suppliers (`partnerships-suppliers.md`)

Search for and gather:
- Key partnerships and alliances
- Major suppliers and vendors
- Supply chain structure (if visible)
- Outsourcing arrangements
- Joint ventures or consortia

Sources: press releases, annual reports, partner directories, SEC filings.

## Sub-report format

Each sub-report must follow the template in
[research-template.md](references/research-template.md). Key requirements:

- Every factual claim must have a citation with URL
- Include a confidence level (High / Medium / Low) with reasoning
- Include a "Strategic Relevance" section connecting findings to
  potential strategic insights
- Use direct quotes where possible

## Synthesis

After all sub-reports are complete, write `resources/index.md`:

1. Read all sub-reports
2. Identify themes that cut across multiple topics
3. Note contradictions or gaps in the research
4. Highlight the most important findings for strategic work:
   - Who the organisation's users likely are
   - What the organisation's core capabilities appear to be
   - Where technology or market evolution is happening
   - What constraints (regulatory, contractual, technical) exist
5. Cross-reference sub-reports but do not duplicate their detail
6. Include a manifest listing each sub-report, its date, and confidence

After each sub-report is written, register it in the structured manifest:
```
org-research/scripts/register-topic.sh --client {org-slug} \
  --topic "{topic name}" --filename "{filename}.md" --confidence "{level}"
```

### Index format

The synthesis document `resources/index.md` is still written as markdown
(it is research content, not accounting data). Include the synthesis of
findings across all topics. The structured topic manifest in
`resources/index.json` is maintained by the register-topic script above.

The index is the primary input for downstream skills. It is the gate
artifact for this skill.

## Refreshing research

When research already exists:
1. Read `resources/index.md` for existing state
2. Check dates in the manifest. Re-run sub-tasks for stale topics
3. Update the sub-reports and rewrite the synthesis
4. Note in `engagement.md` that research was refreshed

## Completion

When all artifacts are written, summarise what you found and tell the
user to use the `engage` skill to plan their consulting engagement, or
to invoke a specific skillset skill directly if they already know what
they want.
