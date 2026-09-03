# VEQTA Foundation Audit

Status: **review record**  
Scope: `PROJECT_CHARTER.md`, `BRAND_ARCHITECTURE.md`, `ENGINEERING_PRINCIPLES.md`, `PRODUCT_LIFECYCLE.md`, `REPOSITORY_STRUCTURE.md`, root `README.md`

## Verdict

**PASS WITH FOLLOW-UP WORK.**

The proposed foundation is internally coherent enough to become the direction of the project and to drive repository restructuring.

No blocking contradiction remains between the five reviewed perspectives:

1. Frappe engineering;
2. software architecture;
3. learning methodology;
4. product / marketing;
5. brand / design.

The remaining work concerns execution policies and migration, not a change of strategic direction.

---

## 1. Frappe engineering audit

### PASS — Frappe remains the platform

The foundation does not introduce a parallel framework or mandatory `veqta_core` layer.

This is consistent with the Frappe model in which an App is the installable software package, a Site is the tenant/runtime instance with its own database and Bench manages Apps/Sites.

### PASS — native mechanisms are evaluated before custom mechanisms

The `native-mechanism-first` rule matches the existing Frappe Architecture Standard and prevents VEQTA from teaching or shipping accidental reimplementations of Framework responsibilities.

### FIXED — one Product was initially treated too rigidly as exactly one App

Risk:

```text
Product = exactly one App forever
```

would be unnecessarily restrictive for a future product that legitimately needs a dedicated frontend, companion service or another App.

Resolution applied:

```text
normal/default software boundary = independent Frappe App
additional component = allowed when real responsibility justifies it
```

The exception must be an architectural decision, not a branding decision.

### PASS — Site is not treated as source of truth

Reproducibility is correctly defined through version-controlled application/configuration artifacts rather than undocumented dev-site state.

### PASS — compatibility is explicit

The foundation requires a Frappe version baseline and makes upgrade-sensitive mechanisms visible.

### Frappe engineering conclusion

No foundational redesign required.

---

## 2. Software architecture audit

### PASS — responsibilities are separated

The four-domain model has clear ownership:

```text
Engineering → accepted engineering knowledge
Learn       → educational transformation of that knowledge
Labs        → uncertainty reduction / experiments
Products    → maintained user-facing software
```

This removes the current category error where architecture, training and a product prototype coexist under one generic `docs/` tree while VEQTA itself is defined as the prototype.

### PASS — no universal domain model

The foundation explicitly prevents `Work Item` or another business entity from becoming the base model of all future VEQTA software.

This is critical because VEQTA is an ecosystem, not a bounded business domain.

### PASS — shared code is extracted from evidence

The shared-code rule prevents speculative common libraries and release coupling before at least two real consumers prove the same responsibility.

### PASS — lifecycle boundaries are explicit

A Lab cannot silently become a Product. Promotion is evidence-based and has technical and product gates.

### FOLLOW-UP — governance authority

The foundation defines document authority but does not yet define human/project authority for:

- accepting Charter changes;
- approving Product graduation;
- accepting major architecture exceptions;
- maintainer roles;
- external contribution decisions.

This does **not** block repository restructuring, but `GOVERNANCE.md` is required before VEQTA actively recruits external maintainers/contributors.

### Architecture conclusion

Foundation is structurally sound.

---

## 3. Methodology audit

### PASS — Learn has a real educational thesis

VEQTA Learn is not defined as a feature catalogue.

The learning model is:

```text
requirement
→ responsibility
→ Frappe mechanism
→ architectural decision
→ implementation
→ verification
```

This creates a defensible educational identity and matches the current architecture passport of the new practicum.

### PASS — training cannot weaken engineering rules

The rule that Learn consumes Engineering prevents a common failure: selecting an architecture because it makes a lesson easier.

### PASS — training is separated from product roadmap

Products are not required to add features for teaching value, and courses do not determine production scope.

### FOLLOW-UP — course contract

Every future course should define its own:

- audience prerequisites;
- learning outcomes;
- practical artifact;
- assessment criteria;
- covered Frappe baseline;
- explicit non-goals.

This belongs to Learn governance, not the project Charter.

### Methodology conclusion

The direction is strong enough to scale from one practicum to multiple learning paths without redefining VEQTA.

---

## 4. Product and marketing audit

### PASS — umbrella and product audiences are separated

VEQTA speaks primarily to builders. Future Products speak to their own end users.

This avoids forcing technical architecture messaging into a business product's value proposition.

### FIXED — primary positioning was initially too compound

Initial formulation:

```text
architecture-first open-source product studio and ecosystem for Frappe
```

mixed organizational model, positioning and ecosystem definition in one phrase.

Resolution applied:

> VEQTA is an independent open-source engineering and product ecosystem built on Frappe Framework.

Then separately:

> It operates as an architecture-first product studio.

This cleanly separates **what VEQTA is** from **how VEQTA operates**.

### PASS — product-led does not mean product-first chaos

Engineering and Learn remain first-class assets, while the strategy still requires useful production software over time.

The project therefore avoids both extremes:

```text
only documentation / education
```

and

```text
ship random Apps without reusable engineering knowledge
```

### PASS — product categories are not invented to fill a portfolio

The `Problem → Lab → Incubation` lifecycle prevents startup theatre such as creating CRM/HR/ERP products merely to make the product grid look complete.

### FOLLOW-UP — naming clearance

`VEQTA` remains a working brand until legal/trademark/domain clearance is completed for relevant markets and classes.

This is a brand execution risk, not a reason to change the ecosystem architecture.

### Product / marketing conclusion

Positioning is differentiated enough to guide public communication and product selection.

---

## 5. Brand and design audit

### PASS — one visual system can support multiple responsibilities

The umbrella owns a shared visual grammar while future Products can have product-specific accents and UI identity.

This is scalable and avoids forcing every Product into identical visual branding.

### PASS — design does not override framework architecture

The foundation explicitly rejects replacing suitable native Frappe UI merely to hide the fact that the software is built on Frappe.

This protects both engineering quality and design honesty.

### PASS — permanent navigation vocabulary is simple

```text
Engineering
Learn
Labs
Products
```

is short, distinct and usable both in GitHub information architecture and a future website.

### FOLLOW-UP — visual identity is intentionally not finalized

Do not design a full logo system, product icon family or expensive public brand package before naming clearance.

Safe work before clearance:

- information architecture;
- typography direction;
- grid / spacing principles;
- documentation layout;
- neutral diagrams;
- product UI principles.

### Brand / design conclusion

The information architecture is ready; final identity execution should follow naming clearance rather than precede it.

---

## 6. Cross-document consistency audit

The following statements are now consistent across the foundation:

```text
VEQTA ≠ single Frappe App
VEQTA ≠ Frappe fork
VEQTA ≠ mandatory runtime layer
VEQTA ≠ one business domain

Engineering / Learn / Labs / Products = permanent domains

Lab ≠ Product
Product candidate starts from a problem
normal product core = independently installable Frappe App
additional components require explicit justification

umbrella audience = builders
product audience = product-specific end users

open-source-first ≠ open-core by default
```

No contradictory statement was found in the new foundation documents after corrections.

---

## 7. Known conflicts with the old repository model

The **existing pre-rebrand content** still contains statements that conflict with the new baseline, including concepts equivalent to:

- VEQTA is one application for work management;
- VEQTA itself owns `Work Type` / `Work Item`;
- architecture standard is outside the VEQTA product model;
- training is separate from VEQTA;
- `lazuale/veqta` is the source of truth of one product.

These are expected migration conflicts, not foundation conflicts.

They must be removed by the repository migration defined in `REPOSITORY_STRUCTURE.md`.

---

## 8. Follow-up work that does not change direction

After foundation acceptance, execute in this order:

1. restructure repository into `engineering/`, `learn/`, `labs/`, `products/`, `brand/`;
2. reclassify Work Management as a Lab and rewrite its local wording;
3. repair all internal links;
4. add licensing policy separating software/content/trademarks;
5. add governance before active external contributor recruitment;
6. perform VEQTA naming/trademark/domain clearance;
7. only then finalize public visual identity;
8. select future Product candidates through the defined lifecycle rather than portfolio planning.

---

## Final decision

**The foundation passes the five-discipline audit and is suitable as the baseline for VEQTA repository restructuring.**

Future disagreements should be resolved inside this model unless new evidence proves that one of the Charter assumptions itself is wrong.