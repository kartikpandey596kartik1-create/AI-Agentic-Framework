# Installation and Usage Guide

## 📦 Installation

### Step 1: Prerequisites
Ensure you have Python 3.8 or higher installed:
```bash
python --version
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python -c "import asyncio; print('✓ Installation successful!')"
```

## 🚀 Quick Start

### Option 1: Run the Quick Start Script
```bash
python quick_start.py
```

This interactive script will guide you through:
- Simple example (basic usage)
- Advanced example (multiple agents)
- Learning example (direct web learning)

### Option 2: Use as a Library

Create a new Python file:

```python
import asyncio
from ai_agentic_framework import AIAgenticFramework
from agent_manager import AgentCapability

async def main():
    # Initialize
    framework = AIAgenticFramework()
    
    # Create agents
    await framework.initialize_agents([{
        "id": "my_agent",
        "type": "research",
        "capabilities": [AgentCapability.RESEARCH]
    }])
    
    # Submit task
    task_id = await framework.submit_task(
        "Research AI trends",
        "research",
        priority=8
    )
    
    # Process
    await framework.agent_manager.process_task_queue()
    
    # Get results
    result = framework.agent_manager.completed_tasks[task_id]
    print(result)
    
    # Cleanup
    await framework.shutdown()

asyncio.run(main())
```

## 📖 Core Concepts

### 1. Constitutional AI
The framework enforces ethical principles:
- **Helpfulness**: Be maximally helpful
- **Harmlessness**: Avoid causing harm
- **Honesty**: Provide accurate information

### 2. Agent Types
Currently supported:
- **Research Agent**: Information gathering and analysis

Coming soon:
- Code Agent
- Communication Agent
- Planning Agent

### 3. Learning Depths
- **Quick**: Fast, surface-level (3 sources)
- **Moderate**: Balanced approach (5 sources)
- **Comprehensive**: Detailed understanding (8-10 sources)
- **Deep**: Expert-level knowledge (15+ sources)

### 4. Task Priorities
Scale of 1-10:
- **1-3**: Low priority, background tasks
- **4-6**: Normal priority
- **7-8**: High priority, important tasks
- **9-10**: Critical priority, urgent tasks

## 🔧 Configuration

### Custom Constitution
Edit `constitution.yaml` to customize ethical guidelines:

```yaml
core_values:
  helpfulness:
    priority: 1
    weight: 1.0
  # Add your values...

prohibited_actions:
  custom_restriction:
    level: high
    categories:
      - your_category
```

### Agent Configuration
Customize agent behavior:

```python
agent_config = {
    "id": "custom_agent",
    "type": "research",
    "capabilities": [
        AgentCapability.RESEARCH,
        AgentCapability.ANALYSIS
    ],
    "max_concurrent_tasks": 5,  # How many tasks simultaneously
    "learning_enabled": True,    # Enable automatic learning
    "constitution_level": "high", # Enforcement level
    "priority": 1                 # Agent priority (1-10)
}
```

## 📊 Monitoring

### Get Framework Status
```python
status = framework.get_status()
print(f"Uptime: {status['uptime_seconds']}s")
print(f"Tasks: {status['agent_stats']['completed_tasks']}")
```

### Get Agent Metrics
```python
agent_status = framework.get_agent_status("agent_id")
print(f"Success Rate: {agent_status['stats']['success_rate']}")
```

### Export Data
```python
# Export framework state
framework.export_state("state.json")

# Export knowledge base
framework.export_knowledge_base("knowledge.json")
```

## 🎯 Common Use Cases

### Research Task
```python
task_id = await framework.submit_task(
    description="Research quantum computing",
    task_type="research",
    priority=8
)
```

### Comparative Analysis
```python
task_id = await framework.submit_task(
    description="Compare Python vs JavaScript",
    task_type="research",
    priority=7
)
```

### Deep Investigation
```python
task_id = await framework.submit_task(
    description="Deep dive into neural networks",
    task_type="research",
    priority=9,
    context={"depth": "deep"}
)
```

### Direct Learning
```python
knowledge = await framework.learn_topic(
    "Blockchain Technology",
    depth="comprehensive"
)
print(knowledge["content"]["summary"])
```

## 🐛 Troubleshooting

### Import Errors
```bash
# Make sure you're in the right directory
cd AI-Agentic-Framework

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Network Issues
The web learner requires internet access. Check your connection and firewall settings.

### Memory Issues
For deep learning tasks, consider:
- Reducing the number of sources
- Using "moderate" depth instead of "deep"
- Processing tasks sequentially instead of parallel

### Async Errors
Always run async functions with `asyncio.run()`:
```python
asyncio.run(my_async_function())
```

## 💡 Best Practices

### 1. Always Use Context Managers
```python
async with framework:
    # Your code here
    pass
# Automatic cleanup
```

### 2. Handle Exceptions
```python
try:
    task_id = await framework.submit_task(...)
except ValueError as e:
    print(f"Task rejected: {e}")
```

### 3. Monitor Agent Performance
```python
# Regularly check agent metrics
for agent_id in framework.agent_manager.agents:
    stats = framework.get_agent_status(agent_id)
    if stats['stats']['success_rate'] < 0.8:
        print(f"Agent {agent_id} needs attention")
```

### 4. Use Appropriate Learning Depth
- Quick: For simple queries
- Moderate: Default choice
- Comprehensive: Important topics
- Deep: Critical research only

### 5. Set Realistic Priorities
Don't make everything priority 10. Use the full scale:
- 1-3: Nice to have
- 4-6: Normal work
- 7-8: Important
- 9-10: Critical/urgent

## 🔐 Security Considerations

### Web Learning
The web learner has **no content filtering**. Consider:
- Running in isolated environment
- Implementing custom filters
- Monitoring learned content
- Using constitutional AI effectively

### API Keys
If you add external API integrations:
- Store keys in environment variables
- Never commit keys to git
- Use `.env` files with `.gitignore`

### Data Privacy
- Don't process sensitive data
- Clear caches regularly
- Encrypt stored knowledge if needed

## 📈 Performance Tips

### 1. Use Caching
The web learner automatically caches content. Benefits:
- Faster repeat queries
- Reduced network usage
- Consistent results

### 2. Parallel Processing
Submit multiple tasks to leverage multiple agents:
```python
task_ids = []
for query in queries:
    task_id = await framework.submit_task(query)
    task_ids.append(task_id)

# All process in parallel
await framework.agent_manager.process_task_queue()
```

### 3. Optimize Agent Count
More agents ≠ better performance
- Start with 2-3 agents
- Monitor CPU and memory usage
- Scale based on task queue size

### 4. Clean Up Resources
```python
# Clear working memory after tasks
agent.clear_working_memory()

# Export and clear knowledge periodically
framework.export_knowledge_base("backup.json")
framework.web_learner.knowledge_base.clear()
```

## 🎓 Learning Resources

### Tutorials
1. [Basic Tutorial](docs/tutorials/basic.md)
2. [Advanced Topics](docs/tutorials/advanced.md)
3. [Custom Agents](docs/tutorials/custom_agents.md)

### API Reference
- [Framework API](docs/api/framework.md)
- [Agent Manager API](docs/api/agent_manager.md)
- [Web Learner API](docs/api/web_learner.md)

### Examples
- [Research Examples](examples/research/)
- [Multi-Agent Examples](examples/multi_agent/)
- [Integration Examples](examples/integrations/)

## 🤝 Getting Help

- 📖 Read the [Full Documentation](docs/)
- 💬 Ask questions in [Discussions](https://github.com/yourusername/AI-Agentic-Framework/discussions)
- 🐛 Report bugs in [Issues](https://github.com/yourusername/AI-Agentic-Framework/issues)
- 💡 Request features in [Issues](https://github.com/yourusername/AI-Agentic-Framework/issues)

## 🚀 Next Steps

1. ✅ Complete installation
2. ✅ Run quick_start.py
3. ✅ Read the core concepts
4. ✅ Try your first custom task
5. ✅ Explore advanced features

Happy coding! 🎉
