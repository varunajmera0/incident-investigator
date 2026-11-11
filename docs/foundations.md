# Foundations: retrieval and RAG

These notes accompany the early Incident Investigator learning project. Examples are fictional.

## Retrieval and RAG

Retrieval finds potentially relevant information for a question. Retrieval-augmented generation (RAG) supplies retrieved information to a language model to help it generate an answer. A retrieval result is evidence to inspect, not proof of a current incident's cause. Citations let a reader check the original source.

## Keyword search

Keyword search matches terms. It can be useful for identifiers such as error codes, but its effectiveness depends on how the index tokenizes those identifiers. Exact matching can miss synonyms and different wording. The current program uses a small stop-word list and inverse-document-frequency-weighted term matching; it does not stem words, so `fail` and `failed` are distinct.

## Semantic search and embeddings

An embedding model represents text as a vector. Search can compare a query vector with document vectors to find candidates with related meaning, even where words differ. Similarity is not evidence of correctness. Documents and queries must use compatible embedding models and configurations. Semantic search is a planned alternative, not implemented here.

## Hybrid search

Hybrid search combines different retrieval methods, commonly keyword and semantic search. Reciprocal rank fusion is one possible way to combine ranked lists using rank positions. A result found by only one method need not be discarded. Hybrid search adds indexing and query complexity and should be evaluated against simpler alternatives.

## Chunking

Chunking splits long documents into smaller pieces for retrieval. Small chunks may lose context; large chunks may contain irrelevant material and use more model tokens. Section-based splitting preserves useful structure; overlap can help around boundaries but can create duplicates and increase storage. Preserve source identifiers and permissions for every chunk. No chunking is implemented yet.

## Interview practice

**Why begin with keyword search?** It is an explainable, inexpensive baseline and can match exact identifiers well. Measure representative queries before adding complexity.

**Why use RAG?** It supplies external evidence at request time. Retrieval may miss the right evidence, and the model can still misinterpret it or generate unsupported claims.

**How do you choose a retrieval approach?** Evaluate keyword, semantic, and hybrid retrieval on labeled representative questions; compare retrieval quality, latency, cost, and access control behavior.

**How do you choose chunk size?** Start from document structure and user questions, then measure whether retrieved chunks contain sufficient evidence and context without excessive irrelevant or duplicated text.
