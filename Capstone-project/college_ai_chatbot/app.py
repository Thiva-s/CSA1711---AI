import streamlit as st
import os
import json
import time
from pathlib import Path
from typing import List, Optional, Dict

from src.config import (
    AppConfig, get_config, DEFAULT_MODELS, DEFAULT_CONFIG, migrate_model_name
)
from src.crawler import crawl_website, CrawledPage
from src.cleaner import clean_content
from src.chunker import create_chunks, TextChunk
from src.embeddings import generate_embeddings
from src.vector_db import create_vector_db, VectorDatabase
from src.rag import create_rag_pipeline, RAGResponse
from src.prompts import get_welcome_message, get_error_message
from src.utils import (
    save_config_to_session, load_config_from_session,
    save_config_to_file, load_config_from_file,
    get_available_models, validate_url, get_status_color
)


st.set_page_config(
    page_title="AI College Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_session_state():
    if "config" not in st.session_state:
        config = load_config_from_file()
        if config is None:
            config = get_config()
        st.session_state.config = config

    # Migrate an old model kept in an existing Streamlit session.
    st.session_state.config.ai.model = migrate_model_name(
        st.session_state.config.ai.model
    )
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "kb_building" not in st.session_state:
        st.session_state.kb_building = False
    
    if "kb_progress" not in st.session_state:
        st.session_state.kb_progress = {"current": 0, "total": 0, "status": "", "current_url": ""}
    
    if "vector_db" not in st.session_state:
        st.session_state.vector_db = None
    
    if "rag_pipeline" not in st.session_state:
        st.session_state.rag_pipeline = None
    
    # Auto-load vector DB and RAG pipeline if KB is ready
    config = st.session_state.config
    if config.knowledge_base_status == "Ready" and st.session_state.vector_db is None:
        try:
            vector_db = create_vector_db(config.vector_db_path, "college_knowledge")
            info = vector_db.get_collection_info()
            if info["count"] > 0:
                st.session_state.vector_db = vector_db
                st.session_state.rag_pipeline = create_rag_pipeline(
                    vector_db=vector_db,
                    ai_config=config.ai,
                    top_k=config.rag.top_k,
                )
        except Exception:
            pass


def render_sidebar():
    config = st.session_state.config
    
    with st.sidebar:
        st.markdown("## 🎓 AI College Assistant")
        st.markdown("---")
        
        render_college_setup(config)
        st.markdown("---")
        render_ai_config(config)
        st.markdown("---")
        render_rag_settings(config)
        st.markdown("---")
        render_knowledge_base_status(config)
        st.markdown("---")
        render_action_buttons(config)


def render_college_setup(config: AppConfig):
    st.markdown("### ⚙ College Setup")
    
    # College Name
    college_name = st.text_input(
        "College Name",
        value=config.college.name,
        placeholder="Enter college name (e.g., Saveetha University)",
        key="college_name",
    )
    config.college.name = college_name
    
    # College Logo
    logo_file = st.file_uploader(
        "College Logo (Optional)",
        type=["png", "jpg", "jpeg", "svg"],
        key="college_logo",
    )
    if logo_file:
        logo_path = f"./data/logo_{logo_file.name}"
        Path("./data").mkdir(exist_ok=True)
        with open(logo_path, "wb") as f:
            f.write(logo_file.getbuffer())
        config.college.logo_path = logo_path
        st.image(logo_path, width=100)
    elif config.college.logo_path and Path(config.college.logo_path).exists():
        st.image(config.college.logo_path, width=100)
    
    st.markdown("#### College Website URLs")
    
    for i, url in enumerate(config.college.urls):
        col1, col2 = st.columns([5, 1])
        with col1:
            new_url = st.text_input(
                f"URL {i+1}",
                value=url,
                placeholder="https://college.edu/page",
                key=f"url_{i}",
                label_visibility="collapsed",
            )
            config.college.urls[i] = new_url
        with col2:
            if st.button("🗑", key=f"del_url_{i}", help="Remove URL"):
                config.college.urls.pop(i)
                st.rerun()
    
    if st.button("➕ Add Another URL", use_container_width=True):
        config.college.urls.append("")
        st.rerun()
    
    if config.college.urls:
        if st.button("🗑 Clear All URLs", use_container_width=True, type="secondary"):
            config.college.urls = []
            st.rerun()


def render_ai_config(config: AppConfig):
    st.markdown("### 🤖 AI Configuration")
    
    # LLM Provider
    provider = st.selectbox(
        "LLM Provider",
        options=list(DEFAULT_MODELS.keys()),
        index=list(DEFAULT_MODELS.keys()).index(config.ai.provider) if config.ai.provider in DEFAULT_MODELS else 0,
        key="llm_provider",
    )
    config.ai.provider = provider
    
    # API Key
    api_key = st.text_input(
        "API Key",
        value="",
        type="password",
        placeholder="Enter your API key",
        key="api_key",
        help="Your API key is stored only in this session and never saved to disk",
    )
    if api_key:
        config.ai.api_key = api_key
        config._api_key_session = api_key
    
    remember_key = st.checkbox("Remember for this session", value=True, key="remember_key")
    
    # Model Selection
    available_models = get_available_models(provider)
    custom_model_option = "Custom model ID..."
    model_options = [*available_models, custom_model_option]
    current_model = migrate_model_name(config.ai.model)
    selected_model = (
        current_model if current_model in available_models else custom_model_option
    )
    model = st.selectbox(
        "Model",
        options=model_options,
        index=model_options.index(selected_model),
        key="model_select",
    )
    if model == custom_model_option:
        config.ai.model = st.text_input(
            "Custom model ID",
            value=current_model if current_model not in available_models else "",
            placeholder="e.g. openai/gpt-oss-120b",
            key="custom_model_id",
            help="Use an active model ID from Groq's model list.",
        ).strip()
    else:
        config.ai.model = model
    
    # Advanced AI Settings
    with st.expander("🔧 Advanced AI Settings"):
        config.ai.temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=config.ai.temperature,
            step=0.1,
            key="temperature",
            help="Lower values = more focused, higher = more creative",
        )
        config.ai.max_tokens = st.number_input(
            "Max Output Tokens",
            min_value=256,
            max_value=8192,
            value=config.ai.max_tokens,
            step=256,
            key="max_tokens",
        )
        config.ai.streaming = st.checkbox(
            "Streaming",
            value=config.ai.streaming,
            key="streaming",
            help="Stream response token by token",
        )

    # Recreate the cached pipeline when the user changes the model, provider,
    # API key, or generation settings. Otherwise an already-created LLM can
    # continue sending requests to the old model.
    ai_signature = (
        config.ai.provider,
        config.ai.api_key or config._api_key_session,
        config.ai.model,
        config.ai.temperature,
        config.ai.max_tokens,
        config.ai.streaming,
    )
    if st.session_state.get("ai_signature") != ai_signature:
        if st.session_state.vector_db is not None:
            st.session_state.rag_pipeline = create_rag_pipeline(
                vector_db=st.session_state.vector_db,
                ai_config=config.ai,
                top_k=config.rag.top_k,
            )
        else:
            st.session_state.rag_pipeline = None
        st.session_state.ai_signature = ai_signature


def render_rag_settings(config: AppConfig):
    st.markdown("### 🔧 RAG Settings")
    
    config.rag.chunk_size = st.number_input(
        "Chunk Size",
        min_value=100,
        max_value=2000,
        value=config.rag.chunk_size,
        step=50,
        key="chunk_size",
        help="Size of text chunks for embedding",
    )
    config.rag.chunk_overlap = st.number_input(
        "Chunk Overlap",
        min_value=0,
        max_value=500,
        value=config.rag.chunk_overlap,
        step=10,
        key="chunk_overlap",
        help="Overlap between consecutive chunks",
    )
    config.rag.top_k = st.number_input(
        "Top K (Retrieved Chunks)",
        min_value=1,
        max_value=20,
        value=config.rag.top_k,
        step=1,
        key="top_k",
        help="Number of chunks to retrieve for each query",
    )
    config.rag.max_crawl_depth = st.number_input(
        "Maximum Crawl Depth",
        min_value=1,
        max_value=5,
        value=config.rag.max_crawl_depth,
        step=1,
        key="max_crawl_depth",
        help="How deep to follow links from seed URLs",
    )
    config.rag.max_pages = st.number_input(
        "Maximum Pages",
        min_value=10,
        max_value=500,
        value=config.rag.max_pages,
        step=10,
        key="max_pages",
        help="Maximum number of pages to crawl",
    )
    config.rag.request_timeout = st.number_input(
        "Request Timeout (seconds)",
        min_value=5,
        max_value=60,
        value=config.rag.request_timeout,
        step=1,
        key="request_timeout",
        help="Timeout for each HTTP request",
    )


def render_knowledge_base_status(config: AppConfig):
    st.markdown("### 📊 Knowledge Base Status")
    
    status_colors = {
        "Not Created": "⚪",
        "Crawling": "🟡",
        "Processing": "🟡",
        "Ready": "🟢",
        "Error": "🔴",
    }
    
    status_icon = status_colors.get(config.knowledge_base_status, "⚪")
    
    st.markdown(f"""
    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; background: #fafafa; color: #000;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <span style="font-size: 20px;">{status_icon}</span>
            <strong style="font-size: 16px;">{config.knowledge_base_status}</strong>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 14px;">
            <div><strong>Pages:</strong> {config.pages_crawled}</div>
            <div><strong>Chunks:</strong> {config.chunks_created}</div>
            <div><strong>Database:</strong> ChromaDB</div>
            <div><strong>Status:</strong> {'Connected' if config.knowledge_base_status == 'Ready' else 'Not Connected'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_action_buttons(config: AppConfig):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Configuration", use_container_width=True):
            save_config_to_file(config)
            save_config_to_session(config)
            st.success("Configuration saved!")
    
    with col2:
        if st.button("🔄 Reset All", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("")
    
    # Build Knowledge Base Button
    can_build = bool(config.college.name and config.college.urls)
    if st.button(
        "🚀 Build Knowledge Base",
        use_container_width=True,
        type="primary",
        disabled=not can_build or st.session_state.kb_building,
    ):
        build_knowledge_base(config)
    
    if not can_build and not st.session_state.kb_building:
        st.caption("⚠ Please provide college name and at least one URL")


def build_knowledge_base(config: AppConfig):
    st.session_state.kb_building = True
    st.session_state.kb_progress = {"current": 0, "total": config.rag.max_pages, "status": "Starting...", "current_url": ""}
    
    progress_container = st.empty()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(current: int, total: int, url: str):
        st.session_state.kb_progress = {
            "current": current,
            "total": total,
            "status": f"Crawling page {current}/{total}",
            "current_url": url,
        }
        progress_bar.progress(min(current / max(total, 1), 1.0))
        status_text.text(f"Crawling: {url[:60]}...")
    
    try:
        config.knowledge_base_status = "Crawling"
        
        # Step 1: Crawl
        crawl_failures = []
        pages = crawl_website(
            urls=[u for u in config.college.urls if u.strip()],
            max_depth=config.rag.max_crawl_depth,
            max_pages=config.rag.max_pages,
            timeout=config.rag.request_timeout,
            output_dir=config.data_dir,
            progress_callback=update_progress,
            failures=crawl_failures,
        )

        if crawl_failures:
            st.warning(
                "Some URLs could not be indexed. They may require JavaScript, "
                "block automated requests, or be temporarily unavailable."
            )
            with st.expander("Skipped URL details"):
                for failure in crawl_failures:
                    st.write(f"- {failure}")
        
        config.pages_crawled = len(pages)
        config.knowledge_base_status = "Processing"
        status_text.text(f"Processing {len(pages)} pages...")
        progress_bar.progress(0.3)

        if not pages:
            raise ValueError(
                "No pages could be downloaded. The configured website may be "
                "blocked by Cloudflare, require JavaScript, or be temporarily unavailable."
            )
        
        # Step 2: Clean and prepare
        cleaned_pages = []
        for page in pages:
            cleaned_content = clean_content(page.content)
            if cleaned_content.strip():
                cleaned_pages.append({
                    "url": page.url,
                    "title": page.title,
                    "content": cleaned_content,
                    "depth": page.depth,
                })
        
        progress_bar.progress(0.5)
        status_text.text("Chunking content...")

        if not cleaned_pages:
            raise ValueError(
                "The downloaded pages contained no readable text. Remove blocked URLs "
                "or add an accessible official college page."
            )
        
        # Step 3: Chunk
        chunks = create_chunks(
            cleaned_pages,
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.chunk_overlap,
        )
        
        config.chunks_created = len(chunks)
        progress_bar.progress(0.6)
        status_text.text(f"Generating embeddings for {len(chunks)} chunks...")

        if not chunks:
            raise ValueError(
                "No text chunks were created. The configured pages may be empty or blocked."
            )
        
        # Step 4: Embeddings
        texts = [chunk.content for chunk in chunks]
        embeddings = generate_embeddings(texts, batch_size=32)
        
        progress_bar.progress(0.8)
        status_text.text("Storing in ChromaDB...")
        
        # Step 5: Vector DB
        vector_db = create_vector_db(
            persist_directory=config.vector_db_path,
            collection_name="college_knowledge",
        )
        # All empty-content checks happen before this point, so replacing the
        # old collection cannot leave Chroma with an empty failed build.
        vector_db.delete_collection()
        vector_db.add_chunks(
            chunks=[{"content": c.content, "metadata": c.metadata} for c in chunks],
            embeddings=embeddings,
        )
        
        config.knowledge_base_status = "Ready"
        config.pages_crawled = len(pages)
        config.chunks_created = len(chunks)
        
        st.session_state.vector_db = vector_db
        st.session_state.rag_pipeline = create_rag_pipeline(
            vector_db=vector_db,
            ai_config=config.ai,
            top_k=config.rag.top_k,
        )
        
        progress_bar.progress(1.0)
        status_text.text("✅ Knowledge Base Ready!")
        
        st.success(f"✅ Knowledge Base Built Successfully!\n\nPages: {len(pages)}\nChunks: {len(chunks)}")
        
    except Exception as e:
        config.knowledge_base_status = "Error"
        st.error(f"❌ Error building knowledge base: {str(e)}")
    finally:
        st.session_state.kb_building = False
        save_config_to_file(config)
        save_config_to_session(config)
        time.sleep(1)
        st.rerun()


def render_chat_area():
    config = st.session_state.config
    
    # Header
    col1, col2 = st.columns([1, 6])
    with col1:
        if config.college.logo_path and Path(config.college.logo_path).exists():
            st.image(config.college.logo_path, width=60)
        else:
            st.markdown("# 🎓")
    with col2:
        st.markdown(f"# {config.college.name or 'AI College Assistant'}")
    
    st.markdown("---")
    
    # Check if ready to chat
    kb_ready = config.knowledge_base_status == "Ready"
    ai_ready = bool(config.ai.api_key and config.ai.provider and config.ai.model)
    
    if not kb_ready:
        st.warning(get_error_message("no_kb"))
        return
    
    if not ai_ready:
        st.warning(get_error_message("no_api_key"))
        return
    
    # Welcome message
    if not st.session_state.messages:
        welcome = get_welcome_message(config.college.name)
        st.markdown(welcome)
    
    # Chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                render_sources(message["sources"])
    
    # Chat input
    if prompt := st.chat_input("Ask your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                rag = st.session_state.rag_pipeline
                for chunk in rag.query_stream(prompt):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                
                # Get sources
                retrieved = rag.retriever.retrieve(prompt)
                sources = rag.retriever.format_sources(retrieved)
                
                if sources:
                    render_sources(sources)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "sources": sources,
                })
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                response_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})


def render_sources(sources: List[Dict]):
    if not sources:
        return
    
    with st.expander("📚 Sources", expanded=False):
        for i, source in enumerate(sources, 1):
            st.markdown(f"**{i}. [{source['title']}]({source['url']})**")
            st.caption(f"Relevance: {source['score']:.2%}")


def main():
    init_session_state()
    
    # Custom CSS
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
    }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
    div[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    .stNumberInput > div > div > input {
        border-radius: 8px;
    }
    .stSelectbox > div > div > div {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    render_sidebar()
    render_chat_area()


if __name__ == "__main__":
    main()
