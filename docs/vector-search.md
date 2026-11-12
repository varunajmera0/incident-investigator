# Vector search, indexes, and databases

We’re in Chapter 1, **retrieval fundamentals**. After splitting incident reports into chunks and turning those chunks into embeddings, we need a way to find the closest chunks when a question arrives.

## Start with an incident

An engineer asks, “Have payments failed because of an expired certificate before?” Our fictional reports describe three different problems.

| Chunk | What it says |
| --- | --- |
| A | The payment certificate expired and the gateway rejected connections. |
| B | Checkout slowed down when the database ran out of connections. |
| C | A deployment pointed checkout at the wrong payment endpoint. |

The system embeds the question and compares it with the stored chunk embeddings. We’d expect chunk A to be a strong candidate. Chunk C is also about payments, but it describes a different cause. Even if A ranks first, it only tells us what happened in that past incident.

```text
Before search    Report → chunks → embeddings → store with source IDs
During search    Question → embedding → find closest allowed chunks → return evidence
```

## Exact search and approximate search

**Exact search** scores the question against every eligible vector. If we ask for the three closest chunks, it returns the true top three under the chosen similarity measure. With four fictional reports, scanning them all is a reasonable starting point.

**Approximate nearest neighbor search (ANN)** uses an index to explore a subset of candidates. This can reduce query latency on a large collection, with a chance of missing a chunk that exact search would have found. **HNSW** is one example. It starts in a sparse graph layer to find a promising region, then searches denser layers for nearby vectors. [HNSW paper](https://arxiv.org/abs/1603.09320)

## Index, library, and database

| Term | What it does |
| --- | --- |
| Vector index | Organizes vectors for similarity search. HNSW is one index design. |
| Search library | Provides implementations of search algorithms. FAISS offers exact and approximate indexes. |
| Database with vector support | Manages stored records and may provide vector indexing, filtering, persistence, and updates. Check the product’s actual capabilities. |

Another ANN approach, **IVF**, groups vectors and searches selected groups. **Quantization** compresses vector representations to reduce memory and can change rankings. Evaluate these options if graph memory or scan latency becomes a bottleneck. [FAISS index documentation](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)

## Apply it to the Incident Investigator

- **Scale and cost.** Benchmark an exact scan first. As the number of chunks or concurrent queries grows, compare an ANN index on p95 query latency, index memory, build time, and update throughput.
- **Quality and failure modes.** Compare ANN results to the exact top k using the same embeddings, metric, and eligible documents. Then measure whether either search retrieves the right evidence for labeled incident questions. For example, finding 8 of the exact top 10 gives 80% ANN recall@10. That score measures agreement with exact search.
- **Security and freshness.** Enforce permissions before any chunk is exposed to the user or the model. Benchmark with realistic access filters, especially when users can see only a small fraction of the corpus. Keep chunk embeddings and access metadata in sync with report updates and deletions.
- **Project status.** The current Python demo implements keyword retrieval over fictional reports. Exact vector search would be our first vector baseline once we add embeddings.

## Interview questions and sample answers

**Do you always need a dedicated vector database for RAG?**

> No. I’d start with an exact scan for a small collection. At higher scale I’d compare vector support in the existing database or search engine with a dedicated service, using the workload’s latency, filtering, update, and cost requirements.

**How do you evaluate an ANN index?**

> I’d compare its top-k results with exact search on the same eligible corpus, then measure p95 latency, memory, and update throughput. I’d separately measure evidence retrieval on labeled user questions.

**Can exact vector search still return an irrelevant result?**

> Yes. Exact search optimizes the chosen similarity measure. That measure can rank two payment incidents closely even when their causes differ.

**Quick check.** If our project has only four incident reports, would you start with an exact scan or HNSW? What measurement might make you revisit that choice?
