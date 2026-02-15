"""
Web Learner - Learns from internet sources on topics the AI doesn't know
Direct internet connection with no content filtering
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import hashlib
import logging
from urllib.parse import urljoin, urlparse

class WebLearner:
    """
    Advanced web learning system that can fetch, process, and learn from any web content
    NO FILTERING - Direct access to all web content for comprehensive learning
    """
    
    def __init__(self, constitution_system=None, cache_dir: str = "./web_cache"):
        self.logger = logging.getLogger(__name__)
        self.constitution = constitution_system
        self.cache_dir = cache_dir
        self.learned_content = {}
        self.knowledge_base = {}
        self.session = None
        
        # User agents to avoid blocking
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        self.logger.info("WebLearner initialized - Direct internet access enabled")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': self.user_agents[0]},
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def search_and_learn(
        self,
        topic: str,
        num_sources: int = 10,
        depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Search for a topic and learn from multiple sources
        
        Args:
            topic: Topic to learn about
            num_sources: Number of sources to fetch
            depth: Learning depth - "quick", "moderate", "comprehensive", "deep"
            
        Returns:
            Learned knowledge structured as a dictionary
        """
        self.logger.info(f"Learning about topic: {topic}")
        
        # Generate search queries
        search_queries = self._generate_search_queries(topic, depth)
        
        # Fetch sources
        sources = []
        for query in search_queries[:num_sources]:
            try:
                fetched = await self.fetch_web_content(query)
                sources.extend(fetched)
            except Exception as e:
                self.logger.warning(f"Failed to fetch for query '{query}': {e}")
        
        # Process and extract knowledge
        knowledge = await self._process_sources(sources, topic)
        
        # Store in knowledge base
        self.knowledge_base[topic] = {
            "content": knowledge,
            "sources": [s["url"] for s in sources],
            "learned_at": datetime.now().isoformat(),
            "confidence": knowledge.get("confidence", 0.7)
        }
        
        self.logger.info(f"Learning complete for '{topic}' from {len(sources)} sources")
        
        return self.knowledge_base[topic]
    
    def _generate_search_queries(self, topic: str, depth: str) -> List[str]:
        """Generate search queries based on topic and desired depth"""
        base_queries = [
            topic,
            f"{topic} tutorial",
            f"{topic} guide",
            f"{topic} explanation",
            f"what is {topic}",
            f"how does {topic} work",
            f"{topic} examples",
            f"{topic} best practices"
        ]
        
        depth_queries = {
            "quick": base_queries[:3],
            "moderate": base_queries[:5],
            "comprehensive": base_queries + [
                f"{topic} advanced",
                f"{topic} research",
                f"{topic} latest developments"
            ],
            "deep": base_queries + [
                f"{topic} advanced",
                f"{topic} research papers",
                f"{topic} academic",
                f"{topic} latest developments",
                f"{topic} implementation",
                f"{topic} case studies",
                f"{topic} expert analysis"
            ]
        }
        
        return depth_queries.get(depth, base_queries)
    
    async def fetch_web_content(
        self,
        url_or_query: str,
        follow_links: bool = False,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Fetch content from web - DIRECT ACCESS, NO FILTERING
        
        Args:
            url_or_query: URL to fetch or search query
            follow_links: Whether to follow links in the page
            max_depth: Maximum depth for link following
            
        Returns:
            List of content dictionaries
        """
        session = await self._get_session()
        
        # If it's a query, simulate search (in production, use real search API)
        if not url_or_query.startswith('http'):
            # For demo purposes, we'll use DuckDuckGo HTML search
            search_url = f"https://duckduckgo.com/html/?q={url_or_query}"
            urls = await self._extract_search_results(search_url)
        else:
            urls = [url_or_query]
        
        contents = []
        for url in urls[:5]:  # Limit to 5 URLs per query
            try:
                content = await self._fetch_single_page(url)
                if content:
                    contents.append(content)
                    
                    # Follow links if requested
                    if follow_links and max_depth > 0:
                        links = content.get("links", [])[:3]
                        for link in links:
                            try:
                                sub_content = await self._fetch_single_page(link)
                                if sub_content:
                                    contents.append(sub_content)
                            except:
                                continue
                                
            except Exception as e:
                self.logger.warning(f"Failed to fetch {url}: {e}")
                continue
        
        return contents
    
    async def _fetch_single_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a single web page"""
        session = await self._get_session()
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Extract main content
                content = {
                    "url": url,
                    "title": soup.title.string if soup.title else "",
                    "text": soup.get_text(separator=' ', strip=True),
                    "links": self._extract_links(soup, url),
                    "metadata": self._extract_metadata(soup),
                    "fetched_at": datetime.now().isoformat()
                }
                
                # Cache content
                self._cache_content(url, content)
                
                return content
                
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def _extract_search_results(self, search_url: str) -> List[str]:
        """Extract URLs from search results"""
        session = await self._get_session()
        
        try:
            async with session.get(search_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract result links (this varies by search engine)
                links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http') and 'duckduckgo' not in href:
                        links.append(href)
                
                return links[:10]  # Return top 10 results
                
        except Exception as e:
            self.logger.error(f"Error extracting search results: {e}")
            return []
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from a page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            if full_url.startswith('http'):
                links.append(full_url)
        return links[:20]  # Limit to 20 links
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from page"""
        metadata = {}
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                metadata[name] = content
        
        # Extract headings
        metadata['headings'] = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
        
        return metadata
    
    async def _process_sources(
        self,
        sources: List[Dict[str, Any]],
        topic: str
    ) -> Dict[str, Any]:
        """Process multiple sources and extract structured knowledge"""
        
        if not sources:
            return {
                "summary": f"No sources found for {topic}",
                "confidence": 0.0,
                "details": {}
            }
        
        # Combine all text
        all_text = " ".join([s.get("text", "") for s in sources])
        
        # Extract key information
        knowledge = {
            "topic": topic,
            "summary": self._generate_summary(all_text, topic),
            "key_points": self._extract_key_points(all_text, topic),
            "definitions": self._extract_definitions(all_text, topic),
            "examples": self._extract_examples(all_text, topic),
            "related_topics": self._extract_related_topics(all_text, topic),
            "technical_details": self._extract_technical_details(all_text),
            "confidence": self._calculate_confidence(sources),
            "source_count": len(sources)
        }
        
        return knowledge
    
    def _generate_summary(self, text: str, topic: str) -> str:
        """Generate a summary of the learned content"""
        # Find sentences containing the topic
        sentences = re.split(r'[.!?]+', text)
        relevant = [s.strip() for s in sentences if topic.lower() in s.lower()][:5]
        
        return " ".join(relevant) if relevant else f"Information about {topic} gathered from web sources."
    
    def _extract_key_points(self, text: str, topic: str) -> List[str]:
        """Extract key points about the topic"""
        # Look for bullet points, numbered lists, or sentences with key phrases
        key_phrases = ['important', 'key', 'main', 'essential', 'critical', 'fundamental']
        
        sentences = re.split(r'[.!?]+', text)
        key_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(phrase in sentence.lower() for phrase in key_phrases):
                if topic.lower() in sentence.lower():
                    key_points.append(sentence)
        
        return key_points[:10]
    
    def _extract_definitions(self, text: str, topic: str) -> List[str]:
        """Extract definitions of the topic"""
        # Look for definition patterns
        patterns = [
            rf"{topic} is (.{{20,200}}?)[.!?]",
            rf"{topic} refers to (.{{20,200}}?)[.!?]",
            rf"{topic} means (.{{20,200}}?)[.!?]",
            rf"{topic}[:\-] (.{{20,200}}?)[.!?]"
        ]
        
        definitions = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            definitions.extend(matches)
        
        return list(set(definitions))[:5]
    
    def _extract_examples(self, text: str, topic: str) -> List[str]:
        """Extract examples related to the topic"""
        # Look for example patterns
        example_phrases = ['for example', 'such as', 'like', 'instance', 'e.g.']
        
        sentences = re.split(r'[.!?]+', text)
        examples = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(phrase in sentence.lower() for phrase in example_phrases):
                if topic.lower() in sentence.lower():
                    examples.append(sentence)
        
        return examples[:5]
    
    def _extract_related_topics(self, text: str, topic: str) -> List[str]:
        """Extract related topics"""
        # Extract capitalized phrases that might be related topics
        related = set()
        
        # Simple extraction of capitalized phrases
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and word.lower() != topic.lower():
                # Check if it's part of a phrase
                phrase = word
                j = i + 1
                while j < len(words) and j < i + 4:
                    if words[j][0].isupper():
                        phrase += " " + words[j]
                        j += 1
                    else:
                        break
                
                if len(phrase.split()) >= 2:
                    related.add(phrase)
        
        return list(related)[:10]
    
    def _extract_technical_details(self, text: str) -> Dict[str, Any]:
        """Extract technical details like code, formulas, specifications"""
        details = {
            "code_snippets": [],
            "numbers_and_stats": [],
            "technical_terms": []
        }
        
        # Extract code-like patterns
        code_patterns = [
            r'`([^`]+)`',
            r'```([^`]+)```'
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, text)
            details["code_snippets"].extend(matches)
        
        # Extract numbers and statistics
        number_patterns = [
            r'\d+%',
            r'\d+\.\d+',
            r'\$\d+',
            r'\d+[KMB]'
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, text)
            details["numbers_and_stats"].extend(matches)
        
        return details
    
    def _calculate_confidence(self, sources: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on number and quality of sources"""
        if not sources:
            return 0.0
        
        # Base confidence on number of sources
        base_confidence = min(len(sources) / 10, 1.0)
        
        # Adjust based on source quality indicators
        quality_indicators = 0
        for source in sources:
            metadata = source.get("metadata", {})
            # Check for quality indicators
            if any(domain in source.get("url", "") for domain in ['.edu', '.gov', '.org']):
                quality_indicators += 0.1
            if len(source.get("text", "")) > 1000:
                quality_indicators += 0.05
        
        confidence = min(base_confidence + quality_indicators, 1.0)
        return round(confidence, 2)
    
    def _cache_content(self, url: str, content: Dict[str, Any]):
        """Cache fetched content"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        self.learned_content[url_hash] = content
    
    def get_knowledge(self, topic: str) -> Optional[Dict[str, Any]]:
        """Retrieve learned knowledge about a topic"""
        return self.knowledge_base.get(topic)
    
    def export_knowledge_base(self, filepath: str):
        """Export entire knowledge base to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Knowledge base exported to {filepath}")
    
    def import_knowledge_base(self, filepath: str):
        """Import knowledge base from file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.knowledge_base = json.load(f)
        
        self.logger.info(f"Knowledge base imported from {filepath}")
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
