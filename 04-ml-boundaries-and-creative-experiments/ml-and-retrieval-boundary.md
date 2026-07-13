# ML and retrieval boundary

## Current, inspectable work

The current technical proof in this portfolio is the ContextPack retrieval slice in `../02-bounded-retrieval/`. It indexes allowlisted Markdown into a dedicated local collection, uses deterministic lexical-hash vectors, returns cited source excerpts, and verifies source hashes after a change.

That is a bounded retrieval and provenance proof. It is not a claim of semantic retrieval, a trained embedding model, a fine-tuned language model, reinforcement-learning work, or a general RAG system.

## Learning direction

Future work may explore semantic embeddings, evaluation, small-model experimentation, and model adaptation only through separate artifacts that identify:

1. the dataset and consent boundary;
2. the model and method actually used;
3. evaluation criteria and baseline;
4. failure cases and rollback path; and
5. the distinction between a research experiment and a product claim.

## Creative-model boundary

The Suno excerpt in `artifacts/` shows prompt-level specification for a specialized creative tool. It should not be represented as training, fine-tuning, or evidence of ML-research proficiency.
