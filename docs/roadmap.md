# Roadmap

This is a learning roadmap, not a claim that future features already exist.

1. **Baseline (current):** Search fictional incident reports with keyword matching and show source IDs.
2. **Evaluation:** Create representative labeled queries, including exact identifiers, synonyms, and no-answer cases. Measure retrieval quality at selected ranks, and report latency and limitations.
3. **Retrieval:** Explore document parsing, chunking, semantic retrieval, hybrid search, and reranking; compare against the baseline.
4. **Evidence-based answers:** Add an LLM with source citations and evaluate whether answers are supported by retrieved evidence.
5. **Investigation tools:** Introduce read-only tools over simulated metrics and logs, handling failures and uncertainty.
6. **Production considerations:** Explore authorization, tenant isolation, untrusted inputs, observability, reliability, cost, and deployment. Document the threat model and what is actually implemented.
7. **Portfolio:** Add architecture diagrams, reproducible evaluations, design decisions, and an honest demo.

Public historical datasets are optional future inputs. Record provenance and check licensing and source terms before incorporating them. Never claim a simulated incident is real.
