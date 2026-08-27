import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class ContentCleaner:
    def __init__(self):
        self.noise_patterns = [
            r"cookie\s+policy",
            r"privacy\s+policy",
            r"terms\s+of\s+service",
            r"terms\s+and\s+conditions",
            r"all\s+rights\s+reserved",
            r"copyright\s+\d{4}",
            r"follow\s+us",
            r"subscribe\s+to",
            r"newsletter",
            r"social\s+media",
            r"share\s+this",
            r"print\s+this\s+page",
            r"back\s+to\s+top",
            r"skip\s+to\s+main\s+content",
            r"accessibility",
            r"site\s+map",
            r"contact\s+us\s*$",
            r"^\s*\d+\s*$",
            r"^\s*[|•]\s*$",
        ]
        
        self.compiled_noise = [re.compile(p, re.IGNORECASE) for p in self.noise_patterns]
    
    def clean(self, text: str) -> str:
        text = self._remove_excess_whitespace(text)
        text = self._remove_noise_lines(text)
        text = self._normalize_punctuation(text)
        text = self._remove_duplicate_lines(text)
        return text.strip()
    
    def _remove_excess_whitespace(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\n[ \t]+\n", "\n\n", text)
        return text
    
    def _remove_noise_lines(self, text: str) -> str:
        lines = text.split("\n")
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                cleaned_lines.append("")
                continue
            
            is_noise = False
            for pattern in self.compiled_noise:
                if pattern.search(line_stripped):
                    is_noise = True
                    break
            
            if not is_noise:
                cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)
    
    def _normalize_punctuation(self, text: str) -> str:
        text = re.sub(r"\.{3,}", "...", text)
        text = re.sub(r"[-]{3,}", "---", text)
        text = re.sub(r"[_]{3,}", "___", text)
        text = re.sub(r"[*]{3,}", "***", text)
        return text
    
    def _remove_duplicate_lines(self, text: str) -> str:
        lines = text.split("\n")
        seen = set()
        result = []
        
        for line in lines:
            stripped = line.strip()
            if stripped and stripped in seen:
                continue
            if stripped:
                seen.add(stripped)
            result.append(line)
        
        return "\n".join(result)
    
    def clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")
        
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe", "form", "button", "input", "select", "textarea", "svg", "path", "meta", "link"]):
            tag.decompose()
        
        for tag in soup.find_all(class_=True):
            classes = tag.get("class", [])
            class_str = " ".join(classes).lower()
            if any(noise in class_str for noise in ["nav", "menu", "footer", "header", "sidebar", "widget", "advert", "banner", "cookie", "popup", "modal", "overlay"]):
                tag.decompose()
        
        return str(soup)
    
    def extract_key_info(self, text: str) -> Dict[str, List[str]]:
        info = {
            "emails": [],
            "phones": [],
            "urls": [],
            "dates": [],
        }
        
        email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        phone_pattern = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
        url_pattern = re.compile(r"https?://[^\s<>\"]+")
        date_pattern = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b")
        
        info["emails"] = list(set(email_pattern.findall(text)))
        info["phones"] = list(set(phone_pattern.findall(text)))
        info["urls"] = list(set(url_pattern.findall(text)))
        info["dates"] = list(set(date_pattern.findall(text)))
        
        return info


def clean_content(text: str) -> str:
    cleaner = ContentCleaner()
    return cleaner.clean(text)


def clean_html(html: str) -> str:
    cleaner = ContentCleaner()
    return cleaner.clean_html(html)