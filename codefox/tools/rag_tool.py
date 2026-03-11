from typing import Callable

from codefox.utils.local_rag import LocalRAG
from codefox.utils.parser import Parser
from codefox.tools.base_tool import BaseTool


class RagTool(BaseTool):
    def __init__(self, rag: LocalRAG, max_rag_chars: int):
        self.rag = rag
        self.max_rag_chars = max_rag_chars

    def get_tool(self) -> Callable:
        def search_knowledge_base(query: str) -> str:
            if not self.rag:
                return "None RAG"

            return Parser.get_files_context(
                self.rag, 
                query, 
                k=18,
                max_rag_chars=self.max_rag_chars
            )
         
        return search_knowledge_base