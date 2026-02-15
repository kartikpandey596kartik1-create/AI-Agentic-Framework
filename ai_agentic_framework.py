"""
AI Agentic Framework - Main Framework
Manages AI agents with constitutional logic and internet learning capabilities
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Import core components
from constitution import ConstitutionalAI
from agent_manager import AgentManager, AgentConfig, Task, AgentCapability, AgentStatus
from web_learner import WebLearner
from research_agent import ResearchAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AIAgenticFramework:
    """
    Main AI Agentic Framework
    
    Features:
    - Multi-agent management and orchestration
    - Constitutional AI for ethical decision-making
    - Direct internet learning without filters
    - Task distribution and coordination
    - Memory and knowledge management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Initialize core systems
        self.logger.info("Initializing AI Agentic Framework...")
        
        # Constitutional AI system
        self.constitution = ConstitutionalAI()
        self.logger.info("Constitutional AI system initialized")
        
        # Web learning system
        self.web_learner = WebLearner(
            constitution_system=self.constitution,
            cache_dir=self.config.get("cache_dir", "./web_cache")
        )
        self.logger.info("Web Learning system initialized")
        
        # Agent manager
        self.agent_manager = AgentManager(
            constitution_system=self.constitution,
            config=self.config.get("agent_config", {})
        )
        self.logger.info("Agent Manager initialized")
        
        # Framework state
        self.framework_id = self._generate_framework_id()
        self.start_time = datetime.now()
        self.running = False
        
        self.logger.info(f"Framework {self.framework_id} ready")
    
    def _generate_framework_id(self) -> str:
        """Generate unique framework ID"""
        import uuid
        return f"framework_{uuid.uuid4().hex[:8]}"
    
    async def initialize_agents(self, agent_configs: List[Dict[str, Any]]):
        """
        Initialize agents based on configurations
        
        Args:
            agent_configs: List of agent configuration dictionaries
        """
        self.logger.info(f"Initializing {len(agent_configs)} agents...")
        
        for config_dict in agent_configs:
            try:
                agent_type = config_dict.get("type", "research")
                agent_id = config_dict.get("id", f"agent_{len(self.agent_manager.agents)}")
                
                # Create agent based on type
                if agent_type == "research":
                    agent_instance = ResearchAgent(
                        agent_id=agent_id,
                        constitution_system=self.constitution,
                        web_learner=self.web_learner,
                        config=config_dict
                    )
                else:
                    # Default to research agent
                    agent_instance = ResearchAgent(
                        agent_id=agent_id,
                        constitution_system=self.constitution,
                        web_learner=self.web_learner,
                        config=config_dict
                    )
                
                # Create agent config
                capabilities = config_dict.get("capabilities", [AgentCapability.RESEARCH])
                agent_config = AgentConfig(
                    name=agent_id,
                    capabilities=capabilities,
                    max_concurrent_tasks=config_dict.get("max_concurrent_tasks", 5),
                    learning_enabled=config_dict.get("learning_enabled", True),
                    constitution_level=config_dict.get("constitution_level", "high")
                )
                
                # Register with agent manager
                self.agent_manager.register_agent(agent_id, agent_instance, agent_config)
                self.logger.info(f"Agent {agent_id} initialized and registered")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize agent: {e}")
    
    async def submit_task(
        self,
        description: str,
        task_type: str = "research",
        priority: int = 5,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit a task to the framework
        
        Args:
            description: Task description
            task_type: Type of task
            priority: Task priority (1-10, 10 highest)
            context: Additional context
            
        Returns:
            Task ID
        """
        import uuid
        
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # Determine required capabilities
        required_caps = self._determine_required_capabilities(task_type, description)
        
        # Create task
        task = Task(
            id=task_id,
            type=task_type,
            description=description,
            priority=priority,
            requirements=required_caps,
            context=context or {}
        )
        
        # Submit to agent manager
        try:
            task_id = self.agent_manager.submit_task(task)
            self.logger.info(f"Task {task_id} submitted: {description[:50]}...")
            return task_id
        except Exception as e:
            self.logger.error(f"Failed to submit task: {e}")
            raise
    
    def _determine_required_capabilities(
        self,
        task_type: str,
        description: str
    ) -> List[AgentCapability]:
        """Determine what capabilities are needed for a task"""
        
        capabilities = []
        
        # Map task types to capabilities
        type_mapping = {
            "research": [AgentCapability.RESEARCH, AgentCapability.ANALYSIS],
            "code": [AgentCapability.CODE],
            "analysis": [AgentCapability.ANALYSIS],
            "communication": [AgentCapability.COMMUNICATION]
        }
        
        if task_type in type_mapping:
            capabilities.extend(type_mapping[task_type])
        
        # Check description for additional hints
        desc_lower = description.lower()
        if any(word in desc_lower for word in ["learn", "research", "find", "search"]):
            if AgentCapability.RESEARCH not in capabilities:
                capabilities.append(AgentCapability.RESEARCH)
        
        if any(word in desc_lower for word in ["plan", "strategy", "organize"]):
            capabilities.append(AgentCapability.PLANNING)
        
        return capabilities if capabilities else [AgentCapability.RESEARCH]
    
    async def run(self, duration: Optional[float] = None):
        """
        Run the framework
        
        Args:
            duration: Optional duration in seconds (None for infinite)
        """
        self.running = True
        self.logger.info("Framework starting...")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            while self.running:
                # Process task queue
                if self.agent_manager.task_queue:
                    await self.agent_manager.process_task_queue()
                
                # Check duration
                if duration:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed >= duration:
                        self.logger.info("Duration limit reached")
                        break
                
                # Small delay to prevent tight loop
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("Framework interrupted by user")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the framework gracefully"""
        self.logger.info("Shutting down framework...")
        self.running = False
        
        # Close web learner session
        await self.web_learner.close()
        
        # Export final state
        self.export_state("framework_final_state.json")
        
        self.logger.info("Framework shutdown complete")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current framework status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "framework_id": self.framework_id,
            "running": self.running,
            "uptime_seconds": uptime,
            "agent_stats": self.agent_manager.get_system_stats(),
            "constitution_summary": self.constitution.get_ethics_summary(),
            "knowledge_base_size": len(self.web_learner.knowledge_base)
        }
    
    def export_state(self, filepath: str):
        """Export framework state to file"""
        state = {
            "framework_id": self.framework_id,
            "timestamp": datetime.now().isoformat(),
            "status": self.get_status(),
            "agents": self.agent_manager.get_agent_status(),
            "completed_tasks": len(self.agent_manager.completed_tasks)
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        self.logger.info(f"Framework state exported to {filepath}")
    
    async def learn_topic(self, topic: str, depth: str = "comprehensive") -> Dict[str, Any]:
        """
        Learn about a topic directly
        
        Args:
            topic: Topic to learn
            depth: Learning depth
            
        Returns:
            Learned knowledge
        """
        return await self.web_learner.search_and_learn(topic, depth=depth)
    
    def get_knowledge(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get learned knowledge about a topic"""
        return self.web_learner.get_knowledge(topic)
    
    def export_knowledge_base(self, filepath: str):
        """Export entire knowledge base"""
        self.web_learner.export_knowledge_base(filepath)
    
    def get_agent_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get agent status"""
        return self.agent_manager.get_agent_status(agent_id)


# Example usage and test functions
async def example_usage():
    """Example of how to use the framework"""
    
    print("=" * 60)
    print("AI AGENTIC FRAMEWORK - DEMONSTRATION")
    print("=" * 60)
    
    # Initialize framework
    framework = AIAgenticFramework(config={
        "cache_dir": "./web_cache"
    })
    
    # Initialize agents
    agent_configs = [
        {
            "id": "research_agent_1",
            "type": "research",
            "capabilities": [AgentCapability.RESEARCH, AgentCapability.ANALYSIS],
            "max_concurrent_tasks": 5,
            "learning_enabled": True
        },
        {
            "id": "research_agent_2",
            "type": "research",
            "capabilities": [AgentCapability.RESEARCH, AgentCapability.LEARNING],
            "max_concurrent_tasks": 3,
            "learning_enabled": True
        }
    ]
    
    await framework.initialize_agents(agent_configs)
    
    print("\n✓ Framework initialized with 2 research agents")
    
    # Submit some tasks
    print("\n" + "=" * 60)
    print("SUBMITTING TASKS")
    print("=" * 60)
    
    tasks = [
        {
            "description": "Research the latest developments in quantum computing",
            "type": "research",
            "priority": 8
        },
        {
            "description": "Compare transformer architectures vs RNN for NLP",
            "type": "research",
            "priority": 7
        },
        {
            "description": "Deep dive into constitutional AI principles",
            "type": "research",
            "priority": 9
        }
    ]
    
    task_ids = []
    for task in tasks:
        task_id = await framework.submit_task(**task)
        task_ids.append(task_id)
        print(f"✓ Submitted: {task['description'][:50]}... (ID: {task_id})")
    
    # Run framework for a short time
    print("\n" + "=" * 60)
    print("PROCESSING TASKS")
    print("=" * 60)
    
    # Process tasks
    await framework.agent_manager.process_task_queue()
    
    # Get status
    print("\n" + "=" * 60)
    print("FRAMEWORK STATUS")
    print("=" * 60)
    
    status = framework.get_status()
    print(f"Framework ID: {status['framework_id']}")
    print(f"Uptime: {status['uptime_seconds']:.2f} seconds")
    print(f"Total Agents: {status['agent_stats']['total_agents']}")
    print(f"Completed Tasks: {status['agent_stats']['completed_tasks']}")
    print(f"Knowledge Base Size: {status['knowledge_base_size']} topics")
    
    # Export state
    framework.export_state("framework_state.json")
    framework.export_knowledge_base("knowledge_base.json")
    
    print("\n✓ State and knowledge base exported")
    
    # Shutdown
    await framework.shutdown()
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
