"""
Base Agent - Abstract base class for all AI agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass

@dataclass
class AgentMemory:
    """Memory structure for agents"""
    short_term: List[Dict[str, Any]]
    long_term: Dict[str, Any]
    working_memory: Dict[str, Any]
    
class BaseAgent(ABC):
    """
    Abstract base class for all AI agents
    Provides common functionality and enforces interface
    """
    
    def __init__(
        self,
        agent_id: str,
        constitution_system,
        web_learner,
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.constitution = constitution_system
        self.web_learner = web_learner
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{agent_id}")
        
        # Initialize memory
        self.memory = AgentMemory(
            short_term=[],
            long_term={},
            working_memory={}
        )
        
        # Performance tracking
        self.metrics = {
            "tasks_executed": 0,
            "tasks_succeeded": 0,
            "tasks_failed": 0,
            "learning_sessions": 0,
            "total_execution_time": 0.0
        }
        
        self.logger.info(f"Agent {agent_id} initialized")
    
    @abstractmethod
    async def execute(self, task) -> Dict[str, Any]:
        """
        Execute a task - must be implemented by subclasses
        
        Args:
            task: Task object to execute
            
        Returns:
            Dict containing task results
        """
        pass
    
    async def learn_about_topic(self, topic: str) -> Dict[str, Any]:
        """
        Learn about a topic using the web learner
        
        Args:
            topic: Topic to learn about
            
        Returns:
            Learned knowledge
        """
        self.logger.info(f"Agent {self.agent_id} learning about: {topic}")
        
        try:
            # Check if already in memory
            if topic in self.memory.long_term:
                self.logger.info(f"Topic '{topic}' found in memory")
                return self.memory.long_term[topic]
            
            # Learn from web
            knowledge = await self.web_learner.search_and_learn(topic)
            
            # Store in long-term memory
            self.memory.long_term[topic] = knowledge
            self.metrics["learning_sessions"] += 1
            
            self.logger.info(f"Successfully learned about '{topic}'")
            return knowledge
            
        except Exception as e:
            self.logger.error(f"Learning failed for '{topic}': {e}")
            raise
    
    def add_to_memory(self, memory_type: str, key: str, value: Any):
        """
        Add information to agent memory
        
        Args:
            memory_type: "short_term", "long_term", or "working"
            key: Memory key
            value: Memory value
        """
        if memory_type == "short_term":
            self.memory.short_term.append({
                "key": key,
                "value": value,
                "timestamp": datetime.now().isoformat()
            })
            # Keep only last 100 short-term memories
            if len(self.memory.short_term) > 100:
                self.memory.short_term = self.memory.short_term[-100:]
                
        elif memory_type == "long_term":
            self.memory.long_term[key] = value
            
        elif memory_type == "working":
            self.memory.working_memory[key] = value
    
    def get_from_memory(self, memory_type: str, key: Optional[str] = None) -> Any:
        """
        Retrieve information from agent memory
        
        Args:
            memory_type: "short_term", "long_term", or "working"
            key: Memory key (optional for short_term)
            
        Returns:
            Memory value or None
        """
        if memory_type == "short_term":
            if key:
                return [m for m in self.memory.short_term if m["key"] == key]
            return self.memory.short_term
            
        elif memory_type == "long_term":
            return self.memory.long_term.get(key) if key else self.memory.long_term
            
        elif memory_type == "working":
            return self.memory.working_memory.get(key) if key else self.memory.working_memory
        
        return None
    
    def clear_working_memory(self):
        """Clear working memory"""
        self.memory.working_memory = {}
    
    async def validate_with_constitution(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an action against constitutional principles
        
        Args:
            action: Action to validate
            context: Context for validation
            
        Returns:
            Validation result
        """
        return self.constitution.evaluate_action(action, context)
    
    def update_metrics(self, success: bool, execution_time: float):
        """Update agent performance metrics"""
        self.metrics["tasks_executed"] += 1
        
        if success:
            self.metrics["tasks_succeeded"] += 1
        else:
            self.metrics["tasks_failed"] += 1
        
        self.metrics["total_execution_time"] += execution_time
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        total_tasks = self.metrics["tasks_executed"]
        
        return {
            "agent_id": self.agent_id,
            "tasks_executed": total_tasks,
            "tasks_succeeded": self.metrics["tasks_succeeded"],
            "tasks_failed": self.metrics["tasks_failed"],
            "success_rate": (self.metrics["tasks_succeeded"] / total_tasks) if total_tasks > 0 else 0,
            "average_execution_time": (self.metrics["total_execution_time"] / total_tasks) if total_tasks > 0 else 0,
            "learning_sessions": self.metrics["learning_sessions"]
        }
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities - override in subclasses"""
        return ["base"]
    
    async def think(self, problem: str) -> str:
        """
        Internal reasoning process
        
        Args:
            problem: Problem to think about
            
        Returns:
            Thought process result
        """
        # Store in working memory
        self.add_to_memory("working", "current_problem", problem)
        
        # Check if we need to learn
        unknown_concepts = self._identify_unknown_concepts(problem)
        
        if unknown_concepts:
            self.logger.info(f"Identified unknown concepts: {unknown_concepts}")
            for concept in unknown_concepts:
                await self.learn_about_topic(concept)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(problem)
        
        return reasoning
    
    def _identify_unknown_concepts(self, text: str) -> List[str]:
        """Identify concepts that might need learning"""
        # Simple heuristic - look for capitalized terms or technical jargon
        # In production, use NLP/ML models
        
        words = text.split()
        unknown = []
        
        for word in words:
            # Check if it's a potential concept (capitalized, not common word)
            if (word[0].isupper() and 
                word.lower() not in ['i', 'the', 'a', 'an'] and
                word not in self.memory.long_term):
                unknown.append(word)
        
        return list(set(unknown))[:5]  # Limit to 5 concepts
    
    def _generate_reasoning(self, problem: str) -> str:
        """Generate reasoning about a problem"""
        # Access relevant knowledge from memory
        relevant_knowledge = []
        
        for topic, knowledge in self.memory.long_term.items():
            if topic.lower() in problem.lower():
                relevant_knowledge.append(knowledge)
        
        # Combine into reasoning
        if relevant_knowledge:
            reasoning = f"Based on my knowledge of {len(relevant_knowledge)} relevant topics, "
            reasoning += f"I understand that this problem involves: {problem}. "
            reasoning += "I will apply the learned concepts to solve it."
        else:
            reasoning = f"Analyzing problem: {problem}. "
            reasoning += "I will use my base capabilities to address this."
        
        return reasoning
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.agent_id}>"
