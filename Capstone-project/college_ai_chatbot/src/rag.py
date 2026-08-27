from typing import List, Dict, Optional, Generator
from dataclasses import dataclass
from src.retriever import Retriever, create_retriever
from src.vector_db import VectorDatabase
from src.prompts import get_rag_prompt, get_system_prompt
from src.config import get_config, AIConfig


@dataclass
class RAGResponse:
    answer: str
    sources: List[Dict]
    question: str


class RAGPipeline:
    def __init__(
        self,
        vector_db: VectorDatabase,
        ai_config: AIConfig,
        top_k: int = 4,
    ):
        self.vector_db = vector_db
        self.ai_config = ai_config
        self.top_k = top_k
        self.retriever = create_retriever(vector_db, top_k)
        self._llm = None
    
    def _get_llm(self):
        if self._llm is None:
            self._llm = self._create_llm()
        return self._llm
    
    def _create_llm(self):
        provider = self.ai_config.provider.lower()
        
        if provider == "groq":
            from langchain_groq import ChatGroq
            return ChatGroq(
                api_key=self.ai_config.api_key,
                model=self.ai_config.model,
                temperature=self.ai_config.temperature,
                max_tokens=self.ai_config.max_tokens,
                streaming=self.ai_config.streaming,
            )
        elif provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=self.ai_config.api_key,
                model=self.ai_config.model,
                temperature=self.ai_config.temperature,
                max_tokens=self.ai_config.max_tokens,
                streaming=self.ai_config.streaming,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.ai_config.provider}")
    
    def query(self, question: str) -> RAGResponse:
        retrieved = self.retriever.retrieve(question)
        sources = self.retriever.format_sources(retrieved)
        
        context = "\n\n".join([r["content"] for r in retrieved])
        
        prompt = get_rag_prompt().format(
            context=context,
            question=question,
        )
        
        llm = self._get_llm()
        response = llm.invoke(prompt)
        
        answer = response.content if hasattr(response, "content") else str(response)
        
        return RAGResponse(
            answer=answer,
            sources=sources,
            question=question,
        )
    
    def query_stream(self, question: str) -> Generator[str, None, RAGResponse]:
        retrieved = self.retriever.retrieve(question)
        sources = self.retriever.format_sources(retrieved)
        
        context = "\n\n".join([r["content"] for r in retrieved])
        
        prompt = get_rag_prompt().format(
            context=context,
            question=question,
        )
        
        llm = self._get_llm()
        
        full_answer = ""
        for chunk in llm.stream(prompt):
            content = chunk.content if hasattr(chunk, "content") else str(chunk)
            full_answer += content
            yield content
        
        return RAGResponse(
            answer=full_answer,
            sources=sources,
            question=question,
        )


def create_rag_pipeline(
    vector_db: VectorDatabase,
    ai_config: AIConfig,
    top_k: int = 4,
) -> RAGPipeline:
    return RAGPipeline(vector_db, ai_config, top_k)
