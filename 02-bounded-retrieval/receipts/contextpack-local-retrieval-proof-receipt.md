---
title: "ContextPack local retrieval proof"
kind: public-safe-derivative
status: review-draft
maturity: implemented_local_proof
source_treatment: Public-safe derivative of a private engineering receipt
reviewed_by: null
reviewed_at: null
verified: false
---

# ContextPack local retrieval proof

## What this proves

This is a small, inspectable retrieval proof. It builds a bounded ContextPack from an explicit allowlist of Markdown sources, preserves headings and line ranges, and records a SHA-256 hash for each source. The proof is local and deterministic.

Its purpose is to test whether context selection can remain reviewable and source-governed. It is not an Exocore desktop application, a semantic-retrieval result, or a claim of general agent memory.

## Public evidence

The public repository includes:

- a standard-library Python CLI for status, indexing, search, ContextPack assembly, and verification;
- an explicit source-selection manifest with inclusion and exclusion rules;
- deterministic unit tests for manifest exclusion, heading citations, provenance drift, and loopback-only service access;
- a disposable local Compose definition; and
- a runbook describing operation and rollback within the public proof directory.

On 2026-07-13, the public test suite completed successfully: **5 passed**.

## Boundary

- The ranker uses deterministic lexical-hash vectors. It does not download a model or claim semantic understanding.
- The service boundary is loopback-only. The proof does not call a provider or remote API.
- The manifest chooses sources explicitly. Generated ContextPacks are disposable projections, not an authority layer.
- The proof does not provide autonomous context injection, provider management, broad filesystem access, or product-runtime governance.

## Reproduction

From the public repository root:

```bash
python3 -m pytest -q 02-bounded-retrieval/contextpack/tests
```

For the optional local service and CLI instructions, read [`../contextpack/README.md`](../contextpack/README.md). Use only the supplied local proof configuration and its documented rollback steps.

## Maturity

The code and test suite are public, bounded engineering evidence. The surrounding product direction remains proposed. `verified: false` means this artifact has not received a human review seal.
