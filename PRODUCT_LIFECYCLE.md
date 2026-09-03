# VEQTA Product Lifecycle

Status: **foundation baseline candidate**

## 1. Purpose

This lifecycle prevents experiments, teaching examples and unfinished applications from being presented as products merely because code exists.

The lifecycle is:

```text
Problem
  ↓
Lab
  ↓
Reference
  ↓
Incubating Product
  ↓
Product
  ↓
Maintain / Evolve / Retire
```

Not every initiative must reach the final stage.

## 2. Stage 0 — Problem

A product direction starts with a real problem, not with a desired technology feature or brand slot.

Minimum record:

- target user or team;
- problem being solved;
- current workaround / alternative;
- why the problem matters;
- what evidence would disprove the opportunity.

No product name is required at this stage.

Examples of invalid starting points:

- "we need a CRM product because the ecosystem should have one";
- "we should use Workflow in a product";
- "we need something like ERPNext".

## 3. Stage 1 — Lab

A Lab validates uncertain assumptions.

A Lab must define:

- hypothesis;
- scope;
- Frappe mechanisms being evaluated;
- experiment procedure;
- PASS / FAIL criteria;
- known shortcuts;
- expected evidence output.

A Lab may use a disposable app/site and may contain temporary code.

A Lab must be visibly marked experimental.

### Lab exits

A Lab ends in one or more outcomes:

```text
FAIL       → hypothesis rejected / knowledge retained
LEARN      → useful educational material
ENGINEERING→ evidence updates architecture guidance
REFERENCE  → implementation worth preserving as an example
INCUBATE   → validated product opportunity
```

Keeping a Lab indefinitely without an explicit outcome is not a lifecycle state.

## 4. Stage 2 — Reference

A Reference is a preserved implementation demonstrating an accepted pattern or decision.

It is not necessarily a user-facing product.

Reference criteria:

- purpose is explicit;
- architecture is explained;
- setup is reproducible;
- unsupported shortcuts are removed or documented;
- compatibility baseline is stated;
- tests exist for the behavior the reference claims to demonstrate, where practical.

References may live in VEQTA Labs or Engineering depending on their purpose.

## 5. Stage 3 — Incubating Product

A candidate becomes an Incubating Product only when it has both technical and product evidence.

### Required product evidence

- clearly defined user;
- clearly defined problem;
- coherent minimum product scope;
- reason the solution deserves to exist independently;
- expected alternative products / workflows acknowledged;
- initial adoption or validation plan.

### Required engineering evidence

- product boundary is defined;
- Frappe App boundary is defined;
- critical data model has passed architecture review;
- no unexplained framework duplication exists;
- install / migration path is reproducible;
- permission model is explicit;
- test strategy is defined;
- compatibility baseline is explicit.

### Repository rule

An Incubating Product should move to its own repository once it becomes a real independently installable Frappe App rather than a Lab artifact.

At this stage it may receive a provisional product name.

## 6. Stage 4 — Product

A Product is an independent maintained application intended for real users.

Minimum graduation gate:

### Product

- value proposition is understandable without VEQTA internal context;
- audience and supported use cases are explicit;
- unsupported / non-goals are explicit;
- versioning and release status are visible.

### Architecture

- App installs cleanly on supported Frappe baseline;
- migrations are reproducible;
- critical server-side invariants are tested;
- permissions are tested;
- important upgrade-sensitive extensions are documented;
- no Lab-only manual configuration is required.

### Operations

- installation path is documented;
- upgrade path is documented;
- backup / migration expectations are documented where product-specific;
- failure modes of integrations or background jobs are observable.

### Open source

- repository is public unless a temporary security exception is documented;
- software license is explicit;
- contribution path is explicit;
- security reporting path exists before significant adoption.

### Experience

- onboarding has a deliberate path;
- empty states and primary workflows are understandable;
- custom UI exists only where justified;
- product branding does not misrepresent experimental features as stable.

## 7. Stage 5 — Maintain / Evolve

A maintained Product has an explicit support matrix.

Changes are classified as:

```text
product capability
architecture / platform adaptation
bug / regression
security
compatibility / Frappe upgrade
migration
experience improvement
```

New major hypotheses should return to a Lab when they create significant architectural uncertainty rather than being tested directly on production architecture.

## 8. Retirement

Open source does not mean eternal maintenance.

A Product or Lab may be retired when:

- the problem is no longer relevant;
- a better solution makes continued development unjustified;
- maintenance burden exceeds value;
- architecture depends on unsupported platform behavior;
- no responsible maintainer remains.

Retirement must be explicit:

- mark repository/status clearly;
- state last supported versions;
- preserve history when useful;
- do not leave users assuming active maintenance.

## 9. Promotion is evidence-based

Movement between stages is a decision, not a rename.

The following are not sufficient evidence of product maturity:

- having a logo;
- having a GitHub repository;
- having many DocTypes;
- having a working demo;
- being used in a course;
- having a large README;
- being technically interesting.

## 10. Product naming gate

Permanent product naming and visual identity should occur after the Incubating Product gate, not at the initial Lab stage.

This prevents brand investment from creating pressure to preserve a failed technical hypothesis.

## 11. Relationship to Learn

Learn may use Labs and Products as examples, but educational sequencing must not drive the Product roadmap.

Likewise, a Product feature must not be added merely because it would make a convenient lesson.

## 12. Relationship to Engineering

Labs and Products are evidence producers.

When they reveal a conflict with current VEQTA Engineering guidance, the conflict is recorded and reviewed. The product may demonstrate a valid exception; Engineering then documents the boundary rather than pretending the original rule was universal.

## 13. Current migration

The existing `Work Type` / `Work Item` prototype is reclassified as:

```text
VEQTA Labs / Work Management / v0.1
```

It is no longer treated as the domain model of VEQTA itself.

Its next outcome must be decided by Lab evidence:

```text
reject
reference
learn
incubate
```

No product status is assumed in advance.