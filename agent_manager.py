"""
Agent Manager - Orchestrates and manages multiple AI agents
"""

import asyncio
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor
import json

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    LEARNING = "learning"
    PAUSED = "paused"

class AgentCapability(Enum):
    RESEARCH = "research"
    CODE = "code"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    LEARNING = "learning"
    PLANNING = "planning"

@dataclass
class AgentConfig:
    """Configuration for an AI agent"""
    name: str
    capabilities: List[AgentCapability]
    max_concurrent_tasks: int = 5
    learning_enabled: bool = True
    constitution_level: str = "high"
    priority: int = 1

@dataclass
class Task:
    """Task to be executed by an agent"""
    id: str
    type: str
    description: str
    priority: int
    requirements: List[AgentCapability]
    context: Dict[str, Any]
    dependencies: List[str] = None
    
class AgentManager:
    """
    Manages multiple AI agents, task distribution, and coordination
    """
    
    def __init__(self, constitution_system, config: Optional[Dict] = None):
        self.logger = logging.getLogger(__name__)
        self.constitution = constitution_system
        self.agents: Dict[str, Any] = {}
        self.task_queue: List[Task] = []
        self.completed_tasks: Dict[str, Any] = {}
        self.agent_status: Dict[str, AgentStatus] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.config = config or {}
        
        self.logger.info("Agent Manager initialized")
    
    def register_agent(self, agent_id: str, agent_instance: Any, config: AgentConfig):
        """Register a new agent with the manager"""
        
        # Validate agent against constitution
        validation = self.constitution.evaluate_action(
            f"Register agent {agent_id} with capabilities {config.capabilities}",
            {"agent_config": config.__dict__}
        )
        
        if not validation["allowed"]:
            self.logger.error(f"Agent registration failed: {validation['violations']}")
            raise ValueError(f"Agent violates constitutional principles: {validation['violations']}")
        
        self.agents[agent_id] = {
            "instance": agent_instance,
            "config": config,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "learning_sessions": 0
        }
        
        self.agent_status[agent_id] = AgentStatus.IDLE
        self.logger.info(f"Agent {agent_id} registered with capabilities: {config.capabilities}")
        
        return agent_id
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.agent_status[agent_id]
            self.logger.info(f"Agent {agent_id} unregistered")
    
    def submit_task(self, task: Task) -> str:
        """Submit a task to the task queue"""
        
        # Validate task against constitution
        validation = self.constitution.evaluate_action(
            f"Execute task: {task.description}",
            {"task_type": task.type, "context": task.context}
        )
        
        if not validation["allowed"]:
            self.logger.error(f"Task rejected: {validation['violations']}")
            raise ValueError(f"Task violates constitutional principles: {validation['violations']}")
        
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)
        
        self.logger.info(f"Task {task.id} submitted: {task.description}")
        return task.id
    
    def _find_suitable_agent(self, task: Task) -> Optional[str]:
        """Find the most suitable agent for a task"""
        suitable_agents = []
        
        for agent_id, agent_data in self.agents.items():
            # Check if agent is available
            if self.agent_status[agent_id] != AgentStatus.IDLE:
                continue
            
            # Check if agent has required capabilities
            agent_capabilities = set(agent_data["config"].capabilities)
            required_capabilities = set(task.requirements)
            
            if required_capabilities.issubset(agent_capabilities):
                suitable_agents.append({
                    "id": agent_id,
                    "priority": agent_data["config"].priority,
                    "success_rate": self._calculate_success_rate(agent_id)
                })
        
        if not suitable_agents:
            return None
        
        # Select best agent based on priority and success rate
        suitable_agents.sort(
            key=lambda a: (a["priority"], a["success_rate"]),
            reverse=True
        )
        
        return suitable_agents[0]["id"]
    
    def _calculate_success_rate(self, agent_id: str) -> float:
        """Calculate agent's success rate"""
        agent_data = self.agents[agent_id]
        completed = agent_data["tasks_completed"]
        failed = agent_data["tasks_failed"]
        
        if completed + failed == 0:
            return 1.0
        
        return completed / (completed + failed)
    
    async def execute_task(self, task: Task, agent_id: str) -> Dict[str, Any]:
        """Execute a task with the specified agent"""
        
        try:
            self.agent_status[agent_id] = AgentStatus.BUSY
            agent = self.agents[agent_id]["instance"]
            
            self.logger.info(f"Agent {agent_id} executing task {task.id}")
            
            # Execute the task
            result = await agent.execute(task)
            
            # Validate result against constitution
            validation = self.constitution.evaluate_action(
                f"Task result: {result.get('summary', 'No summary')}",
                {"result": result, "task": task.__dict__}
            )
            
            if not validation["allowed"]:
                self.logger.warning(f"Task result flagged: {validation['violations']}")
                result["constitutional_warnings"] = validation["violations"]
            
            self.agents[agent_id]["tasks_completed"] += 1
            self.agent_status[agent_id] = AgentStatus.IDLE
            
            self.completed_tasks[task.id] = {
                "task": task,
                "result": result,
                "agent": agent_id,
                "status": "success"
            }
            
            self.logger.info(f"Task {task.id} completed successfully by {agent_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Task {task.id} failed: {e}")
            self.agents[agent_id]["tasks_failed"] += 1
            self.agent_status[agent_id] = AgentStatus.ERROR
            
            self.completed_tasks[task.id] = {
                "task": task,
                "error": str(e),
                "agent": agent_id,
                "status": "failed"
            }
            
            # Try to recover or reassign
            await self._handle_task_failure(task, agent_id, e)
            
            raise
    
    async def _handle_task_failure(self, task: Task, agent_id: str, error: Exception):
        """Handle task failure"""
        self.logger.info(f"Handling failure for task {task.id}")
        
        # Reset agent status after cooldown
        await asyncio.sleep(5)
        self.agent_status[agent_id] = AgentStatus.IDLE
        
        # Consider reassigning task
        if task.priority > 5:  # High priority tasks get reassigned
            self.task_queue.append(task)
            self.logger.info(f"Task {task.id} re-queued for retry")
    
    async def process_task_queue(self):
        """Process tasks in the queue"""
        while self.task_queue:
            task = self.task_queue[0]
            
            # Check dependencies
            if task.dependencies:
                all_completed = all(
                    dep_id in self.completed_tasks and 
                    self.completed_tasks[dep_id]["status"] == "success"
                    for dep_id in task.dependencies
                )
                
                if not all_completed:
                    # Move to back of queue
                    self.task_queue.append(self.task_queue.pop(0))
                    continue
            
            # Find suitable agent
            agent_id = self._find_suitable_agent(task)
            
            if agent_id:
                self.task_queue.pop(0)
                try:
                    await self.execute_task(task, agent_id)
                except Exception as e:
                    self.logger.error(f"Task execution error: {e}")
            else:
                self.logger.debug("No suitable agent available, waiting...")
                await asyncio.sleep(1)
    
    def get_agent_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of one or all agents"""
        if agent_id:
            if agent_id not in self.agents:
                return {"error": "Agent not found"}
            
            return {
                "agent_id": agent_id,
                "status": self.agent_status[agent_id].value,
                "stats": {
                    "tasks_completed": self.agents[agent_id]["tasks_completed"],
                    "tasks_failed": self.agents[agent_id]["tasks_failed"],
                    "success_rate": self._calculate_success_rate(agent_id)
                },
                "config": self.agents[agent_id]["config"].__dict__
            }
        else:
            return {
                agent_id: {
                    "status": self.agent_status[agent_id].value,
                    "stats": {
                        "tasks_completed": self.agents[agent_id]["tasks_completed"],
                        "tasks_failed": self.agents[agent_id]["tasks_failed"],
                        "success_rate": self._calculate_success_rate(agent_id)
                    }
                }
                for agent_id in self.agents.keys()
            }
    
    def pause_agent(self, agent_id: str):
        """Pause an agent"""
        if agent_id in self.agent_status:
            self.agent_status[agent_id] = AgentStatus.PAUSED
            self.logger.info(f"Agent {agent_id} paused")
    
    def resume_agent(self, agent_id: str):
        """Resume a paused agent"""
        if agent_id in self.agent_status:
            self.agent_status[agent_id] = AgentStatus.IDLE
            self.logger.info(f"Agent {agent_id} resumed")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        total_agents = len(self.agents)
        active_agents = sum(1 for status in self.agent_status.values() 
                          if status == AgentStatus.BUSY)
        
        total_completed = sum(a["tasks_completed"] for a in self.agents.values())
        total_failed = sum(a["tasks_failed"] for a in self.agents.values())
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "idle_agents": sum(1 for s in self.agent_status.values() if s == AgentStatus.IDLE),
            "queued_tasks": len(self.task_queue),
            "completed_tasks": total_completed,
            "failed_tasks": total_failed,
            "overall_success_rate": total_completed / (total_completed + total_failed) 
                                   if (total_completed + total_failed) > 0 else 0,
            "constitution_summary": self.constitution.get_ethics_summary()
        }
    
    def export_state(self, filepath: str):
        """Export system state to file"""
        state = {
            "agents": {
                agent_id: {
                    "config": data["config"].__dict__,
                    "stats": {
                        "tasks_completed": data["tasks_completed"],
                        "tasks_failed": data["tasks_failed"]
                    },
                    "status": self.agent_status[agent_id].value
                }
                for agent_id, data in self.agents.items()
            },
            "system_stats": self.get_system_stats()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        self.logger.info(f"System state exported to {filepath}")
