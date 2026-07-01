import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from datetime import datetime

# -----------------------------
# 1. Sample Policy Documents
# -----------------------------
documents = [
    {
        "id": 1,
        "title": "Leave Policy",
        "text": "Employees are entitled to 24 paid leave days annually. Leave must be applied 7 days in advance.",
        "department": "HR",
        "document_type": "Policy",
        "access_level": "Public",
        "effective_date": "2025-01-10"
    },
    {
        "id": 2,
        "title": "Attendance Policy",
        "text": "Employees must mark attendance daily. Late arrival beyond 15 minutes is considered half day leave.",
        "department": "HR",
        "document_type": "Policy",
        "access_level": "Public",
        "effective_date": "2025-02-01"
    },
    {
        "id": 3,
        "title": "Server Access Rules",
        "text": "Only authorized IT staff can access production servers. All access is logged and monitored.",
        "department": "IT",
        "document_type": "Policy",
        "access_level": "Confidential",
        "effective_date": "2025-03-15"
    },
    {
        "id": 4,
        "title": "Data Backup Policy",
        "text": "All critical data must be backed up daily. Backups are stored in encrypted format.",
        "department": "IT",
        "document_type": "Policy",
        "access_level": "Confidential",
        "effective_date": "2025-04-20"
    },
    {
        "id": 5,
        "title": "Expense Reimbursement",
        "text": "Employees can claim business expenses within 30 days with valid receipts.",
        "department": "Finance",
        "document_type": "Policy",
        "access_level": "Public",
        "effective_date": "2025-01-25"
    },
    {
        "id": 6,
        "title": "Budget Approval Process",
        "text": "All departmental budgets must be approved by finance head before execution.",
        "department": "Finance",
        "document_type": "Policy",
        "access_level": "Internal",
        "effective_date": "2025-03-01"
    },
]

df = pd.DataFrame(documents)

# -----------------------------
# 2. Load Embedding Model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# 3. Create Embeddings
# -----------------------------
texts = df["title"] + ". " + df["text"]
embeddings = model.encode(texts.tolist(), convert_to_numpy=True)

dimension = embeddings.shape[1]

# -----------------------------
# 4. Build FAISS Index
# -----------------------------
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# -----------------------------
# 5. Metadata Filtering Function
# -----------------------------
def filter_documents(df, query_filters):
    filtered_df = df.copy()

    for key, value in query_filters.items():
        if value is not None:
            if isinstance(value, list):
                filtered_df = filtered_df[filtered_df[key].isin(value)]
            else:
                filtered_df = filtered_df[filtered_df[key] == value]

    return filtered_df


# -----------------------------
# 6. Semantic Search Function
# -----------------------------
def semantic_search(query, filters=None, top_k=3):
    if filters is None:
        filters = {}

    filtered_df = filter_documents(df, filters)

    if len(filtered_df) == 0:
        return []

    filtered_indices = filtered_df.index.tolist()

    filtered_embeddings = embeddings[filtered_indices]

    temp_index = faiss.IndexFlatL2(dimension)
    temp_index.add(filtered_embeddings)

    query_embedding = model.encode([query])

    distances, indices = temp_index.search(query_embedding, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        doc = filtered_df.iloc[idx]
        results.append({
            "title": doc["title"],
            "text": doc["text"],
            "department": doc["department"],
            "score": float(distances[0][i])
        })

    return results


# -----------------------------
# 7. Run Example Queries
# -----------------------------
if __name__ == "__main__":

    query = "How many leave days are allowed?"
    
    filters = {
        "department": "HR",
        "access_level": "Public"
    }

    results = semantic_search(query, filters)

    print("\nTop Results:\n")
    for r in results:
        print("Title:", r["title"])
        print("Score:", r["score"])
        print("Text:", r["text"])
        print("-" * 50)