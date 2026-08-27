# 🎓 AI College Assistant

A professional, Python-based AI chatbot for colleges and universities. Built with Streamlit, LangChain, ChromaDB, and RAG (Retrieval-Augmented Generation).

## ✨ Features

- **🔍 Automatic Web Crawling** - Provide college website URLs, the system automatically crawls, extracts, and indexes content
- **🧠 RAG-Powered Responses** - Uses ChromaDB vector database with semantic search for accurate answers
- **🤖 Multiple LLM Providers** - Supports Groq and OpenAI with easy extensibility
- **⚙️ Configurable Pipeline** - Adjust chunk size, overlap, retrieval count, crawl depth, and more
- **📚 Source Citations** - Every answer includes clickable source links to original pages
- **💾 Persistent Storage** - ChromaDB persists knowledge base between sessions
- **🔐 Secure API Handling** - Keys stored in session only, never saved to disk
- **🎨 Professional UI** - Clean, responsive Streamlit interface with sidebar configuration

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd college_ai_chatbot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run the Application

```bash
streamlit run app.py
```

### 4. Use the Assistant

1. **College Setup** - Enter college name and website URLs
2. **AI Configuration** - Select provider (Groq/OpenAI), enter API key, choose model
3. **RAG Settings** - Adjust parameters or use defaults
4. **Build Knowledge Base** - Click "🚀 Build Knowledge Base"
5. **Start Chatting** - Ask questions about the college!

## 📁 Project Structure

```
college_ai_chatbot/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── src/
│   ├── config.py         # Configuration management
│   ├── crawler.py        # Web crawling logic
│   ├── scraper.py        # Content extraction
│   ├── cleaner.py        # Text cleaning
│   ├── chunker.py        # Text chunking
│   ├── embeddings.py     # Embedding generation
│   ├── vector_db.py      # ChromaDB operations
│   ├── retriever.py      # RAG retrieval
│   ├── rag.py            # RAG pipeline
│   ├── prompts.py        # Prompt templates
│   └── utils.py          # Utility functions
├── data/
│   └── scraped/          # Crawled page storage
└── vectorstore/          # ChromaDB persistent storage
```

## ⚙️ Configuration

### College Setup
- **College Name** - Display name for the assistant
- **Website URLs** - One or more seed URLs to crawl (e.g., `https://college.edu`, `https://college.edu/admissions`)
- **Logo** - Optional college logo upload

### AI Configuration
- **Provider** - Groq (fast, free tier) or OpenAI
- **API Key** - Enter in UI (session-only, never persisted)
- **Model** - Select from available models per provider
- **Temperature** - 0.1 (recommended for factual QA)
- **Max Tokens** - 1024 (adjust for longer responses)
- **Streaming** - Enable for token-by-token response

### RAG Settings
| Parameter | Default | Description |
|-----------|---------|-------------|
| Chunk Size | 500 | Tokens per text chunk |
| Chunk Overlap | 50 | Overlap between chunks |
| Top K | 4 | Chunks retrieved per query |
| Max Crawl Depth | 2 | Link-following depth |
| Max Pages | 50 | Maximum pages to crawl |
| Request Timeout | 10s | HTTP request timeout |

## 🔑 API Keys

### Groq (Recommended - Free Tier)
1. Visit [console.groq.com](https://console.groq.com/keys)
2. Create account and generate API key
3. Supports current model IDs such as `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`, and `openai/gpt-oss-120b`. Check Groq's model list before using a custom ID.

### OpenAI
1. Visit [platform.openai.com](https://platform.openai.com/api-keys)
2. Create account and generate API key
3. Supports: GPT-4o, GPT-4o-mini, GPT-4, GPT-3.5

## 🎯 Usage Examples

```
"What courses are available in Computer Science?"
"How can I apply for admission to the MBA program?"
"What are the eligibility criteria for B.Tech?"
"Tell me about the placement statistics for 2023."
"What facilities are available on campus?"
"Are there any scholarships for international students?"
```

## 🏗️ Architecture

```
User Question
     ↓
Embedding (Sentence Transformers)
     ↓
ChromaDB Vector Search (Top-K)
     ↓
Relevant Chunks + Context
     ↓
LLM (Groq/OpenAI) → Streaming Response
     ↓
Sources Displayed with Links
```

**Knowledge Base Build Pipeline:**
```
URLs → Web Crawler → Content Extraction → Cleaning → Chunking → Embeddings → ChromaDB
```

## 🔒 Security

- API keys **never** saved to disk or vector database
- Keys only stored in Streamlit session state
- `.gitignore` prevents accidental credential commits
- Use `.env` for local development (not committed)

## 📦 Dependencies

Core:
- `streamlit` - Web UI framework
- `langchain` / `langchain-community` - LLM orchestration
- `langchain-groq` / `langchain-openai` - Provider integrations
- `chromadb` - Vector database
- `sentence-transformers` - Embeddings (all-MiniLM-L6-v2)
- `beautifulsoup4` / `lxml` - HTML parsing
- `requests` - HTTP client
- `tiktoken` - Token counting
- `html2text` - HTML to markdown
- `tqdm` - Progress bars

## 🛠️ Extending

### Add New LLM Provider
1. Add to `DEFAULT_MODELS` in `src/config.py`
2. Add provider logic in `src/rag.py` `_create_llm()`
3. Install corresponding `langchain-*` package

### Customize Prompts
Edit `src/prompts.py` for system prompt and RAG template

### Adjust Crawling
Modify `src/crawler.py` for custom link extraction or content targeting

## 📝 License

MIT License - Feel free to use for educational and commercial projects.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Open Pull Request

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No module named 'src'" | Run from project root: `streamlit run app.py` |
| ChromaDB errors | Delete `vectorstore/` and rebuild |
| Crawling fails | Check URLs are accessible, increase timeout |
| `Expected Embeddings to be non-empty list or numpy array, got []` | The selected pages returned no readable text, commonly because a site blocks automated requests (HTTP 403/Cloudflare). Remove that URL, use an accessible official page, or save the page content locally and add it as a supported source. |
| API key errors | Verify key is valid for selected provider |
| Slow responses | Reduce `max_pages`, `chunk_size`, or `top_k` |

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing UI framework
- [LangChain](https://langchain.com/) for LLM orchestration
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Sentence Transformers](https://www.sbert.net/) for embeddings
- [Groq](https://groq.com/) for fast LLM inference
