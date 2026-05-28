"""RAG (Retrieval-Augmented Generation) module for Chatty-My-Agent.

Indexes local files into a vector database and retrieves relevant chunks
to augment LLM prompts with your own data.
"""
import os
import hashlib
from pathlib import Path
from typing import Optional

VECTORDB_PATH = str(Path.home() / ".chatty-agent" / "vectordb")
SUPPORTED_EXTENSIONS = {".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml",
                        ".log", ".csv", ".html", ".css", ".java", ".c", ".cpp", ".h",
                        ".rs", ".go", ".sh", ".bat", ".ps1", ".sql", ".xml", ".ini", ".cfg", ".toml"}

# Knowledge mode
MODES = ["general", "local", "hybrid"]

_model = None
_collection = None


def _get_model():
    """Lazy-load the embedding model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_collection():
    """Lazy-load the ChromaDB collection."""
    global _collection
    if _collection is None:
        import chromadb
        client = chromadb.PersistentClient(path=VECTORDB_PATH)
        _collection = client.get_or_create_collection(
            name="local_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks by lines."""
    lines = text.split("\n")
    chunks = []
    current = []
    current_len = 0

    for line in lines:
        line_len = len(line.split())
        if current_len + line_len > chunk_size and current:
            chunks.append("\n".join(current))
            # Keep overlap
            overlap_lines = []
            overlap_len = 0
            for l in reversed(current):
                overlap_len += len(l.split())
                if overlap_len > overlap:
                    break
                overlap_lines.insert(0, l)
            current = overlap_lines
            current_len = overlap_len
        current.append(line)
        current_len += line_len

    if current:
        chunks.append("\n".join(current))

    return chunks


def index_file(file_path: str) -> int:
    """Index a single file. Returns number of chunks added."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {path.suffix}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return 0

    chunks = chunk_text(text)
    model = _get_model()
    collection = _get_collection()

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        chunk_id = hashlib.md5(f"{file_path}:{i}:{chunk[:50]}".encode()).hexdigest()
        embedding = model.encode(chunk).tolist()
        ids.append(chunk_id)
        documents.append(chunk)
        embeddings.append(embedding)
        metadatas.append({"source": str(path.absolute()), "chunk_index": i, "filename": path.name})

    collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    return len(chunks)


def index_folder(folder_path: str) -> dict:
    """Index all supported files in a folder recursively. Returns stats."""
    path = Path(folder_path)
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder_path}")

    ignore = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}
    stats = {"files": 0, "chunks": 0, "skipped": 0, "errors": []}

    for item in path.rglob("*"):
        if any(part in ignore for part in item.parts):
            continue
        if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                n = index_file(str(item))
                stats["files"] += 1
                stats["chunks"] += n
            except Exception as e:
                stats["errors"].append(f"{item}: {e}")
                stats["skipped"] += 1

    return stats


def search(query: str, n_results: int = 5) -> list[dict]:
    """Search the vector DB for relevant chunks."""
    model = _get_model()
    collection = _get_collection()

    if collection.count() == 0:
        return []

    query_embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)

    output = []
    for i in range(len(results["documents"][0])):
        output.append({
            "content": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "filename": results["metadatas"][0][i]["filename"],
            "distance": results["distances"][0][i] if results.get("distances") else None,
        })
    return output


def get_context_for_query(query: str, n_results: int = 5) -> str:
    """Get formatted context string from local knowledge for a query."""
    results = search(query, n_results)
    if not results:
        return ""

    context_parts = []
    for r in results:
        context_parts.append(f"[Source: {r['filename']}]\n{r['content']}")

    return "\n\n---\n\n".join(context_parts)


def list_indexed() -> dict:
    """List what's been indexed."""
    collection = _get_collection()
    count = collection.count()

    if count == 0:
        return {"count": 0, "sources": []}

    # Get unique sources
    all_meta = collection.get(include=["metadatas"])
    sources = set()
    for m in all_meta["metadatas"]:
        sources.add(m.get("source", "unknown"))

    return {"count": count, "sources": sorted(sources)}


def clear_index():
    """Clear all indexed data."""
    import chromadb
    client = chromadb.PersistentClient(path=VECTORDB_PATH)
    client.delete_collection("local_knowledge")
    global _collection
    _collection = None
