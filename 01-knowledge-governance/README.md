# 01. Knowledge governance

## What this directory shows

This directory contains the controlled-vocabulary and rule-constraint layer of a file-primary knowledge system. The artifacts make terms, metadata, relationships, lifecycle state, and review boundaries legible to people and validators rather than leaving them as informal conventions.

## Artifacts

- `artifacts/knowledge-taxonomy.yaml`: public-safe pilot registry for terms, concept schemes, evidence states, privacy tiers, and lifecycle values.
- `artifacts/taxonomy-integrity-rules.yaml`: public-safe, machine-readable validation design covering selected taxonomy checks.

## Role in the wider architecture

The taxonomy names the conceptual surface. The integrity rules make selected parts of that surface checkable. Together they are the governance foundation beneath retrieval, review, and later platform projections. They are not a full ontology, an RDF export, or a claim that every current record is already validated.

## Source and maturity

Both files are concise public-safe derivatives of private working records. They retain portable vocabulary and validation ideas while omitting internal paths, personal-record references, contributor identities, and runtime details. The taxonomy is marked `pilot`; the rules describe a validation design, not an installed public service.
