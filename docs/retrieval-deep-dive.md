# Retrieval and RAG: detailed learning notes

These notes expand the concepts introduced so far. Examples and numbers are illustrative; incident reports are fictional. The current project implements only a small keyword-search baseline, not the RAG, vector, chunking, security, or evaluation systems described below. The intended event-log dataset has not yet been inspected.

## Start here: investigate one checkout incident

**Question:** How did the team restore checkout after the payment deployment?

Here is the fictional report we'll use throughout the exercise.

| Section | Report text |
| --- | --- |
| Timeline | After the payment deployment, checkout began returning HTTP 500 errors. |
| Root cause | The payment client was configured to use the wrong endpoint. |
| Resolution | The team rolled back the payment deployment. Checkout recovered. |

**1. Choose what to search.** We could store the whole report as one searchable item, or store one chunk per section. For this question, a section chunk lets us cite the exact resolution. Keep the incident ID and section name with each chunk so the reader can open the original report. If the resolution merely said “They rolled it back,” include the incident title or fetch the surrounding section so the reader knows what “it” refers to.

**2. Rank the chunks.** Suppose an embedding model gave us the following vectors. These are made-up unit vectors chosen to make the arithmetic easy. The query vector is `[1, 0]`, so its cosine similarity to each chunk equals that chunk's first coordinate.

| Chunk | Toy vector | Similarity |
| --- | --- | ---: |
| Timeline | `[0.96, 0.28]` | 0.96 |
| Resolution | `[0.80, 0.60]` | 0.80 |
| Root cause | `[0.00, 1.00]` | 0.00 |

Exact search checks all three vectors. With only one result, it returns **Timeline**, which matches the symptoms but omits the fix. With two results, it also finds **Resolution**, which supports the answer: “The team rolled back the payment deployment” (INC-001, Resolution). The higher similarity score belongs to the wrong section for this question.

**3. Decide what to change.** Try retrieving two chunks and reranking them by whether they answer the question. Or test whether adding section headings to the embedded text improves the initial ranking. A keyword query for `HTTP 500` may help find the timeline, but it can be less useful for this particular question about the fix. Compare these options on several questions, including ones about symptoms and root causes, before settling on a design.

**4. Decide whether an index helps.** Exact search over three vectors is straightforward. If the same system grows to a million chunks, an approximate index such as HNSW may reduce search time. If exact search returns Timeline and Resolution but HNSW returns Timeline and Root cause, the index recovered one of the two exact neighbors. In this example it also lost the only chunk that answers the question. Measure both agreement with exact search and retrieval of labeled evidence. Include query latency and memory in the comparison, and apply the same access rules to both methods.

**Try it before reading further:** Change the question to “What error did customers see?” Which section should rank first now? Would the rollback passage be enough to answer? Then ask “Did the rollback take five minutes?” The report gives no duration, so the answer should state that the duration is unknown.

**Interview follow-up:** “The model gave the wrong answer. How would you debug it?” Start by checking whether the resolution chunk was indexed, authorized for the user, and retrieved. If it was retrieved, check whether it made it into the model's context. If it was present, inspect whether the generated answer was supported by that passage. Each failure points to a different part of the system.

## 1. The problem: finding evidence

A checkout service fails. An engineer asks, “Have we seen a payment configuration failure before?” There may be thousands of incident records. Retrieval finds candidate records to examine. A past incident is evidence of a past event, not proof of the present root cause.

Different questions need different tools. “How many tickets were escalated last month?” is a structured aggregation if suitable event data exists; SQL or another deterministic query can be more appropriate than semantic search. “Find a report describing a similar certificate failure” is a text-retrieval problem. A mixed question may need both, with sources and clear boundaries.

### Source and authorization

Keep an incident ID, source location, version, timestamp and access policy where available. A source ID lets a reader check the record; a timestamp helps identify stale evidence. Authorization must be enforced for the requesting user before content is exposed, including during retrieval and tool calls. Metadata alone is not authorization.

## 2. RAG: retrieval plus generation

A retrieval-augmented generation (RAG) system finds information and sends selected evidence with a question to a language model. The model formulates an answer; the application should give the reader a way to check sources.

```text
Indexing, before a question:
  source → parse → split if appropriate → index text/vectors and metadata

Serving, for each question:
  authenticate → retrieve authorized candidates → select evidence
  → ask model to answer from evidence → return answer and sources
```

**Example:** A report says “An incorrect payment endpoint caused HTTP 500 errors; rollback restored service.” A supported answer can repeat that claim and cite the report. If the question asks about a different outage, the correct response may be “This is a similar past incident; the current cause is not established.” If no useful evidence exists, the system should say so.

**Failures:** The parser may lose content; an index may be stale; retrieval may miss the answer; the selected passage may lack context; or the model may make an unsupported inference. Evaluate these stages separately. A citation is helpful but can point to irrelevant evidence, so verify support as well as citation presence. Treat retrieved text as untrusted data: a report telling the model to ignore its instructions should not become an instruction.

**Alternatives:** For a small, stable set of short documents that fits the context budget, directly providing authorized documents can be simpler. Structured queries are often preferable for exact counts and calculations. Choose using accuracy, permissions, freshness, latency and cost—not fashion.

## 3. Keyword search

Keyword or lexical retrieval uses matching terms. For example, `checkout payment deployment` can find a report containing those words. A search engine typically tokenizes, normalizes and indexes text, then ranks matching candidates. Tokenization matters: a system may split `ERR-403` into `err` and `403`; preserving a separate exact-match field can help. Test identifiers actually used by the application.

### Our baseline: weighted matches

`search.py` lowercases and extracts letter/number sequences, removes a small list of common words, and matches unique query terms against each report's title and text. For each matched term it adds:

```text
weight = 1 + ln((number of documents + 1) / (documents containing term + 1))
score  = sum of weights for matched query terms
```

If there are four reports and a term appears in only one, its illustrative weight is `1 + ln(5/2) ≈ 1.92`. If it appears in all four, its weight is `1 + ln(5/5) = 1`. Rarer matched terms contribute more. The score is for ordering, not a probability or confidence. The implementation uses sets, so repeated occurrences do not raise the score. It doesn't stem `fail` to `failed`, and its simple regular expression splits punctuation.

**Trade-offs:** This approach is easy to run and inspect but scans the toy dataset and can miss synonyms. Full search engines commonly use an inverted index and ranking methods such as BM25, which account for term frequency and document length; our baseline is not BM25. Matching terms alone can also return an irrelevant report.

**Try it:** Run `python3 search.py "checkout errors after payment deployment"`, then `python3 search.py "purchase failures after release"`. Compare the ranking and the wording of the returned text. Do not interpret a shared word as proof of a shared root cause.

## 4. Semantic search and embeddings

An embedding model turns text into a vector—a list of numbers. The particular numbers are not human-readable labels. During indexing, the system computes document or chunk embeddings. During search, it embeds the question and compares its vector to stored vectors.

```text
“checkout stopped working” → vector A
“customers cannot purchase” → vector B
question vector → compare against A and B → rank candidates
```

Related meaning can lead to a higher similarity even when words differ, but this is model-dependent and not guaranteed. A common similarity measure is cosine similarity: the dot product of two vectors divided by the product of their lengths. It compares vector direction; for nonzero normalized vectors, cosine similarity equals their dot product. The choice of metric must match the embedding model and index configuration.

Use compatible query and document embeddings, including any model-specific query/document instructions. If the model changes, existing embeddings may need to be regenerated. Protect sensitive data sent to an embedding provider, and measure embedding cost, latency and storage. Similarity is not factual correctness or a probability of truth.

## 5. Hybrid search and reciprocal rank fusion

Keyword search can find precise identifiers; semantic search can find related phrasing. Hybrid retrieval obtains candidates from both and combines them. A candidate found by just one method can still matter.

A simple fusion method is reciprocal rank fusion (RRF). For each document, add `1 / (k + rank)` for every ranked list where it appears. `k` is a chosen constant and rank starts at 1. With `k = 60`, a report ranked first in keyword and second in semantic search gets `1/61 + 1/62 ≈ 0.0325`. A report found only at rank 1 in one list gets `1/61 ≈ 0.0164`. These are fusion scores, not probabilities.

RRF combines positions, not the raw keyword and vector scores, which might use incompatible scales. Alternatives include normalized weighted score fusion and learning-to-rank; each needs evaluation and tuning. Fused results can still be irrelevant or omit the right evidence. Running both paths adds operational complexity, and generating a query embedding adds cost; parallel execution may reduce latency depending on the architecture.

## 6. Chunking: preserving enough context

Chunking splits a long document into retrievable passages. An incident may have headings for summary, timeline, root cause, and resolution. A query asking “How was it fixed?” might retrieve the resolution section, ideally with enough surrounding context to identify what was fixed.

Consider: “The payment service had the wrong address. The team corrected it, and checkout recovered.” Splitting between sentences risks retrieving “corrected it” without saying what “it” refers to. But placing an entire long report in one chunk can add irrelevant text and consume the model's context budget.

### Strategies and trade-offs

| Approach | Potential benefit | Potential issue |
| --- | --- | --- |
| Fixed-size chunks | Simple and predictable | Can split a thought or structure |
| Paragraph or heading-based | Retains natural structure | Sections vary in size and parsing quality |
| Parent-child | Search smaller passages, then fetch authorized surrounding context | Extra data relationships and more context to manage |
| Overlap | Repeats boundary text to help preserve context | More storage and duplicate results |

Overlap example: chunks `A B C D` and `C D E F` share `C D`. Overlap is not always needed. Chunk size, boundaries and overlap should be evaluated using real questions and model token budgets; there is no universal best size. When parsing tables or code, preserve their structure where possible. Store source ID, document version, position or section, and access metadata; enforce access when retrieving any chunk or parent.

**Evaluation:** For a labeled question, check whether retrieved chunks contain the evidence, whether the evidence has enough surrounding context, how much duplication occurs, and how many tokens are supplied. Test multiple strategies against the same questions.

## 7. Vectors, exact search, ANN, and databases

With a small collection, exact search can compare the query vector to every stored vector and return the closest under the chosen metric. The result is exact with respect to that metric and collection—not necessarily relevant to the question.

An approximate nearest neighbor (ANN) index organizes vectors to search faster without necessarily examining all of them. It may miss some exact nearest neighbors. There is a trade-off among search time, memory, build time and approximation quality. A vector index is a search data structure; a vector database manages stored vectors and may add filtering, persistence, updates and other operations. Existing databases or search engines can also offer vector support.

**FAISS** is a library for similarity search; it offers multiple index types, including exact and approximate options. **HNSW** is a graph-based ANN approach: vectors are connected in layers, and search navigates the graph to find nearby candidates. Index configuration affects speed, memory and accuracy. Neither name implies the application automatically has correct access control, persistence or a complete database service.

For a tiny toy corpus, start with exact comparison if embeddings are actually needed. For a large corpus, benchmark alternatives under the expected workload. For ANN quality, compare its top-k neighbors to exact search using the same vectors and metric. Separately measure whether the retrieved evidence is relevant to users: matching the exact vector ranking perfectly does not prove that the embedding model understood the task.

## 8. Measuring retrieval and answers

Build a small labeled set of representative questions, permitted documents, relevant evidence and no-answer cases. Include exact error codes, synonyms, stale documents and permission boundaries. Split development examples from a held-out test set to reduce overfitting. Avoid claiming strong performance from a handful of easy synthetic examples.

- **Recall@k:** fraction of known relevant items retrieved in the top k. If a question has two relevant reports and top 3 contains one, recall@3 is 1/2.
- **Precision@k:** fraction of top-k retrieved items labeled relevant. If one of three is relevant, precision@3 is 1/3.
- **Latency and cost:** record the setup, dataset size, model and index settings, query latency, resource use and token or provider costs.
- **Answer evaluation:** separately check whether an answer is supported by its cited evidence, whether it addresses the question and whether it acknowledges insufficient evidence.

Relevance labels are incomplete or subjective in many real datasets; report how they were created and the limits of the evaluation. Test authorization and prompt-injection handling as separate security properties, not just as ranking metrics.

## 9. Interview questions and answers

**Explain RAG in one minute.** “I retrieve authorized evidence relevant to the question, select enough context, and pass it to a model to generate an answer with sources. I evaluate retrieval and supported answers separately and handle missing or stale evidence.”

**When would keyword search be better than semantic search?** “For exact identifiers such as error codes, subject to indexing and tokenization. I would benchmark both on real queries rather than assume a winner.”

**What is an embedding?** “A model-generated vector representation used to compare data. Similar vectors are retrieval candidates; they do not establish truth.”

**Why combine lexical and semantic retrieval?** “They can capture complementary signals. I would compare hybrid retrieval with each baseline and account for complexity, latency, permissions and cost.”

**How do you choose chunk size?** “Start from document structure and user questions. Measure evidence coverage, sufficient context, duplicates and token usage across several choices.”

**What is the difference between an index and a database?** “An index helps find vectors; a database manages stored data and may provide vector indexing, filtering, persistence and updates. Capabilities depend on the product.”

**How do you evaluate ANN?** “Compare top-k results with exact vector search to quantify approximation recall, then measure latency and resources. Evaluate relevance to real user questions separately.”

**What security risks matter?** “Unauthorized retrieval, cross-tenant leakage, sensitive content sent to providers or logs, and instructions embedded in retrieved documents. Enforce authorization in retrieval and tool access, minimize data exposure, and test adversarial cases.”

## 10. Project status and next step

The repository currently contains a keyword baseline on four fictional reports. It does not yet implement embeddings, chunks, a vector index, RAG, authentication, or evaluation. Next, inspect the intended [Incident Management event log](https://github.com/processminingdata/incidentmanagement), its fields, sample rows, provenance and license. Decide which questions the actual data supports before choosing structured analysis, document retrieval or both.
