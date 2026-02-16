# Evolution Characteristics

Reference for assessing component evolution stage. Based on Simon Wardley's
evolution characteristics from Chapter 7 of "Wardley Maps."

## The Four Stages

### I. Genesis (0.00 - 0.17)

| Property | Characteristic |
|----------|---------------|
| Ubiquity | Rare, only a few know about it |
| Certainty | Poorly understood, unpredictable |
| Publication | Normally unpublished, tacit knowledge |
| Market | Undefined, no market exists yet |
| Knowledge | Concept, exploration |
| User perception | Surprising, unexpected, "wow" |
| Failure | High rate of failure expected |
| Focus | Exploration, experimentation |
| Appropriate method | Agile, lean startup, prototyping |

### II. Custom-Built (0.17 - 0.40)

| Property | Characteristic |
|----------|---------------|
| Ubiquity | Slowly increasing awareness |
| Certainty | Rapid increase in learning |
| Publication | Emerging publications, conferences |
| Market | Forming, early adopters |
| Knowledge | Hypothesis, divergent approaches |
| User perception | Leading edge, competitive advantage |
| Failure | Moderate, learning from failures |
| Focus | Learning, differentiation |
| Appropriate method | Agile, feature teams |

### III. Product (+rental) (0.40 - 0.70)

| Property | Characteristic |
|----------|---------------|
| Ubiquity | Increasingly common |
| Certainty | Well-defined, predictable features |
| Publication | Multiple competing publications |
| Market | Growing, multiple vendors/providers |
| Knowledge | Theory converging, best practices |
| User perception | Useful, expected, "table stakes" |
| Failure | Understood, failure modes documented |
| Focus | Operationalise, scale |
| Appropriate method | Six Sigma, lean |

### IV. Commodity (+utility) (0.70 - 1.00)

| Property | Characteristic |
|----------|---------------|
| Ubiquity | Widespread, used by almost everyone |
| Certainty | Well understood, predictable |
| Publication | Mature reference material |
| Market | Mature, standardised, few dominant providers |
| Knowledge | Accepted, modelled, taught in universities |
| User perception | Invisible, expected to "just work" |
| Failure | Rare, outages are newsworthy |
| Focus | Efficiency, cost reduction |
| Appropriate method | Outsource, utility billing |

## Assessment Questions

For each component, ask:

1. **How many people/organisations use this?** (Ubiquity)
   - Few → Genesis. Most → Commodity.

2. **How well understood is it?** (Certainty)
   - Poorly → Genesis. Well-defined → Product/Commodity.

3. **Can you buy it off the shelf?** (Market)
   - No → Genesis/Custom. Multiple vendors → Product. Utility pricing → Commodity.

4. **Is it a competitive differentiator?** (User perception)
   - Yes → Custom/early Product. No → late Product/Commodity.

5. **Are there published standards or best practices?** (Publication)
   - None → Genesis. Industry standards → Product/Commodity.

6. **Is there resistance to change (inertia)?** (Inertia)
   - Mark with `inertia` in OWM. Common at Custom→Product and Product→Commodity boundaries.

## Inertia Signals

Inertia indicates resistance to a component's natural evolution.
Common sources:

- **Existing capital investment**: "We just built this in-house"
- **Skills and training**: "Our team specialises in this"
- **Supplier lock-in**: "Our contract runs until 2028"
- **Regulatory requirements**: "Regulations mandate this approach"
- **Cultural attachment**: "This is how we've always done it"
- **Political**: "This is {person}'s project"

Mark components with inertia in the OWM file when you identify these signals.

## Common Mistakes

- **Overestimating evolution**: Just because your organisation uses it
  doesn't mean the market has commoditised it. Look at the industry,
  not just one company.
- **Confusing internal maturity with market maturity**: A company might
  have a mature internal system for something the market considers
  custom-built.
- **Ignoring the supply side**: A component might feel like a product
  to users but still be custom-built internally.
- **Anchoring on current state**: Consider where the component is
  moving, not just where it is. Evolution is continuous.
