# OWM DSL Reference

Open Wardley Map DSL syntax, compatible with
[Online Wardley Maps](https://onlinewardleymaps.com) and
[cli-owm](https://github.com/monkeypants/cli-owm).

## Coordinate System

All positions use `[visibility, maturity]` (Y, X):

- **Visibility (Y)**: 0.0 (bottom, invisible) to 1.0 (top, visible to user)
- **Maturity (X)**: 0.0 (Genesis, left) to 1.0 (Commodity, right)

## Comments

```owm
// Single-line comment
/* Multi-line comment */
component Foo [0.5, 0.5]  // Inline comment
```

## Map Metadata

```owm
title My Strategic Map
style wardley                 // plain, wardley, handwritten, colour, dark
size [800, 600]               // Canvas pixels, default 500x600
evolution Genesis->Custom->Product->Commodity
```

Evolution label variants:
- Activities: `Genesis -> Custom-Built -> Product (+rental) -> Commodity (+utility)`
- Practices: `Novel -> Emerging -> Good -> Best`
- Data: `Unmodelled -> Divergent -> Convergent -> Modelled`
- Knowledge: `Concept -> Hypothesis -> Theory -> Accepted`

## Anchors

Anchors are users/stakeholders at the top of the value chain.

```owm
anchor Customer [0.95, 0.58]
anchor Regulator [0.92, 0.20]
```

Typically placed at visibility 0.90-0.97.

## Components

```owm
component Name [visibility, maturity]
component Name [0.70, 0.45] label [-100, 4]       // Label offset in pixels
component Name [0.55, 0.80] inertia                // Resistance to change
component Name [0.60, 0.30] (build)                // Execution strategy
component Name [0.48, 0.65] (buy)
component Name [0.35, 0.82] (outsource)
component Name [0.50, 0.50] (market)               // Market designation
component Name [0.40, 0.60] (ecosystem)
component Name [0.55, 0.50] (market, outsource)    // Combined decorators
```

## Dependencies (Value Chain Links)

```owm
Customer->Product
Product->Capability
Capability->Sub-component
Product->Capability; context annotation        // Annotated link
```

## Flow Links

```owm
A+>B                          // Forward flow
A+<B                          // Reverse flow
A+<>B                         // Bidirectional flow
A+'data'>B                    // Labelled forward
A+'money'<B                   // Labelled reverse
A+'info'<>B                   // Labelled bidirectional
A+>B; context annotation      // Flow with annotation
```

## Evolution (Movement Arrows)

```owm
evolve Component 0.72                              // Move to maturity 0.72
evolve OldName->NewName 0.55                       // Evolve and rename
evolve Component 0.60 (buy)                        // Evolve with strategy change
evolve Component 0.65 label [10, -20]              // Evolve with label offset
evolve OldName->NewName 0.78 (market, buy) label [5, -20]  // Combined
```

Default target maturity when omitted: 0.85.

## Pipelines

A single capability containing variants at different evolution stages.

```owm
pipeline Component Name
{
  component Variant A [0.18]          // Only maturity, inherits visibility
  component Variant B [0.45]
  component Variant C [0.72]
}
```

Pipeline children specify only maturity (single value). You can link
directly to pipeline children:

```owm
Customer->Variant C; primary
Customer->Variant B; legacy
```

## Standalone Market and Ecosystem

```owm
market Fuel Market [0.35, 0.85] inertia
ecosystem Partner Network [0.30, 0.75]
```

## Standalone Execution Strategy

```owm
build Component Name
buy Component Name
outsource Component Name
```

## Notes

```owm
note Important observation [0.62, 0.12]
note +Highlighted note [0.88, 0.08]          // + prefix for emphasis
```

## Annotations

Numbered callouts with a legend. **Keep each annotation under 12 words**
so it fits on one line in the rendered legend.

```owm
annotation 1 [0.68, 0.28] This is a key insight
annotation 2 [[0.70, 0.27],[0.56, 0.52]] Relationship between these points
annotations [0.90, 0.03]                    // Legend position
```

## Submaps and URLs

```owm
submap Detail Area [0.82, 0.28] url(detail)
url detail [https://onlinewardleymaps.com/#clone:abc123]
```

## Pioneers, Settlers, Town Planners

```owm
pioneers [0.90, 0.00, 0.75, 0.25]          // Bounding box [y1, x1, y2, x2]
settlers [0.75, 0.25, 0.55, 0.55]
townplanners [0.55, 0.55, 0.35, 0.95]
```

## Accelerators and Decelerators

```owm
accelerator Market Force [0.78, 0.65]
deaccelerator Regulatory Barrier [0.72, 0.38]
```

## Complete Example

```owm
title Lair Canteen

anchor Mandatory Fun Committee [0.95, 0.63]
anchor Disposable Henchmen [0.95, 0.78]

component Bowl of Minestrone [0.79, 0.61] label [-110, 4]
component Bowl [0.73, 0.78]
component Minestrone Recipe [0.63, 0.81]
component Hot Broth [0.52, 0.80]
component Seawater [0.38, 0.82]
component Volcanic Cauldron [0.43, 0.35] label [-100, 4]

evolve Volcanic Cauldron->Geothermal Tap 0.62 label [16, 5]

component Lava Vent [0.1, 0.7] label [-48, 20]
evolve Lava Vent 0.89 label [-12, 21]

Mandatory Fun Committee->Bowl of Minestrone
Disposable Henchmen->Bowl of Minestrone
Bowl of Minestrone->Bowl
Bowl of Minestrone->Minestrone Recipe
Bowl of Minestrone->Hot Broth
Hot Broth->Seawater
Hot Broth->Volcanic Cauldron; limited by
Volcanic Cauldron->Lava Vent

annotation 1 [[0.43,0.49],[0.08,0.79]] Standardising lava vents allows Cauldrons to evolve faster
annotation 2 [0.48, 0.85] Hot broth is obvious and well known
annotations [0.72, 0.03]

note +recipe is classified -- see NDA section 7 [0.23, 0.33]

style wardley
```

## Positioning Guidelines

| Visibility | Typical components |
|------------|-------------------|
| 0.90-0.97 | Anchors (users/stakeholders) |
| 0.80-0.90 | User-visible needs and services |
| 0.60-0.80 | Business capabilities |
| 0.40-0.60 | Supporting components |
| 0.10-0.40 | Infrastructure, raw materials |

| Maturity | Stage | Characteristics |
|----------|-------|-----------------|
| 0.00-0.17 | Genesis | Novel, uncertain, experimentation |
| 0.17-0.40 | Custom | Understood but bespoke, emerging practice |
| 0.40-0.70 | Product | Standardised, multiple suppliers, best practice |
| 0.70-1.00 | Commodity | Utility, mature, cost of doing business |
