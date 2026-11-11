"""A small, dependency-free keyword search baseline for synthetic incidents."""
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

DATA = Path(__file__).parent / "data" / "incidents.json"
STOP = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "in", "is", "of", "on", "or", "the", "to", "was", "what", "were", "why", "with"}


def tokens(text):
    return [word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in STOP]


def search(query, documents, limit=3):
    """Rank by query-term coverage weighted by inverse document frequency."""
    query_terms = set(tokens(query))
    if not query_terms:
        return []
    indexed = [set(tokens(doc["title"] + " " + doc["text"])) for doc in documents]
    counts = Counter(term for terms in indexed for term in terms)
    results = []
    for doc, terms in zip(documents, indexed):
        matched = query_terms & terms
        score = sum(math.log((len(documents) + 1) / (counts[term] + 1)) + 1 for term in matched)
        if score:
            results.append((score, doc))
    return sorted(results, key=lambda item: (-item[0], item[1]["id"]))[:limit]


def main():
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        print('Usage: python3 search.py "checkout errors after deployment"')
        return
    documents = json.loads(DATA.read_text(encoding="utf-8"))
    results = search(query, documents)
    if not results:
        print("No matching incidents found.")
    for score, doc in results:
        print(f"[{doc['id']}] {doc['title']} (score: {score:.2f})")
        print(f"  Source: {doc['source']} | Service: {doc['service']} | Date: {doc['date']}")
        print(f"  {doc['text']}\n")


if __name__ == "__main__":
    main()
