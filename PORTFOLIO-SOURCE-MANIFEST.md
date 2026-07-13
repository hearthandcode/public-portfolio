# Portfolio source manifest

This manifest implements the five artifact domains requested in the Knowledge Team workbook. It distinguishes exact source copies from public-safe derivatives, so a visitor can see what is directly inspectable and what has been condensed to avoid publishing private material.

| Domain | Portfolio target | Source or basis | Treatment | Boundary |
| --- | --- | --- | --- | --- |
| Knowledge architecture | `01-knowledge-governance/artifacts/` | Hub taxonomy registry and integrity rules | Public-safe derivatives | Internal paths, personal-record references, contributor identities, and runtime details are omitted. Pilot artifacts, not a complete ontology or deployed product. |
| Retrieval and evaluation | `02-bounded-retrieval/` | Exocore ContextPack code, manifest, tests, runbook, compose file, and proof receipt | Code and operational fixtures copied; proof receipt condensed | Deterministic lexical proof only. No semantic retrieval, provider calls, or product runtime claim. |
| Public-safe research record | `03-research-methods/` | Session-logging protocol, thesis-refocus and methodology sources, selected July session records | Generic protocol copied; thesis scope and reflection excerpts curated | Individual, unverified observations. No raw private log material. |
| ML/RL boundary and creative model use | `04-ml-boundaries-and-creative-experiments/` | Candidate's source note, ContextPack evidence, and a Suno style prompt | Public-safe derivative and style-prompt excerpt | No fine-tuning, RL, embedding-model, or trained-model results are claimed. Raw lyrics are withheld. |
| Exocore platform direction | `05-exocore-platform/artifacts/` | Reviewed project thesis plus top-surface orientation, product-boundary, and roadmap documents | Public-safe derivatives | The two derivatives omit internal architecture, dependency research, personal review answers, and operational planning. They describe proposed direction, not a launched system. |

## Files intentionally not copied

- Raw session logs, which may contain private self-report or third-party material
- The full Suno lyric prompt, which contains personal material not needed to show the creative-model workflow
- Credentials, secrets, live runtime configuration, agent instructions, and generated local indexes

This allowlist is intentionally narrow. Adding a new artifact requires a source check, a privacy check, a maturity label, and Scott's review before publication.
