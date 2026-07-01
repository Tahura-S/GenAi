# Module 5 Practical: Semantic Search over Policy Documents

A from-scratch semantic search pipeline over sample HR/IT/Finance/Security
policy docs, with metadata filtering (department, document type, access
level). No LangChain, no managed vector DB -- built by hand so each piece
(chunking, embedding, indexing, filtering) is visible and swappable later.

## Pipeline

```
data/policies/*.md
    -> document_loader.py   load + split YAML front-matter from body
    -> parser.py             parse front-matter into metadata dict
    -> chunker.py             split by markdown section, recursive fallback if too long
    -> embedder.py            sentence-transformers (all-MiniLM-L6-v2, local, free)
    -> indexer.py             FAISS IndexFlatIP (cosine sim) + metadata.json sidecar
    -> search.py              CLI: embed query, top-k search, post-filter by metadata
```

FAISS has no built-in metadata store, so `metadata.json` is a parallel list:
`metadata[i]` describes the vector stored at index position `i` in
`faiss.index`. Filtering happens by over-fetching candidates from FAISS and
checking them against the metadata dict in Python.

## Setup

```bash
pip install -r requirements.txt
```

First run downloads the `all-MiniLM-L6-v2` embedding model (~90MB) from
Hugging Face and caches it locally.

## Usage

Build the index (run once, or whenever `data/policies/` changes):

```bash
python main.py
```

Search it:

```bash
python src/search.py
```

Example queries:

```
query> how many vacation days do I get
query> department=hr how many vacation days do I get
query> department=it password requirements
```

`department=`, `document_type=`, and `access_level=` are recognized as
filters; everything else in the line is treated as the search text.

## Troubleshooting

**`SSL: CERTIFICATE_VERIFY_FAILED` when the model downloads from
huggingface.co** -- some corporate/antivirus setups intercept TLS in a way
that breaks Python's bundled CA list for huggingface.co specifically (pypi.org
usually still works). `pip-system-certs` (already in requirements.txt) patches
Python to trust the OS certificate store instead and fixes this.
