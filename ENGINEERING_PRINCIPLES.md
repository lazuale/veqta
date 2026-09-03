# VEQTA Engineering Principles

Status: **foundation baseline candidate**

## 1. Purpose

This document defines the engineering discipline shared by VEQTA Engineering, Learn, Labs and Products.

It does not replace the detailed Frappe Architecture Standard. It defines the rules that determine how VEQTA approaches architecture and implementation across the ecosystem.

## 2. Frappe is the platform

Frappe Framework is the technological foundation.

VEQTA does not introduce a mandatory architectural layer between Frappe and every product.

The default relationship is:

```text
Frappe Framework
       ↓
independent VEQTA product App
```

Not:

```text
Frappe Framework
       ↓
VEQTA Core Framework
       ↓
VEQTA product
```

A shared runtime dependency may only be introduced later if real products prove that they share a stable responsibility that cannot reasonably remain independent.

## 3. Native-mechanism-first rule

For every requirement:

```text
requirement
    ↓
what responsibility exists?
    ↓
which native Frappe mechanism owns that responsibility?
    ↓
does its semantics match?
    ├── yes → use it
    └── no  → use an official extension point if suitable
                    ↓
          introduce custom architecture only when justified
```

Custom code is not a defect. Unnecessary duplication of framework responsibility is.

## 4. App boundary rule

A production product should normally be an independent Frappe App.

The App owns its product-specific:

- DocTypes and controllers;
- hooks and integrations;
- fixtures and patches when required;
- tests;
- product modules and reports;
- release lifecycle.

A Site remains a deployment/runtime instance and must not become the only source of product configuration.

## 5. No universal VEQTA domain model

VEQTA is an ecosystem, not one application domain.

Therefore there is no universal `Work Item`, `Customer`, `Asset`, `Case` or other business entity that every VEQTA Product must inherit from.

A common business abstraction is introduced only when multiple real products independently prove the same stable semantic responsibility and the coupling cost is lower than duplication.

## 6. Evidence hierarchy

Technical decisions should be grounded in the strongest relevant evidence available:

1. official Frappe documentation for the target version;
2. Frappe source code for the target version;
3. Frappe release notes / migration guidance;
4. official ecosystem documentation where applicable;
5. implementations in official Frappe applications where they are relevant examples;
6. VEQTA experiments and product evidence;
7. VEQTA architectural conclusions.

A VEQTA conclusion must never be presented as an official Frappe guarantee.

## 7. Version awareness

All significant architecture guidance must have an explicit Frappe version baseline.

Version-sensitive mechanisms must be marked when guidance depends on behavior introduced, removed or changed in a particular release.

The aim is not to freeze VEQTA to one Frappe version. The aim is to make compatibility visible and testable.

## 8. Reproducibility

Accepted product and Lab state must be reproducible from version-controlled artifacts.

The target property is:

```text
compatible clean Frappe environment
+ repository
+ documented install / migrate process
= accepted application state
```

Manual configuration on a development Site that cannot be reproduced from Git is not considered complete engineering delivery.

## 9. Data-model discipline

Before introducing a DocType, field or relationship, identify its responsibility and lifecycle.

Do not create new entities only because a noun exists in a requirement.

Use the Frappe data model according to semantics:

- independent identity → candidate standalone DocType;
- composition owned by one parent → candidate Child DocType;
- small stable choice → consider `Select` before a separate dictionary;
- one Site-wide configuration object → candidate Single DocType;
- relationship to existing document → use `Link` when semantics fit.

Detailed rules belong to the Frappe Architecture Standard.

## 10. Lifecycle discipline

Do not introduce `Workflow`, submit/cancel behavior, custom state machines or separate status entities merely because a document has states.

First identify:

- what state means;
- who may transition it;
- whether transition history matters;
- whether state changes carry irreversible business meaning;
- whether native Document or Workflow semantics match.

## 11. Permissions are architecture

Permissions are not a final UI configuration step.

Product design must explicitly account for:

- role model;
- document-level access;
- ownership / assignment where relevant;
- server-side enforcement;
- privileged code paths;
- integration identities.

Client-side hiding is not an authorization boundary.

## 12. UI follows model

Use Desk, standard views, Reports, Workspaces, Web Forms and other native surfaces when their semantics fit the user problem.

A custom frontend is legitimate when the product experience genuinely requires one. It must not be introduced only to make the product look less like Frappe.

UX quality matters, but architecture is not sacrificed to visual differentiation.

## 13. Integration discipline

Integrations must have explicit contracts.

For every external integration define:

- source of truth;
- authentication model;
- data ownership;
- idempotency expectations;
- retry behavior;
- failure visibility;
- transaction boundary;
- versioning / compatibility assumptions.

Do not create hidden synchronization dependencies between products by convenience.

## 14. Testing discipline

Tests should protect responsibilities and invariants, not only implementation details.

At minimum, important product behavior should be testable for:

- server-side validation;
- permissions;
- lifecycle transitions;
- migration / fixture reproducibility where applicable;
- integration boundaries;
- regressions discovered in Labs or production.

A Lab may initially use explicit manual PASS/FAIL experiments, but a graduated Product must convert stable critical behavior into automated tests where practical.

## 15. Shared-code extraction rule

Do not create shared VEQTA libraries speculatively.

A candidate shared component requires evidence of all of the following:

1. at least two independent consumers have the same responsibility;
2. the semantics are genuinely the same, not merely similar code;
3. the interface can be kept stable independently of either product;
4. centralizing it reduces total complexity;
5. the dependency does not create an unnecessary release bottleneck.

Until then, duplication may be cheaper and safer than premature coupling.

## 16. Architecture decision record

A significant deviation from the Frappe-native default should record:

```text
Context
Frappe mechanism considered
Why it is insufficient
Chosen extension / custom mechanism
Trade-offs
Evidence
Compatibility impact
Test strategy
```

The goal is not bureaucracy. The goal is to prevent accidental platform reimplementation.

## 17. Learn / Lab / Product separation

### Learn

May simplify the problem scope, but may not teach an architecture known to be wrong merely because it is easier to explain.

### Labs

May contain disposable code and explicit hypotheses. Experimental shortcuts must be marked and cannot silently become production architecture.

### Products

Must meet reproducibility, maintenance, testing and release expectations appropriate to production software.

## 18. Upgrade principle

Prefer extension over fork and public contracts over patching framework internals.

Every dependency on undocumented internal behavior creates an upgrade liability and must be treated as such.

## 19. Engineering review question

Before accepting a design, the reviewer must be able to answer:

> Which responsibility belongs to Frappe, which responsibility belongs to this App, and what evidence justifies the boundary?

If that boundary cannot be explained, the design is not ready.