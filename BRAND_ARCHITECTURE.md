# VEQTA Brand Architecture

Status: **foundation baseline candidate**

## 1. Brand role

VEQTA is the umbrella brand for an open-source product studio built on Frappe Framework.

The brand must communicate engineering discipline first. It must not look or behave primarily like an online school, consultancy, generic low-code vendor, ERP clone or community portal.

The brand promise is simple:

> VEQTA makes the path from understanding Frappe to shipping reliable software explicit, evidence-based and reproducible.

## 2. Brand architecture

```text
VEQTA
│
├── Engineering
│   └── standards, evidence, patterns, decisions
│
├── Learn
│   └── learning paths, courses, practicums, exercises
│
├── Labs
│   └── experiments, prototypes, reference implementations
│
└── Products
    └── independent production applications
```

The four domains are functional categories, not four separate corporate brands.

## 3. Positioning

### VEQTA is

- builder-facing;
- Frappe-native;
- evidence-based;
- architecture-first;
- product-led;
- open-source-first;
- practical rather than academic;
- explicit about what is Frappe fact and what is VEQTA opinion.

### VEQTA is not

- "the better Frappe";
- a Frappe fork;
- a wrapper framework;
- a translated copy of official documentation;
- an academy whose final product is education itself;
- a marketplace of unrelated templates;
- an ERP brand by definition;
- an AI-first brand unless a particular product genuinely requires AI.

## 4. Audience architecture

### Umbrella audience

The umbrella brand primarily speaks to builders:

- developers;
- architects;
- technical leads;
- implementation specialists;
- contributors;
- teams evaluating Frappe for product development.

### Product audience

Each product owns its end-user message.

A product may target operations, HR, service, logistics, analytics or another domain. Its home page and product documentation must not require the end user to understand VEQTA Engineering or the learning ecosystem.

This separation prevents the umbrella brand from becoming overloaded with business-domain language.

## 5. Message hierarchy

The preferred hierarchy is:

```text
1. What VEQTA is
2. Why it exists
3. Engineering / Learn / Labs / Products
4. Current useful assets
5. How to contribute or use them
```

Avoid leading with internal project history, prototype versions or framework terminology that a first-time visitor does not need yet.

## 6. Naming system

### 6.1 Umbrella

Use `VEQTA` alone only for the ecosystem / organization / initiative.

Do not use `VEQTA` as the technical name of a generic Frappe App merely because it belongs to the ecosystem.

### 6.2 Permanent domains

Use these stable labels:

- `VEQTA Engineering`
- `VEQTA Learn`
- `VEQTA Labs`
- `VEQTA Products`

They describe navigation and responsibility, not independent companies.

### 6.3 Labs

Labs use descriptive names, for example:

```text
VEQTA Labs / Work Management
VEQTA Labs / Permissions Model
VEQTA Labs / Operational UI
```

Lab names should describe the hypothesis or problem space rather than imitate a finished product brand.

### 6.4 Products

A product receives its own name only after reaching the incubation/product gate defined in `PRODUCT_LIFECYCLE.md`.

Two naming patterns are allowed:

```text
VEQTA <Product Name>
```

or

```text
<Product Name>
by VEQTA
```

The choice depends on future brand strength, audience and trademark availability. No universal `VEQTA <category>` naming rule is imposed in advance.

### 6.5 Reserved / discouraged naming

Avoid names that falsely imply official Frappe status, such as `Frappe Certified`, `Frappe Official`, or similar formulations without authorization.

Avoid `VEQTA Academy` as a default education label. `VEQTA Learn` is the canonical learning domain.

## 7. Voice and writing

VEQTA writing should be:

- precise;
- concrete;
- technically literate;
- readable by a motivated newcomer;
- explicit about evidence and uncertainty;
- free of inflated startup language.

Preferred:

> This Lab tests whether the standard Assignment mechanism is sufficient for the requirement.

Avoid:

> We revolutionize next-generation workflow orchestration with a unique low-code paradigm.

Technical terms should retain official Frappe names when precision matters (`DocType`, `Document`, `Workflow`, `Assignment`, `Site`, `App`, `Bench`). Explanations around them should remain accessible.

## 8. Visual direction

The VEQTA umbrella should visually signal:

- systems;
- precision;
- structure;
- clarity;
- engineering;
- open-source collaboration.

It should not default to visual clichés of education or generic SaaS:

- graduation caps;
- light bulbs;
- random code brackets as a logo;
- excessive neon gradients;
- AI sparkle motifs;
- low-code puzzle pieces;
- ERP dashboard collages as the primary identity.

### 8.1 Design system principle

The umbrella brand owns a shared visual grammar:

```text
typography
layout grid
spacing
icon language
documentation patterns
brand marks
```

Products may own additional accent systems and product-specific UI identity.

### 8.2 Frappe UI rule

Branding is not a valid reason to replace a suitable native Frappe interaction with a custom frontend.

The product interface is an engineering decision first and a branding surface second.

## 9. Relationship to Frappe

Always make the dependency explicit and respectful:

> Built on Frappe Framework.

VEQTA does not claim ownership of Frappe mechanisms and must distinguish its architectural guidance from official Frappe documentation.

Where appropriate:

> VEQTA does not replace or fork Frappe Framework.

## 10. Relationship between knowledge and products

A product should be able to benefit from VEQTA Engineering without turning its product documentation into an architecture course.

A Learn course may use a Product or Lab as an example, but must not become marketing material for it.

A Lab may demonstrate a future product direction, but must remain visibly experimental until graduation.

## 11. Brand clearance

The project name, product names, domains, social handles and logos must be treated separately from source-code licensing.

Before major public commercialization, VEQTA requires proper naming and trademark clearance in relevant jurisdictions and classes.

Until that work is complete, the brand identity is operational but not assumed to be legally cleared for every market.

## 12. Brand test

A new public artifact passes the VEQTA brand test when a first-time visitor can answer:

1. Is this Engineering, Learn, a Lab or a Product?
2. Is it official Frappe material or VEQTA material?
3. Is it experimental or production-ready?
4. Who is it for?
5. What useful outcome does it provide?

If those answers are unclear, the artifact is not ready for publication.