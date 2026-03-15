"""
Multi-Agent System Runner - main entry point for multi-agent architecture
"""
import sys
import os
import time
from typing import Dict, List

# Add agents/multi-agent to path so we can import from it
multi_agent_path = os.path.join(os.path.dirname(__file__), 'multi-agent')
if multi_agent_path not in sys.path:
    sys.path.insert(0, multi_agent_path)

# Import infrastructure
from agents.infra import AgentResult

# Import multi-agent components
from orchestrator import run_orchestrator
from market_specialist import run_market_specialist
from fundamentals_specialist import run_fundamentals_specialist
from sentiment_specialist import run_sentiment_specialist
from critic import run_critic
from synthesizer import run_synthesizer


def run_multi_agent(question: str, verbose: bool = True) -> Dict:
    """
    Main entry point for the multi-agent system.
    
    Architecture: Orchestrator → Specialists → Critic → Synthesizer
    
    Args:
        question: The user's question
        verbose: Whether to print progress
    
    Returns:
        Dict with keys:
            - final_answer: str
            - agent_results: List[AgentResult]
            - elapsed_sec: float
            - architecture: str
    """
    start_time = time.time()
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🚀 Multi-Agent System")
        print(f"{'='*60}")
    
    # Step 1: Orchestrator decides which specialists to activate
    plan = run_orchestrator(question, verbose=verbose)
    specialists_needed = plan.get("specialists_needed", [])
    tasks = plan.get("tasks", {})
    
    # Step 2: Run the selected specialists
    specialist_map = {
        "Market": run_market_specialist,
        "Fundamentals": run_fundamentals_specialist,
        "Sentiment": run_sentiment_specialist
    }
    
    agent_results: List[AgentResult] = []
    
    for specialist_name in specialists_needed:
        if specialist_name in specialist_map and specialist_name in tasks:
            if verbose:
                print(f"\n  ▶️  Activating {specialist_name} Specialist...")
            
            specialist_func = specialist_map[specialist_name]
            task = tasks[specialist_name]
            
            try:
                result = specialist_func(task, verbose=verbose)
                agent_results.append(result)
            except Exception as e:
                if verbose:
                    print(f"     ⚠️  {specialist_name} Specialist failed: {e}")
                # Create a placeholder result
                agent_results.append(AgentResult(
                    agent_name=f"{specialist_name} Specialist",
                    answer=f"Error: {str(e)}",
                    tools_called=[],
                    raw_data={}
                ))
    
    # Step 3: Critic reviews each specialist's answer
    if verbose:
        print(f"\n  🔍 Critic Review Phase...")
    
    for result in agent_results:
        run_critic(result, verbose=verbose)
    
    # Step 4: Synthesizer combines answers
    if verbose:
        print(f"\n  🔗 Synthesis Phase...")
    
    final_answer = run_synthesizer(question, agent_results, verbose=verbose)
    
    elapsed = time.time() - start_time
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"✅ Multi-Agent completed in {elapsed:.1f}s")
        print(f"{'='*60}\n")
    
    return {
        "final_answer": final_answer,
        "agent_results": agent_results,
        "elapsed_sec": elapsed,
        "architecture": "Orchestrator+Specialists+Critic"
    }
