"""
Quick Start Example - AI Agentic Framework
Run this script to see the framework in action
"""

import asyncio
import sys
import os

# Import framework components
from constitution import ConstitutionalAI
from agent_manager import AgentManager, AgentConfig, Task, AgentCapability
from web_learner import WebLearner
from research_agent import ResearchAgent
from ai_agentic_framework import AIAgenticFramework

async def simple_example():
    """Simple example demonstrating basic framework usage"""
    
    print("\n" + "="*70)
    print(" AI AGENTIC FRAMEWORK - QUICK START EXAMPLE")
    print("="*70 + "\n")
    
    # 1. Initialize the framework
    print("1️⃣  Initializing AI Agentic Framework...")
    framework = AIAgenticFramework(config={
        "cache_dir": "./web_cache"
    })
    print("   ✓ Framework initialized\n")
    
    # 2. Create agents
    print("2️⃣  Creating AI agents...")
    agent_configs = [
        {
            "id": "researcher_1",
            "type": "research",
            "capabilities": [AgentCapability.RESEARCH, AgentCapability.ANALYSIS],
            "max_concurrent_tasks": 5,
            "learning_enabled": True
        }
    ]
    
    await framework.initialize_agents(agent_configs)
    print("   ✓ Created 1 research agent\n")
    
    # 3. Submit a research task
    print("3️⃣  Submitting research task...")
    task_id = await framework.submit_task(
        description="Research artificial intelligence and machine learning trends in 2024",
        task_type="research",
        priority=8,
        context={"depth": "moderate"}
    )
    print(f"   ✓ Task submitted with ID: {task_id}\n")
    
    # 4. Process the task
    print("4️⃣  Processing task (this may take a moment)...")
    await framework.agent_manager.process_task_queue()
    print("   ✓ Task processing complete\n")
    
    # 5. Get results
    print("5️⃣  Retrieving results...")
    if task_id in framework.agent_manager.completed_tasks:
        result = framework.agent_manager.completed_tasks[task_id]
        
        if result["status"] == "success":
            print("   ✓ Task completed successfully!\n")
            print("-" * 70)
            print("RESULTS:")
            print("-" * 70)
            
            task_result = result["result"]
            if "findings" in task_result:
                findings = task_result["findings"]
                print(f"\n📊 Research Type: {task_result.get('research_type', 'N/A')}")
                print(f"📝 Topic: {task_result.get('topic', 'N/A')}")
                print(f"\n💡 Summary:")
                print(findings.get("content", {}).get("summary", "No summary available")[:500])
                print("\n")
        else:
            print(f"   ⚠ Task failed: {result.get('error', 'Unknown error')}\n")
    else:
        print("   ⚠ Task results not found\n")
    
    # 6. Show framework status
    print("6️⃣  Framework Status:")
    print("-" * 70)
    status = framework.get_status()
    print(f"   Framework ID: {status['framework_id']}")
    print(f"   Uptime: {status['uptime_seconds']:.2f} seconds")
    print(f"   Total Agents: {status['agent_stats']['total_agents']}")
    print(f"   Active Agents: {status['agent_stats']['active_agents']}")
    print(f"   Completed Tasks: {status['agent_stats']['completed_tasks']}")
    print(f"   Knowledge Base: {status['knowledge_base_size']} topics learned")
    print()
    
    # 7. Export results
    print("7️⃣  Exporting results...")
    framework.export_state("framework_state.json")
    framework.export_knowledge_base("knowledge_base.json")
    print("   ✓ Results exported to:")
    print("      - framework_state.json")
    print("      - knowledge_base.json\n")
    
    # 8. Shutdown
    print("8️⃣  Shutting down framework...")
    await framework.shutdown()
    print("   ✓ Framework shutdown complete\n")
    
    print("="*70)
    print(" QUICK START COMPLETE!")
    print("="*70 + "\n")


async def advanced_example():
    """Advanced example with multiple agents and tasks"""
    
    print("\n" + "="*70)
    print(" AI AGENTIC FRAMEWORK - ADVANCED EXAMPLE")
    print("="*70 + "\n")
    
    # Initialize framework
    framework = AIAgenticFramework()
    
    # Create multiple agents with different capabilities
    agent_configs = [
        {
            "id": "researcher_alpha",
            "type": "research",
            "capabilities": [AgentCapability.RESEARCH, AgentCapability.ANALYSIS],
            "learning_enabled": True,
            "priority": 2
        },
        {
            "id": "researcher_beta",
            "type": "research",
            "capabilities": [AgentCapability.RESEARCH, AgentCapability.LEARNING],
            "learning_enabled": True,
            "priority": 1
        }
    ]
    
    await framework.initialize_agents(agent_configs)
    print("✓ Created 2 research agents with different priorities\n")
    
    # Submit multiple tasks
    tasks = [
        {
            "description": "Deep dive into quantum computing applications",
            "type": "research",
            "priority": 9
        },
        {
            "description": "Compare different neural network architectures",
            "type": "research",
            "priority": 8
        },
        {
            "description": "Survey the current state of AI ethics",
            "type": "research",
            "priority": 7
        }
    ]
    
    print("Submitting 3 research tasks...")
    task_ids = []
    for i, task in enumerate(tasks, 1):
        task_id = await framework.submit_task(**task)
        task_ids.append(task_id)
        print(f"  {i}. {task['description'][:50]}... (Priority: {task['priority']})")
    
    print("\nProcessing tasks in parallel...")
    await framework.agent_manager.process_task_queue()
    
    # Show results
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    for i, task_id in enumerate(task_ids, 1):
        if task_id in framework.agent_manager.completed_tasks:
            result = framework.agent_manager.completed_tasks[task_id]
            status = "✓ Success" if result["status"] == "success" else "✗ Failed"
            agent = result.get("agent", "Unknown")
            print(f"\nTask {i}: {status} (Agent: {agent})")
    
    # Show agent statistics
    print("\n" + "="*70)
    print("AGENT PERFORMANCE")
    print("="*70)
    
    for agent_id in ["researcher_alpha", "researcher_beta"]:
        stats = framework.get_agent_status(agent_id)
        if "stats" in stats:
            print(f"\n{agent_id}:")
            print(f"  Tasks Completed: {stats['stats']['tasks_completed']}")
            print(f"  Success Rate: {stats['stats']['success_rate']:.2%}")
    
    # Cleanup
    await framework.shutdown()
    
    print("\n" + "="*70)
    print(" ADVANCED EXAMPLE COMPLETE!")
    print("="*70 + "\n")


async def learning_example():
    """Example demonstrating direct learning capabilities"""
    
    print("\n" + "="*70)
    print(" DIRECT LEARNING EXAMPLE")
    print("="*70 + "\n")
    
    framework = AIAgenticFramework()
    
    # Learn about a topic directly
    topics = [
        "Constitutional AI",
        "Large Language Models",
        "Reinforcement Learning"
    ]
    
    print("Learning about multiple topics from the web...\n")
    
    for i, topic in enumerate(topics, 1):
        print(f"{i}. Learning about: {topic}")
        knowledge = await framework.learn_topic(topic, depth="moderate")
        
        content = knowledge.get("content", {})
        print(f"   Sources: {knowledge.get('source_count', 0)}")
        print(f"   Confidence: {knowledge.get('confidence', 0):.2%}")
        print(f"   Summary: {content.get('summary', 'N/A')[:150]}...")
        print()
    
    # Show knowledge base
    print("=" * 70)
    print(f"Knowledge Base: {len(framework.web_learner.knowledge_base)} topics stored")
    print("=" * 70)
    
    for topic in framework.web_learner.knowledge_base.keys():
        print(f"  • {topic}")
    
    await framework.shutdown()
    print("\n✓ Learning example complete!\n")


def main():
    """Main entry point"""
    
    print("\n🤖 AI Agentic Framework - Quick Start\n")
    print("Choose an example to run:")
    print("1. Simple Example (Recommended for first time)")
    print("2. Advanced Example (Multiple agents and tasks)")
    print("3. Learning Example (Direct web learning)")
    print("4. Run all examples")
    print("0. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        asyncio.run(simple_example())
    elif choice == "2":
        asyncio.run(advanced_example())
    elif choice == "3":
        asyncio.run(learning_example())
    elif choice == "4":
        print("\nRunning all examples...\n")
        asyncio.run(simple_example())
        asyncio.run(advanced_example())
        asyncio.run(learning_example())
    elif choice == "0":
        print("\nGoodbye! 👋\n")
        sys.exit(0)
    else:
        print("\n❌ Invalid choice. Please run again.\n")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
