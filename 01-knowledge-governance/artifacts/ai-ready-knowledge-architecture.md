# AI-ready knowledge architecture

**Source treatment:** Public-safe derivative of independent knowledge-system design work.
**Maturity:** Design record with inspectable companion artifacts. It is not a deployed product or enterprise governance service.
**Public release review:** Scott Rallya reviewed this derivative for publication on 2026-07-14.

## Why information architecture comes before an AI answer

An AI-enabled search, retrieval, or assistant system depends on the quality of the records it touches. Source material needs usable boundaries. Terms need stable meanings across contexts. A reviewer needs to be able to identify the authoritative record, the source material behind a result, and the route for correcting it.

The knowledge-governance artifacts in this portfolio describe a file-primary approach to those conditions. The goal is to make technical and research material easier to discover and reuse while keeping authority, provenance, and review visible.

## Design patterns represented here

### Controlled metadata and vocabulary discipline

A resource needs stable descriptive fields before it can be routed, retrieved, evaluated, or reused reliably. The companion [knowledge taxonomy](knowledge-taxonomy.yaml) makes several of those fields explicit: artifact type, domain, evidence state, lifecycle status, privacy tier, and relationship type.

The approach draws design vocabulary from [SKOS](https://www.w3.org/TR/skos-primer/) and [Dublin Core](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/). Those sources inform the design. They do not establish a standards-conformant implementation.

### Provenance and review-state visibility

A useful result should remain traceable to the material and process that produced it. The taxonomy treats provenance, evidence state, privacy tier, and lifecycle status as visible record properties. The [integrity rules](taxonomy-integrity-rules.yaml) show how selected structural checks can be made explicit while reserving semantic and privacy judgments for human review.

PROV-O is a useful reference vocabulary for this problem. This portfolio does not claim a PROV-O implementation.

### Canonical records and derived views

An index, summary, search result, or generated description is a derived view. It should not silently acquire the authority of the record it represents. Keeping that distinction visible preserves a correction path when definitions change, a source proves incomplete, or an automated interpretation is wrong.

### Human-visible authority and reversible change

Automation can propose structure. A person still needs to see why a suggestion appeared, what source context informed it, where its authority ends, and how to reverse a durable change. This pattern gives AI-supported knowledge work a review surface rather than asking a plausible inference to stand as an untraceable fact.

## Inspectable public evidence

- [Knowledge taxonomy](knowledge-taxonomy.yaml): controlled vocabulary, concept schemes, evidence states, lifecycle values, privacy tiers, and relationship types.
- [Taxonomy integrity rules](taxonomy-integrity-rules.yaml): machine-readable validation design for selected structural checks.
- [Bounded ContextPack retrieval proof](../../02-bounded-retrieval/): runnable local proof with an explicit provenance boundary.
- [Exocore public orientation](../../05-exocore-platform/artifacts/exocore-public-orientation.md): proposed local-first workbench direction for inspectable knowledge work and reliable return to prior work.

## Claim boundary

This artifact represents current independent design and systems work. It does not establish prior administration of Alation or another enterprise catalog, enterprise metadata-governance leadership, formal business-glossary ownership, or production RDF, OWL, SKOS, SPARQL, or graph-database implementation.

The current portfolio includes a bounded local retrieval proof and public design records. It does not claim semantic retrieval, a general RAG service, a production knowledge-management product, or a deployed AI governance runtime.
