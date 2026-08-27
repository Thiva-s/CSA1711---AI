import tiktoken
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    metadata: Dict
    token_count: int
    chunk_index: int


class TextChunker:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict] = None,
    ) -> List[TextChunk]:
        if metadata is None:
            metadata = {}
        
        tokens = self.encoding.encode(text)
        
        if len(tokens) <= self.chunk_size:
            return [TextChunk(
                content=text,
                metadata=metadata,
                token_count=len(tokens),
                chunk_index=0,
            )]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = chunk_index
            chunk_metadata["token_start"] = start
            chunk_metadata["token_end"] = end
            
            chunks.append(TextChunk(
                content=chunk_text,
                metadata=chunk_metadata,
                token_count=len(chunk_tokens),
                chunk_index=chunk_index,
            ))
            
            chunk_index += 1
            start += self.chunk_size - self.chunk_overlap
            
            if start >= len(tokens):
                break
        
        return chunks
    
    def chunk_by_paragraphs(
        self,
        text: str,
        metadata: Optional[Dict] = None,
    ) -> List[TextChunk]:
        if metadata is None:
            metadata = {}
        
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_tokens = self.count_tokens(para)
            
            if current_tokens + para_tokens > self.chunk_size and current_chunk:
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_index"] = chunk_index
                
                chunks.append(TextChunk(
                    content=current_chunk.strip(),
                    metadata=chunk_metadata,
                    token_count=current_tokens,
                    chunk_index=chunk_index,
                ))
                
                chunk_index += 1
                
                overlap_tokens = self.encoding.encode(current_chunk)[-self.chunk_overlap:]
                current_chunk = self.encoding.decode(overlap_tokens) + "\n\n" + para
                current_tokens = self.count_tokens(current_chunk)
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
                current_tokens = self.count_tokens(current_chunk)
        
        if current_chunk:
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = chunk_index
            chunks.append(TextChunk(
                content=current_chunk.strip(),
                metadata=chunk_metadata,
                token_count=current_tokens,
                chunk_index=chunk_index,
            ))
        
        return chunks
    
    def chunk_pages(
        self,
        pages: List[Dict],
    ) -> List[TextChunk]:
        all_chunks = []
        global_index = 0
        
        for page in pages:
            metadata = {
                "source_url": page.get("url", ""),
                "source_title": page.get("title", ""),
                "page_depth": page.get("depth", 0),
            }
            
            text = page.get("content", "") or page.get("text", "") or page.get("markdown", "")
            
            if not text.strip():
                continue
            
            page_chunks = self.chunk_by_paragraphs(text, metadata)
            
            for chunk in page_chunks:
                chunk.metadata["global_index"] = global_index
                chunk.chunk_index = global_index
                global_index += 1
            
            all_chunks.extend(page_chunks)
        
        return all_chunks


def create_chunks(
    pages: List[Dict],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[TextChunk]:
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_pages(pages)