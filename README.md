# Incident Investigator

A learning project exploring how to find evidence for software incidents. The goal is to evolve a transparent search baseline into an incident investigation assistant, while measuring retrieval quality and documenting security and system design trade-offs.

**Status:** Early learning baseline. The current program searches four fictional incident reports using keyword matching. It does not call an LLM, perform semantic or hybrid search, enforce access controls, or diagnose live incidents.

## Try the baseline

Requires Python 3 and no third-party packages or API keys.

```bash
python3 search.py "checkout errors after payment deployment"
python3 search.py "database connection timeout"
python3 search.py "purchase failures after release"
```

The last example highlights a weakness of exact-word search: relevant reports may use different words. Results include synthetic source IDs so that the reader can inspect the evidence. A high ranking does not establish an incident's root cause.

## How it works today

```text
Question → tokenize → score matching terms → rank reports → show source and text
```

The scorer weights a query term more heavily when it appears in fewer reports. This is a small educational baseline, not a full search engine or BM25 implementation. Data is loaded from [`data/incidents.json`](data/incidents.json).

## Learning notes and roadmap

- [Complete learning series and interview practice](docs/learning-series.md)
- [Retrieval, RAG, keyword and semantic search, hybrid search, and chunking](docs/foundations.md)
- [Vector search, indexes, and databases](docs/vector-search.md)
- [Planned milestones and evaluation](docs/roadmap.md)

The reports are fictional, created for this project. The intended main dataset is the [Incident Management event log](https://github.com/processminingdata/incidentmanagement), which has not yet been inspected or integrated. We will inspect its schema and document its provenance and license before use or redistribution.

## Limitations and security

This local demo has no authentication, authorization, tenant isolation, prompt-injection defenses, or sensitive-data handling. Do not use it with confidential incident data or as a production incident response tool. Results are clues to investigate, not verified diagnoses.
