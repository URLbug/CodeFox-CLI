from pathlib import Path

import faiss
import numpy as np
from fastembed import TextEmbedding

from codefox.utils.helper import Helper


class LocalRAG:
    def __init__(self, embedding: str, files_path: str):
        self.all_files = Helper.get_all_files(files_path)
        self.model = TextEmbedding(embedding)
        self.index = None
        self.chunks: list[str] = []

    def build(self) -> None:
        texts = []

        for file in self.all_files:
            try:
                file = Path(file)
                content = file.read_text()
                texts.append(f"FILE: {file}\n{content}")
            except Exception:
                continue

        self.chunks = texts
        vectors = list(self.model.embed(texts))
        vectors_np = np.array(vectors).astype("float32")

        dim = vectors_np.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(vectors_np)

    def search(self, query: str, k: int = 5) -> list[str]:
        if self.index is None:
            return []

        q_vec = list(self.model.embed([query]))[0]
        q_vec = np.array([q_vec]).astype("float32")

        _, ids = self.index.search(q_vec, k)

        return [self.chunks[i] for i in ids[0]]
