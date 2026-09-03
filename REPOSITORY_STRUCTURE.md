# VEQTA Repository Structure

Status: **foundation baseline candidate**

## 1. Purpose

This document defines how VEQTA source, engineering knowledge, learning materials, experiments and production products are separated in Git.

The goal is to avoid two failure modes:

1. one repository becoming an undifferentiated dump of unrelated artifacts;
2. premature fragmentation into many repositories before boundaries are real.

## 2. Current phase: ecosystem hub repository

At the current stage, `lazuale/veqta` remains the ecosystem hub and source of truth for foundation, engineering knowledge, learning materials and Labs.

Target structure:

```text
veqta/
│
├── README.md
├── PROJECT_CHARTER.md
├── BRAND_ARCHITECTURE.md
├── ENGINEERING_PRINCIPLES.md
├── PRODUCT_LIFECYCLE.md
├── REPOSITORY_STRUCTURE.md
│
├── engineering/
│   ├── README.md
│   └── frappe/
│       ├── README.md
│       ├── 01_FOUNDATIONS.md
│       ├── 02_DATA_MODEL.md
│       ├── ...
│       └── EVIDENCE_REGISTER.md
│
├── learn/
│   ├── README.md
│   └── courses/
│       └── frappe-core/
│           ├── README.md
│           ├── ARCHITECTURE_PASSPORT.md
│           ├── REQUIREMENTS_MATRIX.md
│           ├── PRACTICUM_ROADMAP.md
│           └── ...
│
├── labs/
│   ├── README.md
│   └── work-management/
│       └── v0.1/
│           ├── MODEL.md
│           ├── PROTOTYPE.md
│           ├── DECISIONS.md
│           ├── DEVELOPMENT.md
│           └── SETUP.md
│
├── products/
│   └── README.md
│
└── brand/
    ├── README.md
    ├── PRINCIPLES.md
    └── NAMING.md
```

Not every empty directory should be created immediately. Directories appear when they contain a real artifact.

## 3. Why `docs/` is removed as the main taxonomy

`docs/` is too generic for the new model because it currently mixes fundamentally different responsibilities:

- product/prototype model documentation;
- architecture standards;
- training materials;
- setup instructions.

The new top-level taxonomy communicates responsibility directly:

```text
engineering → accepted engineering knowledge
learn       → education
labs        → experiments
products    → product catalogue / links
brand       → identity system
```

Documentation may still exist inside any of these domains, but `docs` is no longer the primary business architecture of the repository.

## 4. Migration map from current repository

```text
docs/frappe-architecture-standard/
    → engineering/frappe/

docs/frappe-training/
    → learn/courses/frappe-core/

docs/MODEL_V0_1.md
    → labs/work-management/v0.1/MODEL.md

docs/PROTOTYPE_V0_1.md
    → labs/work-management/v0.1/PROTOTYPE.md

docs/DECISIONS.md
    → labs/work-management/v0.1/DECISIONS.md

docs/DEVELOPMENT.md
    → labs/work-management/v0.1/DEVELOPMENT.md

docs/START_HERE_WSL2.md
    → labs/work-management/v0.1/SETUP.md
    or a later general developer setup document if its scope proves broader
```

The content should be reviewed during migration rather than moved mechanically when old wording defines VEQTA as a single product.

## 5. Root README responsibility

The root `README.md` is the public landing page of the ecosystem.

It must answer, in order:

1. What is VEQTA?
2. What is its relationship to Frappe?
3. What are Engineering, Learn, Labs and Products?
4. What is currently usable?
5. Where should a new visitor start?
6. What is experimental versus production-ready?

It must not use one current Lab as the definition of VEQTA.

## 6. Engineering structure

`engineering/` contains accepted or actively maintained engineering guidance.

The current Frappe Architecture Standard belongs under:

```text
engineering/frappe/
```

A future structure may include additional engineering concerns only when they become real:

```text
engineering/
├── frappe/
├── decisions/
├── compatibility/
└── references/
```

Do not create categories in anticipation of content.

## 7. Learn structure

`learn/` contains educational artifacts.

Courses are independent learning units:

```text
learn/courses/<course-slug>/
```

A course may contain specification, roadmap, exercises, solutions, code references and evaluation material, but its educational code must not be confused with production Product code.

Learning paths may later combine courses without physically duplicating them.

## 8. Labs structure

Each Lab has an explicit scope and status:

```text
labs/<lab-name>/<version-or-experiment>/
```

A Lab README or primary document should state:

- hypothesis;
- status;
- Frappe baseline;
- expected outcome;
- whether code is disposable, reference-quality or incubation candidate.

When a Lab graduates into a standalone Product, product code moves to an independent repository. Lab evidence can remain in the hub as historical/reference material.

## 9. Products structure in the hub

`products/` is initially a catalogue and governance area, not a monorepo for all product source code.

Example future catalogue:

```text
products/README.md

Product A → github.com/<owner>/<product-a>
Product B → github.com/<owner>/<product-b>
```

This keeps the ecosystem discoverable while preserving Frappe App independence.

## 10. When a Product gets its own repository

A Product should be extracted when:

- it is an independently installable Frappe App;
- it has its own issue/release lifecycle;
- it has its own user-facing documentation;
- it can be versioned independently from VEQTA Engineering and Learn;
- its source no longer exists mainly to support a Lab experiment.

Repository extraction should happen by the Incubating Product stage or earlier if independent installation already matters.

## 11. Future organization model

If VEQTA grows beyond a personal repository namespace, the preferred mature model is a dedicated GitHub organization.

Possible shape:

```text
github.com/<veqta-org>/
│
├── veqta              # ecosystem hub / foundation
├── <product-a>        # production Frappe App
├── <product-b>        # production Frappe App
└── <shared-library>   # only after shared-code extraction criteria are proven
```

Engineering and Learn may remain in the hub while the project is compact. They should be split into separate repositories only when independent release/contribution workflows create a real benefit.

Repository count is not a maturity metric.

## 12. Repository naming

Repository names should reflect actual responsibility.

Avoid vague names such as:

```text
veqta-core
veqta-common
veqta-utils
veqta-platform
```

unless the responsibility and consumer set have already been proven.

Product repositories should use the product's real technical/package identity rather than a generic ecosystem term.

## 13. Source of truth

Each artifact has one primary source of truth:

```text
Foundation policy   → ecosystem hub
Engineering guidance→ ecosystem hub / engineering
Learning material   → ecosystem hub / learn
Lab evidence        → ecosystem hub / labs
Product source      → product repository
```

Do not maintain competing canonical copies across Learn, Labs and Product repositories.

## 14. Migration order

The repository should be migrated in this order:

```text
1. accept foundation documents
2. rewrite root README
3. create real target directories
4. move Engineering
5. move Learn
6. reclassify current prototype as Lab
7. repair all internal links
8. audit old terminology
9. only then remove obsolete paths
```

This order preserves a readable repository throughout the migration.

## 15. Definition of done for the reorganization

The repository reorganization is complete when:

- root README no longer defines VEQTA as one application;
- every maintained artifact is classified as Engineering, Learn, Lab, Product or foundation/brand governance;
- no current path implies that Learn or Engineering are temporary additions to a single product;
- the Work Management prototype is visibly a Lab;
- internal links resolve after migration;
- no duplicate source of truth remains;
- future production App code has a documented extraction path.