"""
RAG service — vector knowledge base for resume optimization.
Stores resume examples, JD templates, and optimization history.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import settings
from services.embedding_service import embedding_service


class RAGService:
    """Vector knowledge base for resume optimization context."""

    COLLECTIONS = ["resume_examples", "jd_templates", "optimization_history"]

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or settings.RAG_CHROMA_PATH
        self._client = None
        self._enabled = False

    def _init_client(self):
        """Lazy-init ChromaDB client."""
        if self._client is not None:
            return
        try:
            import chromadb
            os.makedirs(self.persist_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_dir)
            self._enabled = True
            # Ensure collections exist
            for name in self.COLLECTIONS:
                try:
                    self._client.get_collection(name)
                except ValueError:
                    self._client.create_collection(name)
        except ImportError:
            self._enabled = False

    @property
    def enabled(self) -> bool:
        self._init_client()
        return self._enabled and settings.RAG_ENABLED

    def add_resume_example(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a high-quality resume example to the knowledge base."""
        return self._add_to_collection("resume_examples", text, metadata)

    def add_jd_template(self, jd_text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a JD template to the knowledge base."""
        return self._add_to_collection("jd_templates", jd_text, metadata)

    def add_optimization_result(
        self, original: str, optimized: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store optimization result for future reference."""
        text = f"ORIGINAL:\n{original}\n\nOPTIMIZED:\n{optimized}"
        meta = {
            "source": "user_optimization",
            "created_at": datetime.utcnow().isoformat(),
            **(metadata or {}),
        }
        return self._add_to_collection("optimization_history", text, meta)

    def search_similar(
        self,
        query: str,
        collection: str = "resume_examples",
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar content in the knowledge base."""
        if not self.enabled:
            return []

        self._init_client()
        try:
            col = self._client.get_collection(collection)
            results = col.query(
                query_texts=[query],
                n_results=min(top_k, 20),
                where=filter,
            )
            items = []
            for i in range(len(results["ids"][0])):
                items.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": results["distances"][0][i] if results["distances"] else 0,
                })
            return items
        except Exception as e:
            print(f"[RAG] Search failed: {e}")
            return []

    def get_optimization_context(
        self,
        resume_text: str,
        jd_text: Optional[str] = None,
    ) -> str:
        """
        Get RAG-enhanced context for prompt injection.

        Returns a formatted string with relevant examples from the knowledge base.
        """
        if not self.enabled:
            return ""

        parts = []

        # 1. Similar resume examples
        examples = self.search_similar(resume_text, "resume_examples", top_k=2)
        if examples:
            parts.append("## 参考优秀简历片段")
            for i, ex in enumerate(examples, 1):
                parts.append(f"### 示例 {i}\n{ex['text'][:500]}")

        # 2. Similar JD templates (if JD provided)
        if jd_text:
            templates = self.search_similar(jd_text, "jd_templates", top_k=2)
            if templates:
                parts.append("## 参考 JD 模板")
                for i, t in enumerate(templates, 1):
                    parts.append(f"### JD 模板 {i}\n{t['text'][:500]}")

        # 3. Similar optimization history
        history = self.search_similar(resume_text, "optimization_history", top_k=3)
        if history:
            parts.append("## 参考历史优化")
            for i, h in enumerate(history, 1):
                parts.append(f"### 历史优化 {i}\n{h['text'][:500]}")

        return "\n\n".join(parts)

    def get_stats(self) -> Dict[str, int]:
        """Get knowledge base statistics."""
        if not self.enabled:
            return {name: 0 for name in self.COLLECTIONS}

        self._init_client()
        stats = {}
        for name in self.COLLECTIONS:
            try:
                col = self._client.get_collection(name)
                stats[name] = col.count()
            except ValueError:
                stats[name] = 0
        return stats

    def _add_to_collection(
        self, collection: str, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Internal: add text to a collection."""
        if not self.enabled:
            return False

        self._init_client()
        try:
            col = self._client.get_collection(collection)
            from uuid import uuid4
            col.add(
                ids=[uuid4().hex[:12]],
                documents=[text],
                metadatas=[metadata or {"source": "manual"}],
            )
            return True
        except Exception as e:
            print(f"[RAG] Add to {collection} failed: {e}")
            return False


# Global singleton
rag_service = RAGService()