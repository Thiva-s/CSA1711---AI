from langchain_core.prompts import PromptTemplate


def get_system_prompt() -> str:
    return """You are an AI College Assistant, a knowledgeable and helpful chatbot designed to answer questions about colleges and universities.

Your role is to provide accurate, helpful, and concise information based on the college's official website content that has been provided to you.

Guidelines:
1. Answer questions using ONLY the provided context from the college website
2. If the information is not in the context, clearly state that you don't have that information
3. Be specific and reference the relevant sections/pages when possible
4. Keep responses concise but complete
5. Use a friendly, professional tone
6. If asked about admissions, courses, placements, or other specific topics, provide structured information
7. Always cite your sources by mentioning the relevant page/section"""


def get_rag_prompt() -> PromptTemplate:
    template = """{system_prompt}

Context from college website:
{context}

Question: {question}

Answer:"""
    
    return PromptTemplate(
        template=template,
        input_variables=["system_prompt", "context", "question"],
        partial_variables={"system_prompt": get_system_prompt()},
    )


def get_welcome_message(college_name: str) -> str:
    return f"""🎓 **AI College Assistant - {college_name}**

Welcome! I'm your AI assistant for {college_name}. I can help you with information about:

- **Courses & Programs** - Available degrees, specializations, curriculum details
- **Admissions** - Application process, eligibility, deadlines, required documents
- **Placements** - Placement statistics, top recruiters, salary packages
- **Departments & Faculty** - Academic departments, research areas, faculty profiles
- **Campus Life** - Facilities, hostels, clubs, events, student activities
- **Fees & Scholarships** - Fee structure, scholarship opportunities, financial aid
- **Contact Information** - Important contacts, office hours, location

**Example questions you can ask:**
- "What courses are available in the Computer Science department?"
- "How can I apply for admission to the MBA program?"
- "What are the eligibility criteria for B.Tech?"
- "Tell me about the placement statistics for 2023."
- "What facilities are available on campus?"
- "Are there any scholarships for international students?"

Ask me anything about {college_name}!"""


def get_error_message(error_type: str) -> str:
    messages = {
        "no_kb": "⚠ Knowledge base is not ready. Please build the knowledge base first by clicking 'Build Knowledge Base' in the sidebar.",
        "no_api_key": "⚠ Please enter your API key in the AI Configuration section before starting the chat.",
        "no_urls": "⚠ Please add at least one college website URL in the College Setup section.",
        "crawl_failed": "⚠ Failed to crawl the website. Please check the URLs and try again.",
        "embedding_failed": "⚠ Failed to generate embeddings. Please check your configuration.",
        "llm_error": "⚠ Error communicating with the LLM. Please check your API key and model selection.",
        "generic": "⚠ An error occurred. Please try again or check your configuration.",
    }
    return messages.get(error_type, messages["generic"])