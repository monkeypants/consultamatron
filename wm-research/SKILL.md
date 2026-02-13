---
name: wm-research
description: >
  Research a real organisation for Wardley Mapping. Gathers publicly
  available information about an organisation's users, products, technology,
  market position, partnerships, and regulatory environment through parallel
  sub-tasks. Produces sub-reports with citations, a synthesis, and a coarse
  enterprise landscape map in OWM format. Use when starting a new Wardley
  mapping engagement or when asked to research an organisation for mapping.
metadata:
  author: monkeypants
  version: "0.1"
  methodology: wardley-mapping
  stage: "1"
---

# Organisation Research for Wardley Mapping

You are conducting the **research phase** of a Wardley mapping engagement.
Your goal is to gather as much publicly available information as possible
about a real organisation, structured for subsequent mapping stages.

## Before you start

Ask the user for:
1. **Organisation name** (and URL if available)
2. **Workspace path** (default: `./maps/{org-slug}/`)
3. **Scope** — the whole enterprise, a specific division, or a specific
   product/service? (default: whole enterprise)

Create the workspace directory structure:
```
{workspace}/
├── 1-research/
│   └── tasks/
├── 2-needs/
│   └── drafts/
├── 3-chain/
│   └── chains/
├── 4-evolve/
│   └── assessments/
├── 5-strategy/
│   └── plays/
└── decisions.md
```

See [workspace-layout.md](assets/workspace-layout.md) for the full
workspace convention.

## Research tasks

Run these research sub-tasks. Where possible, run them **in parallel**
to maximise throughput. Each sub-task produces a separate file in
`1-research/tasks/`.

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
- Include a "Relevance to Mapping" section connecting findings to
  potential users, needs, capabilities, or evolution signals
- Use direct quotes where possible

## Synthesis

After all sub-reports are complete, write `1-research/summary.md`:

1. Read all sub-reports
2. Identify themes that cut across multiple topics
3. Note contradictions or gaps in the research
4. Highlight the most important findings for mapping:
   - Who the organisation's users likely are
   - What the organisation's core capabilities appear to be
   - Where technology or market evolution is happening
   - What constraints (regulatory, contractual, technical) exist
5. Cross-reference sub-reports — do not duplicate their detail

The summary should be 1-3 pages. It is the primary input for the next
stage (wm-needs).

## Landscape map

Generate `1-research/landscape.owm` — a coarse, high-level enterprise
map with approximately 10-15 components. This map is:

- **A sketch**, not a commitment. Positions are approximate.
- **Useful for orientation** — it gives the client something visual early.
- **Expected to be wrong** — the map will be rebuilt properly in stages 3-5.

Use OWM DSL syntax. Include:
- 1-3 anchors (primary user classes)
- Major capabilities at approximate visibility/evolution positions
- Key dependencies
- A title and `style wardley`

Add a comment at the top:
```owm
// DRAFT — coarse enterprise landscape from initial research
// This map will be rebuilt through the wm-needs, wm-chain, and wm-evolve stages
```

## Completion

When all artifacts are written, summarise what you found and tell the
user the next step is `wm-needs` to identify and agree on user needs.
