import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict, Optional
import time
from dataclasses import dataclass
from pathlib import Path
import json
from tqdm import tqdm
import hashlib


@dataclass
class CrawledPage:
    url: str
    title: str
    content: str
    links: List[str]
    depth: int
    timestamp: float


class WebCrawler:
    def __init__(
        self,
        base_urls: List[str],
        max_depth: int = 2,
        max_pages: int = 50,
        timeout: int = 10,
        delay: float = 0.5,
    ):
        self.base_urls = base_urls
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.timeout = timeout
        self.delay = delay
        
        self.visited: Set[str] = set()
        self.pages: List[CrawledPage] = []
        self.failures: List[str] = []
        self.base_domains = [urlparse(url).netloc for url in base_urls]
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
    
    def is_valid_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            if parsed.netloc not in self.base_domains:
                return False
            if any(url.endswith(ext) for ext in [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".rar", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico", ".css", ".js", ".woff", ".woff2", ".ttf", ".eot"]):
                return False
            return True
        except Exception:
            return False
    
    def normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.rstrip('/') or '/'
        return f"{parsed.scheme}://{parsed.netloc}{path}"
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        try:
            time.sleep(self.delay)
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code >= 400:
                self.failures.append(f"{url} — HTTP {response.status_code}")
                return None
            
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type.lower():
                self.failures.append(f"{url} — response is not HTML ({content_type or 'unknown type'})")
                return None
            
            return BeautifulSoup(response.content, "lxml")
        except requests.exceptions.Timeout:
            self.failures.append(f"{url} — request timed out")
            return None
        except requests.exceptions.ConnectionError:
            self.failures.append(f"{url} — connection failed")
            return None
        except requests.exceptions.TooManyRedirects:
            self.failures.append(f"{url} — too many redirects")
            return None
        except requests.exceptions.RequestException:
            self.failures.append(f"{url} — request failed")
            return None
        except Exception:
            self.failures.append(f"{url} — unexpected crawler error")
            return None
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(base_url, href)
            normalized = self.normalize_url(full_url)
            if self.is_valid_url(normalized):
                links.append(normalized)
        return list(set(links))
    
    def extract_content(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe", "form", "button", "input", "select", "textarea"]):
            tag.decompose()
        
        title = ""
        if soup.title:
            title = soup.title.string.strip() if soup.title.string else ""
        elif soup.find("h1"):
            title = soup.find("h1").get_text().strip()
        
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=lambda x: x and ("content" in x.lower() or "main" in x.lower())) or soup.body
        
        if main_content:
            content = main_content.get_text(separator="\n", strip=True)
        else:
            content = soup.get_text(separator="\n", strip=True)
        
        return {"title": title, "content": content}
    
    def crawl(self, progress_callback=None) -> List[CrawledPage]:
        queue = [(url, 0) for url in self.base_urls]
        
        pbar = tqdm(total=self.max_pages, desc="Crawling pages")
        
        while queue and len(self.pages) < self.max_pages:
            url, depth = queue.pop(0)
            normalized = self.normalize_url(url)
            
            if normalized in self.visited or depth > self.max_depth:
                continue
            
            self.visited.add(normalized)
            
            soup = self.fetch_page(normalized)
            if not soup:
                continue
            
            extracted = self.extract_content(soup, normalized)
            links = self.extract_links(soup, normalized)
            
            page = CrawledPage(
                url=normalized,
                title=extracted["title"],
                content=extracted["content"],
                links=links,
                depth=depth,
                timestamp=time.time(),
            )
            self.pages.append(page)
            
            pbar.update(1)
            pbar.set_description(f"Crawled: {normalized[:50]}...")
            
            if progress_callback:
                progress_callback(len(self.pages), self.max_pages, normalized)
            
            if depth < self.max_depth:
                for link in links:
                    if link not in self.visited and len(self.pages) < self.max_pages:
                        queue.append((link, depth + 1))
        
        pbar.close()
        return self.pages
    
    def save_pages(self, output_dir: str):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for i, page in enumerate(self.pages):
            filename = f"page_{i:04d}_{hashlib.md5(page.url.encode()).hexdigest()[:8]}.json"
            filepath = Path(output_dir) / filename
            data = {
                "url": page.url,
                "title": page.title,
                "content": page.content,
                "depth": page.depth,
                "timestamp": page.timestamp,
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_pages(self, input_dir: str) -> List[CrawledPage]:
        pages = []
        for filepath in sorted(Path(input_dir).glob("*.json")):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            pages.append(CrawledPage(**data))
        return pages


def crawl_website(
    urls: List[str],
    max_depth: int = 2,
    max_pages: int = 50,
    timeout: int = 10,
    output_dir: str = "./data/scraped",
    progress_callback=None,
    failures: Optional[List[str]] = None,
) -> List[CrawledPage]:
    crawler = WebCrawler(
        base_urls=urls,
        max_depth=max_depth,
        max_pages=max_pages,
        timeout=timeout,
    )
    pages = crawler.crawl(progress_callback=progress_callback)
    crawler.save_pages(output_dir)
    if failures is not None:
        failures.extend(crawler.failures)
    return pages
