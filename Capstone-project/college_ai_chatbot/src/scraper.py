import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import html2text


class ContentScraper:
    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.ignore_emphasis = False
        self.html_converter.body_width = 0
    
    def extract_main_content(self, html: str, url: str) -> Dict[str, str]:
        soup = BeautifulSoup(html, "lxml")
        
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe", "form", "button", "input", "select", "textarea", "svg", "path"]):
            tag.decompose()
        
        title = self._extract_title(soup)
        
        main_content = self._find_main_content(soup)
        
        if main_content:
            text = self._clean_text(main_content.get_text(separator="\n", strip=True))
        else:
            text = self._clean_text(soup.get_text(separator="\n", strip=True))
        
        markdown = self._to_markdown(main_content or soup)
        
        return {
            "title": title,
            "text": text,
            "markdown": markdown,
            "url": url,
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()
        
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()
        
        return ""
    
    def _find_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        selectors = [
            "main",
            "article",
            '[role="main"]',
            ".main-content",
            "#main-content",
            ".content",
            "#content",
            ".page-content",
            ".post-content",
            ".entry-content",
            ".college-content",
            ".university-content",
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element
        
        return soup.body
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\n[ \t]+\n", "\n\n", text)
        return text.strip()
    
    def _to_markdown(self, soup: BeautifulSoup) -> str:
        try:
            return self.html_converter.handle(str(soup))
        except Exception:
            return ""
    
    def extract_structured_data(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "lxml")
        structured = []
        
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json
                data = json.loads(script.string)
                structured.append(data)
            except Exception:
                pass
        
        return structured


def scrape_page(html: str, url: str) -> Dict[str, str]:
    scraper = ContentScraper()
    return scraper.extract_main_content(html, url)