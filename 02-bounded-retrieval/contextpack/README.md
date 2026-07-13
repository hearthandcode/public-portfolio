# Exocore ContextPack CLI Proof

This directory is a narrow, runnable retrieval proof for Exocore architectural records. It is not the Exocore product runtime, a semantic-memory service, or a general repository crawler.

## What it does

- reads only `contextpack-manifest.json` allowlisted Markdown sources;
- creates a dedicated Qdrant collection in a loopback-only service at `127.0.0.1:6335`;
- chunks records by headings and indexes deterministic lexical-hash vectors;
- returns source path, line range, review state, verification state, score, and source hash;
- writes bounded Markdown ContextPacks with JSON provenance sidecars;
- verifies a pack's cited source hashes after a source change.

The vectors are a deterministic lexical baseline. They do **not** use an embedding model and must not be described as semantic understanding.

## Run from the Harness root

```bash
# Start only the dedicated proof service. It does not use the Archive's Qdrant collection.
docker compose -f tools/contextpack/docker-compose.local.yml -p exocore-contextpack up -d

# Confirm the manifest and loopback service.
python3 tools/contextpack/contextpack.py status

# Rebuild only the dedicated proof collection.
python3 tools/contextpack/contextpack.py index --replace

# Retrieve cited records.
python3 tools/contextpack/contextpack.py search "ADR-003 record projection contract"

# Build a reusable review pack.
python3 tools/contextpack/contextpack.py pack \
  "ADR-003 record projection contract" \
  --purpose "prepare the next T37 architecture design record"
```

## Boundaries

- Canonical Markdown/YAML remains authoritative. Qdrant and generated packs are disposable projections.
- The manifest excludes agent instructions, runtime state, credentials, session material, and raw research staging.
- The proof uses `127.0.0.1:6335` only. Do not point it at the existing `knowledge_archive` collection or publicly bound Qdrant service.
- There is no MCP server or automatic Hermes context injection. A narrow skill may invoke this CLI only after test and live-pack verification.

## Verify and roll back

```bash
python3 -m unittest discover -s tools/contextpack/tests -v
python3 tools/contextpack/contextpack.py verify \
  .exocore-contextpacks/packs/<contextpack>.manifest.json

docker compose -f tools/contextpack/docker-compose.local.yml -p exocore-contextpack down -v
rm -rf .exocore-contextpacks/
```
