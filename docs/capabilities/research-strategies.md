---
type: capability
name: research-strategies
description: >
  Practice provides research use cases for gathering intelligence about
  a subject. Skillsets supply domain-specific research strategy
  descriptions that shape how information is sourced — whether the
  subject is a client organisation, a methodology domain, a market,
  or a technology landscape.
direction: driven
mechanism: language_port
adapter_contract: >
  A research-strategies.md file (or research-strategies/ knowledge pack)
  in the skill's references/ directory. Each strategy describes: when to
  apply it, what information tasks it prescribes, what the expected
  output structure is. Strategies are named and described so the agent
  can select the appropriate one through negotiation with the operator.
discovery: filesystem_convention
maturity: nascent
hidden_decision: >
  What information a domain needs and how best to source it. The practice
  layer provides the research mechanism (web search, operator mediation,
  structured output). The skillset knows what questions to ask about
  a subject and what answers matter for its methodology.
information_expert: >
  The skillset author. They understand what information the methodology
  requires. org-research needs corporate intelligence; ns-research needs
  academic literature and practitioner guides. Same capability, different
  domain questions.
structural_tests: []
semantic_verification:
  reference_problem: >
    Read the research strategies. Could an agent select the right
    strategy for a typical research subject? Are the strategies
    distinguishable from each other? Do they prescribe concrete
    information-gathering tasks?
  sample_size: 3
  max_tokens_per_evaluation: 1500
  evaluation_criteria:
    - each strategy has a clear applicability condition
    - strategies prescribe concrete tasks, not generic advice
    - strategies are distinguishable (different subjects warrant different strategies)
    - output structure expectations are stated
  trigger: content change in research strategy files
---

# Research Strategies

Research strategies are domain-specific intelligence about *how to learn
about a subject*. The subject might be a client organisation (org-research),
a methodology domain (ns-research), a market, or a technology landscape.
Different domains need different information, and the same domain needs
different approaches for different subject profiles.

## What the practice layer provides

Research use cases that provide the execution mechanism: web search,
structured output (semantic bytecode hierarchy L0-L3), operator-mediated
briefing, and the propose-negotiate-agree loop for strategy selection.

The research skill loads strategies by reference from the skillset's
`references/` directory and presents them to the operator for selection.
The mechanism is the same whether the subject is a Fortune 500 company
or an academic discipline.

## What the skillset supplies

Research strategy descriptions. The consulting BC's `org-research`
currently supplies four named strategies for client research:

1. **Standard research** — subjects with substantive public presence
2. **Market landscape** — stealth-mode or emerging subjects
3. **Recent pivot** — contradictory public information
4. **Operator-mediated briefing** — operator has direct access to subject matter

The skillset engineering BC's `ns-research` would supply different
strategies for methodology research: academic literature review,
practitioner guide survey, tool ecosystem analysis, case study
collection.

Each strategy describes applicability conditions, prescribed tasks, and
expected output structure. The agent selects a strategy through
negotiation with the operator, then executes its tasks.

## Architectural rationale

Research strategies are an Anti-Corruption Layer (Evans). The research
output format (semantic bytecode hierarchy, `resources/index.md` or
equivalent) is the Published Language that downstream skills consume.
But how that research is *gathered* depends on the domain and the
subject — a wardley mapper needs technology landscape intelligence;
a skillset engineer needs academic methodology literature. The research
strategy translates domain requirements into research tasks without
polluting the shared output format.

This is currently the weakest integration point. No discovery mechanism
finds research strategies automatically. No verification confirms they
prescribe actionable tasks. Research skills read the file by hard-coded
reference path. Promotion to established requires at minimum a discovery
convention (e.g. `references/research-strategies.md` as a standard path)
and shape verification.

## References

- [Semantic Packs](../articles/semantic-packs.md) §8 — design-time
  packs in skill references directories
