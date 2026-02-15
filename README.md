# AI Agentic Framework

A powerful, production-ready framework for managing multiple AI agents with constitutional AI principles and direct internet learning capabilities.

## 🌟 Features

### Core Capabilities
- **Multi-Agent Management**: Orchestrate multiple AI agents with different specializations
- **Constitutional AI**: Built-in ethical decision-making framework similar to Claude
- **Direct Internet Learning**: Agents can learn from the web without content filters
- **Task Orchestration**: Intelligent task distribution and dependency management
- **Memory Systems**: Short-term, long-term, and working memory for each agent
- **Real-time Learning**: Agents automatically learn about unknown topics

### Key Components

#### 1. Constitutional AI System (`constitution.py`)
- Ethical guidelines and decision-making framework
- Multiple violation levels (Critical, High, Medium, Low)
- Core values: Helpfulness, Harmlessness, Honesty
- Behavioral guidelines: Autonomy, Transparency, Privacy, Fairness
- Action validation and logging

#### 2. Agent Manager (`agent_manager.py`)
- Multi-agent orchestration
- Task queue management
- Agent status tracking (Idle, Busy, Error, Learning, Paused)
- Performance metrics and success rate tracking
- Task dependency resolution
- Automatic task reassignment on failure

#### 3. Web Learner (`web_learner.py`)
- **NO FILTERING** - Direct access to all web content
- Automatic web search and content fetching
- Knowledge extraction and structuring
- Caching system for efficiency
- Multiple learning depths: Quick, Moderate, Comprehensive, Deep
- Confidence scoring based on source quality

#### 4. Base Agent (`base_agent.py`)
- Abstract base class for all agents
- Memory management (short-term, long-term, working)
- Constitutional validation integration
- Performance metrics tracking
- Automatic learning for unknown concepts

#### 5. Research Agent (`research_agent.py`)
- Specialized in information gathering and analysis
- Multiple research strategies:
  - Deep Dive: Comprehensive research with related topics
  - Comparative: Side-by-side comparison of multiple items
  - Survey: Landscape overview with trends and expert opinions
  - Standard: General purpose research

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/AI-Agentic-Framework.git
cd AI-Agentic-Framework

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
import asyncio
from ai_agentic_framework import AIAgenticFramework
from agent_manager import AgentCapability

async def main():
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
            "learning_enabled": True
        }
    ]
    
    await framework.initialize_agents(agent_configs)
    
    # Submit a task
    task_id = await framework.submit_task(
        description="Research the latest developments in AI",
        task_type="research",
        priority=8
    )
    
    # Process tasks
    await framework.agent_manager.process_task_queue()
    
    # Get results
    result = framework.agent_manager.completed_tasks.get(task_id)
    print(result)
    
    # Shutdown
    await framework.shutdown()

asyncio.run(main())
```

### Direct Learning

```python
# Learn about a topic directly
knowledge = await framework.learn_topic(
    "quantum computing",
    depth="comprehensive"
)

print(knowledge["content"]["summary"])
print(knowledge["content"]["key_points"])
```

## 📚 Configuration

### Constitution Configuration (`config/constitution.yaml`)

```yaml
core_values:
  helpfulness:
    priority: 1
    weight: 1.0
  harmlessness:
    priority: 1
    weight: 1.0
  honesty:
    priority: 1
    weight: 1.0

behavioral_guidelines:
  respect_autonomy:
    enabled: true
  transparency:
    enabled: true
  privacy:
    enabled: true
  fairness:
    enabled: true

prohibited_actions:
  harm:
    level: critical
  illegal_activities:
    level: critical
  misinformation:
    level: high
```

### Agent Configuration

```python
agent_config = {
    "id": "custom_agent",
    "type": "research",
    "capabilities": [
        AgentCapability.RESEARCH,
        AgentCapability.ANALYSIS,
        AgentCapability.LEARNING
    ],
    "max_concurrent_tasks": 5,
    "learning_enabled": True,
    "constitution_level": "high",
    "priority": 1
}
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   AI Agentic Framework                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Constitution │    │    Agent     │    │     Web      │  │
│  │     AI       │◄──►│   Manager    │◄──►│   Learner    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         ▲                    ▲                    ▲          │
│         │                    │                    │          │
│         └────────────────────┼────────────────────┘          │
│                              │                                │
│                    ┌─────────▼─────────┐                     │
│                    │   Base Agent      │                     │
│                    └─────────┬─────────┘                     │
│                              │                                │
│         ┌────────────────────┼────────────────────┐          │
│         │                    │                    │          │
│  ┌──────▼──────┐    ┌───────▼──────┐    ┌───────▼──────┐   │
│  │  Research   │    │     Code     │    │   Analysis   │   │
│  │   Agent     │    │    Agent     │    │    Agent     │   │
│  └─────────────┘    └──────────────┘    └──────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Use Cases

### 1. Automated Research
```python
# Research multiple topics in parallel
topics = ["AI Ethics", "Quantum Computing", "Blockchain"]
for topic in topics:
    await framework.submit_task(
        description=f"Research {topic}",
        task_type="research",
        priority=7
    )
```

### 2. Comparative Analysis
```python
await framework.submit_task(
    description="Compare Python vs JavaScript for web development",
    task_type="research",
    priority=8
)
```

### 3. Deep Technical Investigation
```python
await framework.submit_task(
    description="Deep dive into transformer architectures",
    task_type="research",
    priority=9,
    context={"depth": "deep"}
)
```

## 🔒 Constitutional AI

The framework includes a comprehensive constitutional AI system that:

1. **Evaluates Actions**: Every action is evaluated against ethical principles
2. **Prevents Harm**: Blocks actions that could cause harm
3. **Maintains Transparency**: Logs all decisions for accountability
4. **Respects Privacy**: Protects user data and privacy
5. **Ensures Fairness**: Treats all users equally

Example:
```python
evaluation = constitution.evaluate_action(
    "Delete user data",
    {"user_consent": False}
)

if not evaluation["allowed"]:
    print(f"Action blocked: {evaluation['violations']}")
```

## 🌐 Web Learning System

### Features
- **No Content Filtering**: Direct access to all web content
- **Intelligent Caching**: Reduces redundant fetches
- **Multi-Source Learning**: Learns from multiple sources for accuracy
- **Confidence Scoring**: Rates knowledge based on source quality
- **Structured Extraction**: Converts web content into structured knowledge

### Learning Depths

- **Quick**: 3 sources, surface-level understanding
- **Moderate**: 5 sources, good overview
- **Comprehensive**: 8-10 sources, detailed understanding
- **Deep**: 15+ sources, expert-level knowledge with related topics

## 📊 Monitoring and Metrics

### Framework Status
```python
status = framework.get_status()
print(f"Uptime: {status['uptime_seconds']}s")
print(f"Agents: {status['agent_stats']['total_agents']}")
print(f"Tasks Completed: {status['agent_stats']['completed_tasks']}")
print(f"Success Rate: {status['agent_stats']['overall_success_rate']}")
```

### Agent Metrics
```python
agent_status = framework.get_agent_status("research_agent_1")
print(f"Tasks Completed: {agent_status['stats']['tasks_completed']}")
print(f"Success Rate: {agent_status['stats']['success_rate']}")
```

## 🛠️ Advanced Features

### Custom Agents

Create your own specialized agents:

```python
from base_agent import BaseAgent

class CustomAgent(BaseAgent):
    async def execute(self, task):
        # Your custom logic here
        result = await self.learn_about_topic(task.description)
        return {
            "status": "success",
            "result": result
        }
```

### Task Dependencies

```python
task1_id = await framework.submit_task(
    description="Research topic A",
    task_type="research"
)

task2_id = await framework.submit_task(
    description="Analyze results from topic A",
    task_type="analysis",
    context={"dependencies": [task1_id]}
)
```

## 🔧 Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
flake8 .
```

### Type Checking
```bash
mypy ai_agentic_framework.py
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Contact

For questions or support, please open an issue on GitHub.

## ⚠️ Important Notes

### No Content Filtering
This framework provides **direct, unfiltered access to web content**. The Web Learner component fetches and processes content from the internet without content filtering. This is by design to allow comprehensive learning, but users should:

1. Use the Constitutional AI system to enforce ethical guidelines
2. Implement additional filtering if needed for specific use cases
3. Be aware of potential exposure to inappropriate content
4. Ensure compliance with local laws and regulations

### Responsible AI
While this framework includes constitutional AI principles, users are responsible for:
- Ensuring ethical use of the system
- Complying with applicable laws and regulations
- Monitoring agent behavior
- Implementing additional safeguards as needed

## 🚀 Roadmap

- [ ] Add more specialized agent types (Code, Communication, Planning)
- [ ] Implement vector database for knowledge storage
- [ ] Add reinforcement learning for agent improvement
- [ ] Create web UI for monitoring and control
- [ ] Add multi-modal capabilities (images, audio)
- [ ] Implement distributed agent coordination
- [ ] Add blockchain integration for transparency
- [ ] Create agent marketplace

## 📚 Documentation

Full documentation available at: [Documentation Link]

## 🌟 Acknowledgments

- Inspired by Claude's Constitutional AI approach
- Built with modern async Python
- Designed for production use

---

**Built with ❤️ for the AI community**
