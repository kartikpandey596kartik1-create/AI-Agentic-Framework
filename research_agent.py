"""
Research Agent - Specialized in information gathering, research, and analysis
"""

import asyncio
from typing import Dict, Any, List
import re

class ResearchAgent:
    """
    Research agent that specializes in gathering and analyzing information
    Uses web learning extensively
    """
    
    def __init__(self, agent_id: str, constitution_system, web_learner, config=None):
        self.agent_id = agent_id
        self.constitution = constitution_system
        self.web_learner = web_learner
        self.config = config or {}
        self.memory = {"short_term": [], "long_term": {}, "working_memory": {}}
        self.metrics = {
            "tasks_executed": 0,
            "tasks_succeeded": 0,
            "research_depth_avg": 0.0
        }
    
    async def execute(self, task) -> Dict[str, Any]:
        """Execute a research task"""
        try:
            description = task.description
            context = task.context
            
            # Determine research strategy
            strategy = self._determine_research_strategy(description, context)
            
            # Execute research
            if strategy == "deep_dive":
                result = await self._deep_dive_research(description, context)
            elif strategy == "comparative":
                result = await self._comparative_research(description, context)
            elif strategy == "survey":
                result = await self._survey_research(description, context)
            else:
                result = await self._standard_research(description, context)
            
            self.metrics["tasks_executed"] += 1
            self.metrics["tasks_succeeded"] += 1
            
            return {
                "status": "success",
                "result": result,
                "agent": self.agent_id,
                "summary": result.get("summary", "Research completed")
            }
            
        except Exception as e:
            self.metrics["tasks_executed"] += 1
            raise Exception(f"Research task failed: {e}")
    
    def _determine_research_strategy(self, description: str, context: Dict) -> str:
        """Determine the best research strategy"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ["deep", "comprehensive", "detailed", "thorough"]):
            return "deep_dive"
        elif any(word in desc_lower for word in ["compare", "versus", "vs", "difference"]):
            return "comparative"
        elif any(word in desc_lower for word in ["survey", "overview", "landscape", "trends"]):
            return "survey"
        else:
            return "standard"
    
    async def _deep_dive_research(self, topic: str, context: Dict) -> Dict[str, Any]:
        """Perform deep dive research on a topic"""
        # Extract core topic
        core_topic = self._extract_core_topic(topic)
        
        # Learn about main topic with comprehensive depth
        main_knowledge = await self.web_learner.search_and_learn(
            core_topic,
            num_sources=15,
            depth="deep"
        )
        
        # Identify and research related topics
        related_topics = main_knowledge["content"].get("related_topics", [])[:5]
        related_knowledge = []
        
        for related in related_topics:
            try:
                knowledge = await self.web_learner.search_and_learn(
                    related,
                    num_sources=5,
                    depth="moderate"
                )
                related_knowledge.append(knowledge)
            except:
                continue
        
        # Synthesize findings
        synthesis = self._synthesize_deep_research(main_knowledge, related_knowledge)
        
        return {
            "research_type": "deep_dive",
            "main_topic": core_topic,
            "main_findings": main_knowledge,
            "related_research": related_knowledge,
            "synthesis": synthesis,
            "confidence": main_knowledge.get("confidence", 0.7)
        }
    
    async def _comparative_research(self, description: str, context: Dict) -> Dict[str, Any]:
        """Perform comparative research"""
        # Extract items to compare
        items = self._extract_comparison_items(description)
        
        if len(items) < 2:
            items = context.get("items_to_compare", [])
        
        # Research each item
        item_knowledge = {}
        for item in items:
            knowledge = await self.web_learner.search_and_learn(
                item,
                num_sources=10,
                depth="comprehensive"
            )
            item_knowledge[item] = knowledge
        
        # Generate comparison
        comparison = self._generate_comparison(item_knowledge)
        
        return {
            "research_type": "comparative",
            "items_compared": items,
            "individual_research": item_knowledge,
            "comparison": comparison,
            "recommendation": self._generate_recommendation(comparison)
        }
    
    async def _survey_research(self, topic: str, context: Dict) -> Dict[str, Any]:
        """Perform survey research to understand landscape"""
        core_topic = self._extract_core_topic(topic)
        
        # Get broad overview
        overview = await self.web_learner.search_and_learn(
            f"{core_topic} overview",
            num_sources=8,
            depth="moderate"
        )
        
        # Get recent trends
        trends = await self.web_learner.search_and_learn(
            f"{core_topic} latest trends",
            num_sources=8,
            depth="moderate"
        )
        
        # Get expert opinions
        expert_views = await self.web_learner.search_and_learn(
            f"{core_topic} expert analysis",
            num_sources=6,
            depth="moderate"
        )
        
        return {
            "research_type": "survey",
            "topic": core_topic,
            "overview": overview,
            "current_trends": trends,
            "expert_perspectives": expert_views,
            "key_insights": self._extract_key_insights([overview, trends, expert_views])
        }
    
    async def _standard_research(self, topic: str, context: Dict) -> Dict[str, Any]:
        """Perform standard research"""
        knowledge = await self.web_learner.search_and_learn(
            topic,
            num_sources=10,
            depth="comprehensive"
        )
        
        return {
            "research_type": "standard",
            "topic": topic,
            "findings": knowledge,
            "summary": knowledge["content"].get("summary", "")
        }
    
    def _extract_core_topic(self, text: str) -> str:
        """Extract the core topic from description"""
        # Remove common question words and extract main topic
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'is', 'are', 'the']
        words = text.lower().split()
        
        filtered = [w for w in words if w not in question_words and len(w) > 3]
        
        return " ".join(filtered[:5]) if filtered else text
    
    def _extract_comparison_items(self, text: str) -> List[str]:
        """Extract items to compare from text"""
        # Look for patterns like "X vs Y", "X and Y", "compare X with Y"
        patterns = [
            r'(\w+)\s+(?:vs|versus)\s+(\w+)',
            r'compare\s+(\w+)\s+(?:with|and|to)\s+(\w+)',
            r'(\w+)\s+and\s+(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return list(match.groups())
        
        return []
    
    def _synthesize_deep_research(
        self,
        main_knowledge: Dict,
        related_knowledge: List[Dict]
    ) -> str:
        """Synthesize deep research findings"""
        main_summary = main_knowledge["content"].get("summary", "")
        
        synthesis = f"Deep Research Synthesis:\n\n"
        synthesis += f"Main Topic Analysis: {main_summary}\n\n"
        
        if related_knowledge:
            synthesis += "Related Areas:\n"
            for rk in related_knowledge:
                topic = rk["content"].get("topic", "Unknown")
                summary = rk["content"].get("summary", "")[:200]
                synthesis += f"- {topic}: {summary}...\n"
        
        synthesis += f"\nOverall Confidence: {main_knowledge.get('confidence', 0.7)}"
        
        return synthesis
    
    def _generate_comparison(self, item_knowledge: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate comparison between items"""
        comparison = {
            "similarities": [],
            "differences": [],
            "strengths": {},
            "weaknesses": {}
        }
        
        # Extract key points from each item
        for item, knowledge in item_knowledge.items():
            content = knowledge.get("content", {})
            comparison["strengths"][item] = content.get("key_points", [])[:3]
        
        return comparison
    
    def _generate_recommendation(self, comparison: Dict) -> str:
        """Generate recommendation based on comparison"""
        return "Based on the research, consider the specific use case and requirements when choosing between the options."
    
    def _extract_key_insights(self, knowledge_list: List[Dict]) -> List[str]:
        """Extract key insights from multiple knowledge sources"""
        insights = []
        
        for knowledge in knowledge_list:
            content = knowledge.get("content", {})
            key_points = content.get("key_points", [])
            insights.extend(key_points[:3])
        
        return list(set(insights))[:10]
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return ["research", "analysis", "information_gathering", "comparison"]
