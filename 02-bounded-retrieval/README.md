# 02. Bounded retrieval and verification

## What this directory shows

This is a deliberately narrow retrieval proof. It indexes an explicit allowlist of Markdown sources into a local, loopback-only Qdrant collection; returns cited excerpts with line ranges and source hashes; builds bounded ContextPacks; and detects provenance drift after a source changes.

## Artifacts

- `contextpack/contextpack.py`: standard-library Python CLI.
- `contextpack/contextpack-manifest.json`: allowlist and exclusion contract.
- `contextpack/tests/test_contextpack.py`: deterministic unit tests.
- `contextpack/docker-compose.local.yml`: disposable loopback-only Qdrant service.
- `contextpack/README.md`: operation and rollback guide.
- `receipts/contextpack-local-retrieval-proof-receipt.md`: public-safe proof receipt with reproducible checks and a clear boundary.

## Role in the wider architecture

This is the evidence-retrieval layer between file-primary records and future work surfaces. It demonstrates how retrieval can remain inspectable and source-governed while keeping canonical Markdown and YAML authoritative.

## Boundary

The proof uses deterministic lexical-hash vectors. It does not download a model, call a provider, claim semantic understanding, operate as a general crawler, or constitute the Exocore product runtime. The copied code is presented as an inspectable proof slice; the public receipt omits private source layout and local-profile details.
