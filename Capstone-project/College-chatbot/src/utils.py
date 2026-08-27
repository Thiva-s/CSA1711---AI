import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st
from dotenv import load_dotenv
from src.config import AppConfig, get_config, DEFAULT_MODELS


load_dotenv()


def save_config_to_session(config: AppConfig):
    st.session_state["app_config"] = config


def load_config_from_session() -> Optional[AppConfig]:
    if "app_config" in st.session_state:
        return st.session_state["app_config"]
    return None


def save_config_to_file(config: AppConfig, filepath: str = "./config.json"):
    data = {
        "college": {
            "name": config.college.name,
            "urls": config.college.urls,
            "logo_path": config.college.logo_path,
        },
        "ai": {
            "provider": config.ai.provider,
            "model": config.ai.model,
            "temperature": config.ai.temperature,
            "max_tokens": config.ai.max_tokens,
            "streaming": config.ai.streaming,
        },
        "rag": {
            "chunk_size": config.rag.chunk_size,
            "chunk_overlap": config.rag.chunk_overlap,
            "top_k": config.rag.top_k,
            "max_crawl_depth": config.rag.max_crawl_depth,
            "max_pages": config.rag.max_pages,
            "request_timeout": config.rag.request_timeout,
        },
        "kb_status": {
            "knowledge_base_status": config.knowledge_base_status,
            "pages_crawled": config.pages_crawled,
            "chunks_created": config.chunks_created,
        },
    }
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_config_from_file(filepath: str = "./config.json") -> Optional[AppConfig]:
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    config = get_config()
    
    if "college" in data:
        config.college.name = data["college"].get("name", "")
        config.college.urls = data["college"].get("urls", [])
        config.college.logo_path = data["college"].get("logo_path")
    
    if "ai" in data:
        config.ai.provider = data["ai"].get("provider", "Groq")
        config.ai.model = data["ai"].get("model", config.ai.model)
        config.ai.temperature = data["ai"].get("temperature", 0.1)
        config.ai.max_tokens = data["ai"].get("max_tokens", 1024)
        config.ai.streaming = data["ai"].get("streaming", True)
    
    if "rag" in data:
        config.rag.chunk_size = data["rag"].get("chunk_size", 500)
        config.rag.chunk_overlap = data["rag"].get("chunk_overlap", 50)
        config.rag.top_k = data["rag"].get("top_k", 4)
        config.rag.max_crawl_depth = data["rag"].get("max_crawl_depth", 2)
        config.rag.max_pages = data["rag"].get("max_pages", 50)
        config.rag.request_timeout = data["rag"].get("request_timeout", 10)
    
    if "kb_status" in data:
        config.knowledge_base_status = data["kb_status"].get("knowledge_base_status", "Not Created")
        config.pages_crawled = data["kb_status"].get("pages_crawled", 0)
        config.chunks_created = data["kb_status"].get("chunks_created", 0)

    # Load optional environment configuration without ever saving API keys
    # back to config.json.
    env_provider = os.getenv("LLM_PROVIDER")
    env_model = os.getenv("LLM_MODEL")
    if env_provider:
        config.ai.provider = env_provider.strip().title()
    if env_model:
        config.ai.model = env_model.strip()

    env_key_name = "GROQ_API_KEY" if config.ai.provider.lower() == "groq" else "OPENAI_API_KEY"
    env_api_key = os.getenv(env_key_name, "").strip()
    if env_api_key and not env_api_key.startswith("your_"):
        config.ai.api_key = env_api_key
        config._api_key_session = env_api_key

    from src.config import migrate_model_name
    config.ai.model = migrate_model_name(config.ai.model)
    
    return config


def get_available_models(provider: str) -> list:
    return DEFAULT_MODELS.get(provider, [])


def validate_url(url: str) -> bool:
    from urllib.parse import urlparse
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def format_file_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.0f}m {seconds%60:.0f}s"
    else:
        return f"{seconds/3600:.0f}h {(seconds%3600)/60:.0f}m"


def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def get_status_color(status: str) -> str:
    colors = {
        "Ready": "🟢",
        "Not Created": "⚪",
        "Crawling": "🟡",
        "Processing": "🟡",
        "Error": "🔴",
    }
    return colors.get(status, "⚪")
