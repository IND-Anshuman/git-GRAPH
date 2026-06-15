"""Embedding generator for capabilities."""

import hashlib
from typing import List, Any

class CapabilityEmbedding:
    """Generates stable vector embeddings from capability metadata to support semantic GraphRAG search."""

    def generate_embedding(self, capability: Any) -> List[float]:
        """
        Generates a 16-dimensional deterministic floating-point vector using SHA256 hashes of capability text.
        This provides a lightweight, pure-Python mock representation of embeddings.
        """
        raw_text = f"{capability.name} {capability.description} {' '.join(capability.concepts)}"
        hash_bytes = hashlib.sha256(raw_text.encode("utf-8")).digest()
        embedding = []
        for i in range(16):
            # Read two bytes to form a float in [0.0, 1.0]
            val = (hash_bytes[i * 2] + hash_bytes[i * 2 + 1] * 256) / 65535.0
            embedding.append(round(val, 4))
        return embedding
