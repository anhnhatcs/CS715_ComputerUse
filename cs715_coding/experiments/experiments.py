"""
Experiments for Claude Computer Use evaluation.
"""

import asyncio
import logging
import os
from pathlib import Path

# You may need to install these packages with pip
# pip install python-dotenv
# pip install cua-agent (for Computer and Agent)
try:
    from dotenv import load_dotenv
    from computer import Computer
    from agent import ComputerAgent, LLM, AgentLoop, LLMProvider
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Make sure to install required packages:")
    print("pip install python-dotenv cua-agent")


# Load environment variables from .env file in the parent directory
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path)

# Get API keys from environment or prompt user
anthropic_key = os.getenv("ANTHROPIC_API_KEY") or input("Enter your Anthropic API key: ")
openai_key = os.getenv("OPENAI_API_KEY") or input("Enter your OpenAI API key: ")


def setup_computer():
    """Setup the Computer instance for experiments."""
    computer = Computer(verbosity=logging.INFO)
    return computer


def setup_claude_agent(computer):
    """Set up a Claude-powered agent."""
    claude = LLM(
        provider=LLMProvider.ANTHROPIC,
        model="claude-3-opus-20240229",
        api_key=anthropic_key
    )
    
    agent = ComputerAgent(
        computer=computer,
        llm=claude,
        name="ClaudeAgent"
    )
    
    return agent


def setup_gpt4_agent(computer):
    """Set up a GPT-4-powered agent."""
    gpt4 = LLM(
        provider=LLMProvider.OPENAI,
        model="gpt-4o",
        api_key=openai_key
    )
    
    agent = ComputerAgent(
        computer=computer,
        llm=gpt4,
        name="GPT4Agent"
    )
    
    return agent


async def run_task(agent, task_description, max_turns=10):
    """Run a task with an agent and return the results."""
    loop = AgentLoop(agent=agent)
    
    conversation = await loop.run(
        user_message=task_description,
        max_turns=max_turns
    )
    
    return conversation


def run_benchmark(task_descriptions, agent_types=None, max_turns=10):
    """Run benchmark experiments with different tasks and agents."""
    if agent_types is None:
        agent_types = ["claude", "gpt4"]
        
    computer = setup_computer()
    results = {}
    
    for task in task_descriptions:
        task_results = {}
        
        for agent_type in agent_types:
            if agent_type == "claude":
                agent = setup_claude_agent(computer)
            elif agent_type == "gpt4":
                agent = setup_gpt4_agent(computer)
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            # Run the task
            conversation = asyncio.run(run_task(agent, task, max_turns))
            
            # Store results
            task_results[agent_type] = conversation
        
        results[task] = task_results
    
    return results


if __name__ == "__main__":
    # Example task descriptions
    tasks = [
        "Create a simple Python script that calculates the Fibonacci sequence",
        "Create a web scraper that extracts headlines from a news website",
        "Debug a Python function with a logic error"
    ]
    
    # Run experiments
    results = run_benchmark(tasks, agent_types=["claude"], max_turns=5)
    
    # Print results summary
    for task, task_results in results.items():
        print(f"Task: {task}")
        for agent_type, conversation in task_results.items():
            print(f"  Agent: {agent_type}")
            # Count turns (divide by 2 for user/assistant pairs)
            turns = len(conversation.messages) // 2
            print(f"  Turns: {turns}")
            print("")
