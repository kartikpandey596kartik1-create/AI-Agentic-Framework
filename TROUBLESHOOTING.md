# 🔧 Quick Fix Guide

## Error: "submit_task() got an unexpected keyword argument 'type'"

### Problem
The method signature uses `task_type` but you might be calling it with `type`.

### Solution

**WRONG:**
```python
await framework.submit_task(
    "Research AI trends",
    type="research",  # ❌ Wrong parameter name
    priority=8
)
```

**CORRECT:**
```python
await framework.submit_task(
    "Research AI trends",
    task_type="research",  # ✅ Correct parameter name
    priority=8
)
```

### Quick Start Examples (Fixed)

**Example 1: Basic task submission**
```python
import asyncio
from ai_agentic_framework import AIAgenticFramework
from agent_manager import AgentCapability

async def main():
    # Initialize framework
    framework = AIAgenticFramework()
    
    # Initialize agents
    await framework.initialize_agents([{
        "id": "research_agent_1",
        "type": "research",
        "capabilities": [AgentCapability.RESEARCH]
    }])
    
    # Submit task - CORRECT WAY
    task_id = await framework.submit_task(
        description="Research quantum computing",
        task_type="research",  # ✅ Use task_type
        priority=8
    )
    
    # Process tasks
    await framework.agent_manager.process_task_queue()
    
    # Get result
    if task_id in framework.agent_manager.completed_tasks:
        result = framework.agent_manager.completed_tasks[task_id]
        print(result)
    
    # Shutdown
    await framework.shutdown()

asyncio.run(main())
```

**Example 2: Multiple tasks**
```python
# Submit multiple tasks
tasks = [
    {
        "description": "Research AI trends",
        "task_type": "research",  # ✅
        "priority": 8
    },
    {
        "description": "Analyze market data",
        "task_type": "analysis",  # ✅
        "priority": 7
    }
]

task_ids = []
for task in tasks:
    task_id = await framework.submit_task(**task)
    task_ids.append(task_id)
```

**Example 3: With context**
```python
task_id = await framework.submit_task(
    description="Deep research on transformers",
    task_type="research",  # ✅
    priority=9,
    context={"depth": "comprehensive"}
)
```

### Alternative: Positional Arguments

You can also use positional arguments:

```python
# Positional (description, task_type, priority)
task_id = await framework.submit_task(
    "Research AI trends",
    "research",
    8
)
```

### Method Signature Reference

```python
async def submit_task(
    self,
    description: str,        # Required: Task description
    task_type: str = "research",  # Optional: Type of task
    priority: int = 5,       # Optional: Priority 1-10
    context: Optional[Dict[str, Any]] = None  # Optional: Extra context
) -> str:  # Returns: task_id
```

### Common Mistakes & Fixes

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| `type="research"` | `task_type="research"` |
| `task="research"` | `task_type="research"` |
| `kind="research"` | `task_type="research"` |

### If You Still Get Errors

**Check your code for:**
1. Make sure you're using `task_type` not `type`
2. Make sure you have `description` as first parameter
3. Make sure framework is properly initialized

**Debug your code:**
```python
# Add this before calling submit_task
print("About to submit task...")
print(f"Description: Research AI")
print(f"Task Type: research")  # Check this matches parameter name

# Then call with explicit parameter names
task_id = await framework.submit_task(
    description="Research AI",
    task_type="research",  # Explicit
    priority=8
)
```

### Working Complete Example

Save this as `test_framework.py`:

```python
import asyncio
from ai_agentic_framework import AIAgenticFramework
from agent_manager import AgentCapability

async def test():
    print("Initializing framework...")
    framework = AIAgenticFramework()
    
    print("Creating agent...")
    await framework.initialize_agents([{
        "id": "agent_1",
        "type": "research",
        "capabilities": [AgentCapability.RESEARCH]
    }])
    
    print("Submitting task...")
    task_id = await framework.submit_task(
        description="Research Python programming",
        task_type="research",
        priority=5
    )
    
    print(f"Task submitted: {task_id}")
    
    print("Processing task...")
    await framework.agent_manager.process_task_queue()
    
    print("Checking result...")
    if task_id in framework.agent_manager.completed_tasks:
        result = framework.agent_manager.completed_tasks[task_id]
        print(f"Status: {result['status']}")
    
    await framework.shutdown()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(test())
```

Run it:
```cmd
cd F:\AI-Agentic-Framework
python test_framework.py
```

### Still Having Issues?

If you're still getting errors, share the exact code you're running and I'll help debug it!

---

**TL;DR: Use `task_type="research"` not `type="research"`** ✅
