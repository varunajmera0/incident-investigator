# What we have studied: retrieval and RAG foundations

For worked examples, trade-offs, evaluation, and interview answers, see [the detailed retrieval and RAG lessons](retrieval-deep-dive.md).

These are introductory learning notes, not a claim of mastery or completed implementation. Incident examples are fictional. The project currently implements only a small keyword-search demonstration; the event-log dataset has not yet been inspected or integrated.

## 1. Retrieval and evidence

Suppose checkout fails. A team member asks whether it happened before. **Retrieval** means finding potentially relevant past reports, much like a librarian finding books about a subject. A report is a clue, not proof that the current incident has the same cause.

For example, the question “Why did checkout fail?” may retrieve a report saying a payment endpoint was misconfigured. The report's incident ID and source let the engineer check it. In a real system, users must be allowed to access the evidence they retrieve.

## 2. Retrieval-augmented generation (RAG)

RAG adds a language model to retrieval:

```text
Question → retrieve relevant evidence → provide question and evidence to model
         → generate an answer with sources
```

Search returns candidate evidence; generation uses the supplied evidence to formulate an answer. RAG can help a model answer using information available at request time. It does not guarantee correctness: retrieval might miss the right passage, return an outdated report, or the model might misinterpret the evidence. Citations help users inspect the source but do not by themselves guarantee that the answer is supported.

## 3. Keyword search

Keyword search looks for terms from the question in documents. For “checkout payment deployment”, a report containing those words can rank highly. Exact identifiers such as `ERR-403` can be particularly useful, provided the tokenizer and index preserve or reliably match them.

Its limitation is vocabulary mismatch: “purchase failed” may not match “checkout stopped working”. Matching words also does not prove that a report answers the question.

The current `search.py` uses a small stop-word list and scores unique matched query terms with inverse document frequency (IDF): terms appearing in fewer reports get more weight. It is a teaching baseline, not BM25. It does not stem words, so `fail` and `failed` differ. Its score is a ranking number, not a confidence percentage.

## 4. Semantic search and embeddings

An **embedding** is a numerical representation (a vector) produced by a model. In semantic retrieval, reports or chunks are embedded in advance. A question is embedded at search time, and its vector is compared with stored vectors. This can find related wording such as “customers could not purchase” and “checkout failed”.

The question and documents need embeddings from a compatible model and configuration. The closest vector is only a candidate: similarity does not establish relevance or a true cause. Embeddings add computation, storage, update, and potentially external-provider cost. Semantic search is not implemented in this project yet.

## 5. Hybrid search and RRF

Hybrid retrieval combines methods, commonly keyword search and semantic search. Keyword search can help with an exact error code; semantic search can help when symptoms are described in different words.

One way to merge ranked lists is **reciprocal rank fusion (RRF)**: results receive contributions based on their position in each list. A document found by only one method can still appear in the combined results. Combining ranks avoids directly adding raw scores that may be on different scales.

Hybrid search adds components and cost. Compare it with each simpler method using the same representative questions, access rules, latency, and cost measurements. It is not implemented yet.

## 6. Chunking and metadata

A long report may have sections for summary, timeline, root cause, and resolution. **Chunking** divides it into smaller pieces so retrieval can return a useful passage rather than the whole document.

- Small chunks can be precise but may lose surrounding context.
- Large chunks retain context but may add irrelevant text and increase token use.
- Section-based splitting can preserve structure; unusually long sections may need further splitting.
- Overlap repeats text across boundaries to preserve context, at the cost of extra storage and possible duplicates.

Keep source identifiers and relevant permissions with chunks. Test chunking on representative questions: does the retrieved passage contain the evidence and enough context? Chunking is not implemented yet.

## 7. Vector search and indexes

**Exact vector search** compares a question vector with all stored vectors, then ranks them by a chosen similarity measure. It can be a sensible starting point for a small collection.

An **approximate nearest neighbor (ANN) index** searches more efficiently by potentially accepting that some exact nearest neighbors may be missed. A **vector index** is a search structure; a **vector database** stores and manages vectors and may offer indexes, filtering, and updates. FAISS is a similarity-search library; HNSW is an index approach. A separate vector database is not always necessary.

Evaluate ANN against exact search for neighbor recall, latency, and resource use; also measure whether retrieved material is relevant to real questions. Even an exact nearest vector is not necessarily useful evidence. Vector search is not implemented yet.

## 8. Interview practice

**What is retrieval?** Finding potentially useful information for a question. A retrieved result must still be checked for relevance and authorization.

**What is RAG?** Retrieving external information and supplying it to a language model at request time to help generate an answer. Its quality depends on both retrieval and faithful use of evidence.

**When is keyword search useful?** For exact terms such as identifiers and error codes, subject to correct tokenization. It also makes a simple baseline. It may miss synonyms.

**What is an embedding?** A model-generated numerical representation of data that can be compared with other compatible vectors for tasks such as similarity search.

**What is hybrid search?** Combining retrieval methods, such as lexical and semantic search. Measure whether the improvement justifies complexity and cost.

**Why chunk documents?** To retrieve relevant portions of longer documents. Choose boundaries and overlap by testing evidence coverage, context, duplication, and token use.

**Exact vs. approximate vector search?** Exact search finds nearest vectors under a chosen measure by examining the full collection; ANN can be faster but may miss some nearest neighbors. Neither guarantees a correct answer.

**How do you choose a design?** Start with requirements and a simple baseline. Compare approaches using labeled representative questions, retrieval quality, supported answers, latency, cost, security, and operational needs.

## Next practical step

Inspect the [Incident Management event log](https://github.com/processminingdata/incidentmanagement): its schema, sample rows, provenance, and license. Determine what it can actually answer before choosing structured analysis, document retrieval, or both.
