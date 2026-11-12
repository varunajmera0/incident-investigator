# Agentic AI system design learning series

Start with a fictional online shop. Checkout stopped working last year, and an engineer wrote down what happened. Today checkout is failing again. The Incident Investigator will help an engineer find that old report, inspect evidence from the current incident, and explain which conclusions the evidence supports.

This guide follows one project through five chapters. Chapter 1 links to the lessons covered so far. Chapters 2–5 introduce the next design problems and the exercises we will build toward. The README tracks the working implementation.

## 1. Foundations and knowledge systems

An engineer asks, “Has checkout failed like this before?” Search finds old reports. RAG gives those reports to a language model so it can answer with sources. The retrieval system still needs to find the right passage, and a similar past incident only suggests a hypothesis about today's outage.

- [Retrieval, RAG, keyword search, embeddings, hybrid search, and chunking](retrieval-deep-dive.md)
- [Exact vector search, approximate search, indexes, and databases](vector-search.md)

**Project exercise.** Compare keyword, semantic, and hybrid retrieval on the same labeled questions. Include exact error codes, paraphrases, and questions for which the collection has no evidence. Record how often the expected evidence appears in the first few results, along with latency and cost. Later lessons will cover reranking, metadata filters, access control, and index freshness.

**Interview question.** When would you add an approximate vector index?  
**Sample answer.** I'd measure exact search under expected load first. If it misses the latency target, I'd compare an approximate index on latency, memory, and how often it recovers the nearest results found by exact search. I'd also check whether that change affects retrieval of useful evidence.

## 2. Context engineering

The investigator finds twenty reports. A few are relevant, several repeat the same information, and one describes an older version of checkout. Context engineering decides what the model sees for this particular question. That includes the user's question, selected evidence, and any relevant prior conversation.

**Project exercise.** Give the investigator a fixed token budget. Compare sending the top results as-is with removing duplicates and selecting passages by source, relevance, and freshness. Preserve source IDs and report versions so engineers can inspect the evidence. Test whether summarization drops error codes, timestamps, or qualifiers. Keep saved preferences separate from incident facts and apply access rules when loading either.

**Interview question.** How do you handle conflicting reports?  
**Sample answer.** I'd retain each report's source, timestamp, and scope, then check whether the reports describe different versions or services. If both apply and disagree, I'd show the conflict and explain what evidence would resolve it.

## 3. Agent systems and harness engineering

An engineer asks whether checkout failures started after a release. The investigator needs the deployment time and an error-rate series. The model can request those tools. The surrounding application validates tool arguments, checks permissions, runs the tools, and gives the results back to the model.

**Project exercise.** Start with a fixed workflow over simulated deployments and metrics, then compare it with a model that chooses from the same read-only tools. Measure how often each finds the required evidence, how many calls it takes, and what happens when a tool fails. Limit calls and execution time, record tool outcomes, and treat text returned by tools or retrieved from reports as untrusted data. Explore MCP when there is a tool integration to share across clients.

**Interview question.** When would you choose a fixed workflow over a model-directed agent?  
**Sample answer.** I'd use a fixed workflow when the required checks and their order are predictable. I'd let the model choose tools if investigations need different steps based on what they find, then compare both approaches on evidence quality, reliability, and cost.

## 4. Production AI engineering and LLMOps

The investigator gets slow after the incident collection grows. A trace shows how long the request spent on search, reranking, tool calls, and generation. That tells us which stage to investigate and what to measure after changing it.

**Project exercise.** Record retrieval quality, citation support, median and p95 latency, failed tool calls, and cost per investigation. Compare a simple release against changes such as caching or model routing using the same evaluation cases. Test permission changes and tenant isolation before sharing cached results. Add regression cases for stale evidence and unsupported diagnoses.

**Interview question.** What should happen if retrieval or telemetry is unavailable?  
**Sample answer.** I'd return the evidence we have, identify the missing source, and qualify any conclusions that depend on it. I'd bound retries and track the failure so operators can distinguish a source outage from a model-quality problem.

## 5. End-to-end system design capstones

Bring the pieces together in a simulated checkout incident. The investigator should establish a timeline from current evidence, retrieve related historical reports, and produce a cited brief that distinguishes observed facts, plausible causes, and open questions.

**Portfolio exercise.** Publish a reproducible demo, a diagram showing ingestion and investigation, a comparison against the keyword baseline, and the failure cases we found. Use the same design principles in a second exercise for an AI coding agent, including tool permissions, execution limits, validation, and human approval for consequential changes.

**Interview question.** How would you defend your architecture in five minutes?  
**Sample answer.** I'd state the user need and constraints, walk through ingestion and investigation, show the quality and latency measurements that justify the design, and explain what I'd change if scale, permissions, or freshness requirements increased.

See the [project roadmap](roadmap.md) for implementation milestones. As each lesson is covered, this guide will link to its detailed explanation, worked example, design alternatives, and interview practice.
