# VEQTA Project Charter

Status: **foundation baseline candidate**  
Scope: VEQTA as an open-source initiative built around Frappe Framework

## 1. Definition

VEQTA is an **architecture-first open-source product studio and ecosystem for Frappe Framework**.

VEQTA exists to connect four activities that are usually separated:

1. understanding how Frappe is designed to be used;
2. teaching that engineering model in a reproducible way;
3. testing uncertain decisions in isolated experiments;
4. turning mature solutions into independent production applications.

VEQTA is not a Frappe App, a replacement for Frappe Framework, a fork of Frappe, or a generic collection of tutorials.

## 2. Mission

Build useful open-source software on Frappe while making the engineering path from framework knowledge to production implementation explicit, verifiable and teachable.

The long-term result is not one universal application. It is a coherent family of engineering knowledge, learning materials, experiments and independent products that share the same engineering discipline.

## 3. Strategic model

```text
Frappe Framework
       │
       ▼
VEQTA Engineering
       │
       ├──────────────┐
       ▼              ▼
VEQTA Learn       VEQTA Labs
       │              │
       └──────┬───────┘
              ▼
       VEQTA Products
              │
              ▼
users · contributors · services · community
```

The ecosystem is an outcome of useful engineering assets and useful products. Community size is not treated as a substitute for product value.

## 4. Four permanent domains

### 4.1 VEQTA Engineering

The engineering knowledge layer.

It defines how VEQTA evaluates architecture on Frappe, records evidence, separates Frappe facts from VEQTA conclusions, documents patterns and anti-patterns, and maintains compatibility guidance.

Its core asset is the Frappe Architecture Standard.

### 4.2 VEQTA Learn

The educational layer.

It converts accepted engineering knowledge into structured learning paths, courses, practicums and exercises. It teaches decision-making and responsibility ownership, not a catalogue of framework features.

Learn consumes Engineering. A convenient lesson is never a reason to weaken an engineering rule.

### 4.3 VEQTA Labs

The experimental layer.

Labs are isolated, explicitly temporary environments for validating architectural, product or UX hypotheses. A Lab may produce a reference implementation, invalidate an idea, feed evidence back into Engineering, become material for Learn, or graduate into product incubation.

A Lab is not a production product and must never be presented as one.

### 4.4 VEQTA Products

The production layer.

Products solve real user problems. A production product built on Frappe is an independent Frappe App with its own scope, repository, release lifecycle, documentation and product identity.

VEQTA itself does not need its own DocTypes or runtime package.

## 5. Primary audience

The VEQTA umbrella brand is primarily builder-facing:

- Frappe developers and future Frappe developers;
- software and solution architects;
- technical leads;
- independent builders;
- implementation teams;
- open-source contributors.

Individual products address their own end users and must be understandable without requiring those users to understand the whole VEQTA ecosystem.

## 6. Non-goals

VEQTA does not aim to:

- replace official Frappe documentation;
- create a parallel framework over Frappe;
- create a mandatory `veqta_core` dependency for all products;
- reproduce ERPNext under another name;
- build courses merely to demonstrate every Frappe feature;
- keep failed experiments alive for branding reasons;
- turn branding or visual identity into a justification for custom technical architecture;
- force unrelated products into one domain model;
- define community growth as the main success criterion.

## 7. Engineering authority

The order of authority for technical claims is:

```text
official Frappe documentation / source / releases
                    ↓
             VEQTA Engineering
             ↙       ↓       ↘
          Learn     Labs    Products
```

Engineering may contain VEQTA architectural conclusions, but they must be identified as conclusions rather than represented as official Frappe rules.

Labs and Products can generate evidence that causes Engineering to be revised. They do not silently override it.

## 8. Product-led rule

VEQTA must produce useful software, not only knowledge about software.

Engineering and Learn are first-class outputs, but the strategic direction requires a path toward independent production products. No artificial deadline or invented product category is required; product candidates must emerge from validated problems and evidence.

## 9. Open-source rule

VEQTA follows an open-source-first product model.

The default strategic model is not "open core" where essential product capabilities are deliberately withheld from the open-source application. Sustainable commercial activity may later exist around hosting, support, implementation, consulting, education or other services.

Exact software, content and trademark licensing is defined separately and may differ by artifact type.

## 10. Brand rule

VEQTA is an umbrella identity, not the default name of every application.

Products may use a VEQTA-endorsed name or a standalone product name, but each production product must have its own identity, audience and value proposition.

The current VEQTA name is treated as a working brand until formal trademark and naming clearance is complete.

## 11. Decision rules

The following decisions require an explicit change to this Charter rather than an informal convention:

- redefining VEQTA as a single application;
- introducing a mandatory VEQTA runtime/framework layer between Frappe and products;
- merging Learn, Labs and Products into one undifferentiated development area;
- changing the open-source product strategy to open-core;
- making one product domain the universal domain model of VEQTA;
- changing the four-domain architecture of Engineering, Learn, Labs and Products.

## 12. Foundation documents

This Charter is interpreted together with:

- [`BRAND_ARCHITECTURE.md`](BRAND_ARCHITECTURE.md)
- [`ENGINEERING_PRINCIPLES.md`](ENGINEERING_PRINCIPLES.md)
- [`PRODUCT_LIFECYCLE.md`](PRODUCT_LIFECYCLE.md)
- [`REPOSITORY_STRUCTURE.md`](REPOSITORY_STRUCTURE.md)

If these documents conflict, `PROJECT_CHARTER.md` has priority until the conflict is resolved explicitly.

## 13. Baseline test

Any future initiative using the VEQTA name must be classifiable without ambiguity as one of:

```text
Engineering artifact
Learning artifact
Lab artifact
Product artifact
Ecosystem / governance support
```

If it cannot be classified, its place in VEQTA has not been designed yet and it must not be added by convention.