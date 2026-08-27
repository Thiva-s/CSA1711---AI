import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class CollegeConfig:
    name: str = ""
    urls: List[str] = field(default_factory=list)
    logo_path: Optional[str] = None


@dataclass
class AIConfig:
    provider: str = "Groq"
    api_key: str = ""
    model: str = "llama-3.1-8b-instant"
    temperature: float = 0.1
    max_tokens: int = 1024
    streaming: bool = True


@dataclass
class RAGConfig:
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 4
    max_crawl_depth: int = 2
    max_pages: int = 50
    request_timeout: int = 10


@dataclass
class AppConfig:
    college: CollegeConfig = field(default_factory=CollegeConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    
    knowledge_base_status: str = "Not Created"
    pages_crawled: int = 0
    chunks_created: int = 0
    vector_db_path: str = "./vectorstore"
    data_dir: str = "./data/scraped"
    
    # Session state for non-persistent config
    _api_key_session: str = ""
    
    def validate_college_setup(self) -> List[str]:
        errors = []
        if not self.college.name.strip():
            errors.append("College name is required")
        if not self.college.urls:
            errors.append("At least one college website URL is required")
        else:
            for i, url in enumerate(self.college.urls):
                if not url.strip():
                    errors.append(f"URL {i+1} cannot be empty")
                elif not (url.startswith("http://") or url.startswith("https://")):
                    errors.append(f"URL {i+1} must be a valid HTTP/HTTPS URL")
        return errors
    
    def validate_ai_config(self) -> List[str]:
        errors = []
        if not self.ai.provider:
            errors.append("LLM provider must be selected")
        if not self.ai.api_key and not self._api_key_session:
            errors.append("API key is required")
        if not self.ai.model:
            errors.append("Model must be selected/entered")
        return errors
    
    def validate_kb_ready(self) -> List[str]:
        errors = []
        if self.knowledge_base_status != "Ready":
            errors.append("Knowledge base is not ready. Please build it first.")
        return errors


DEFAULT_MODELS = {
    "Groq": [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-120b",
        "qwen/qwen3.6-27b",
    ],
    "OpenAI": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ],
}


MODEL_REPLACEMENTS = {
    "llama-3.1-70b-versatile": "llama-3.3-70b-versatile",
    "llama-3.1-70b-specdec": "llama-3.3-70b-specdec",
    "mixtral-8x7b-32768": "llama-3.3-70b-versatile",
    "gemma2-9b-it": "llama-3.1-8b-instant",
}


def migrate_model_name(model: str) -> str:
    """Replace known retired Groq model IDs in saved/session config."""
    model = (model or "").strip()
    return MODEL_REPLACEMENTS.get(model, model)

DEFAULT_CONFIG = AppConfig()


def get_config() -> AppConfig:
    return DEFAULT_CONFIG


def reset_config():
    global DEFAULT_CONFIG
    DEFAULT_CONFIG = AppConfig()
