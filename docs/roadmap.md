# Study plan and project roadmap

This plan combines the Educosys Agentic AI System Design curriculum with the [Krish Naik Generative and Agentic AI tutorial](https://www.krishnaik.in/ai-tutorials/generative-and-agentic-ai). It is a learning roadmap, not a claim that planned features are already implemented. Study in short concept-first lessons followed by practical milestones and interview practice.

## Current progress

- Introduced retrieval, RAG, keyword, semantic and hybrid search, chunking, and vector indexes conceptually. These topics still need practical work and evaluation.
- A dependency-free keyword-search demo runs on four fictional reports. It is not yet an AI agent or RAG system.
- The intended main dataset is the [Incident Management event log](https://github.com/processminingdata/incidentmanagement). It has not yet been inspected, downloaded, or integrated.

## Phases

1. **Foundations and knowledge systems (25–35 hours):** Inspect the event log and define supported questions. Study keyword and semantic search, embeddings, chunking, vector stores, ANN, FAISS, HNSW, hybrid retrieval, reranking, access control, freshness, debugging, and RAG evaluation. Build and measure an appropriate baseline. The tutorial's LLM and RAG lessons provide practical examples.
2. **Context engineering (10–15 hours):** Context assembly, short- and long-term memory, token budgets, compression, selective loading, and stale or conflicting information. Apply relevant techniques to evidence selection.
3. **Agents and harnesses (20–30 hours):** Tool calling, agent patterns, LangGraph, MCP, execution environments, retries and fallbacks, state persistence, human approvals, and multi-agent trade-offs. Add controlled, read-only tools where appropriate.
4. **Production AI engineering (15–20 hours):** Observability, tracing, evaluation pipelines, release workflows, cost, caching, routing, reliability, security, guardrails, and long-running workflows. Document threat models and measured behavior.
5. **Capstones and interviews (25–40 hours):** Develop the incident project into a documented portfolio piece and separately design and implement an AI coding agent. Practice requirements, alternatives, architecture, trade-offs, and failure modes.
6. **Additional model concepts:** Cover quantization, fine-tuning, LoRA and QLoRA fundamentals and interview trade-offs alongside the phases above; implementation is optional unless justified by a use case.

Estimates total about **95–140 hours**; allow roughly **100–150 hours** with debugging and revision. These are planning estimates, not course-provider durations. At about 10 hours per week, this is approximately 10–15 weeks. Reassess after an initial 30-hour milestone.

## First practical milestone: inspect the data

1. Inspect the source archive, license, CSV schema, representative rows, and data quality before choosing a question or implementation.
2. Determine what one row and one incident represent, and whether fields support structured analysis, document retrieval, or both.
3. Define questions the actual data can answer. If it lacks detailed technical narratives, consider a separate, clearly attributed document source rather than inventing evidence.
4. Build a baseline and a small labeled evaluation. Compare quality, latency, and cost before adding complexity.

The source describes a simulated event log, not live company data. Record attribution and applicable license terms before redistribution. Access control, tenant isolation, and prompt-injection protection remain future work; never claim a simulated incident is real.

## Interview and portfolio practice

For each major topic: explain the idea simply, implement or inspect a small example, compare alternatives, identify failure modes and security risks, and describe how to measure quality, scale, latency, and cost. Keep the README, architecture, datasets, and evaluation results honest and reproducible.
