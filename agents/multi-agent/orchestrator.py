"""
Orchestrator - coordinates the multi-agent system workflow
"""
from agents.infra import AgentResult
from config import client, ACTIVE_MODEL
from typing import List, Dict
import json


ORCHESTRATOR_PROMPT = """You are an orchestrator for a financial data analysis system. Your job is to read a user's question and decide which specialist agents to activate.

Available specialists:
1. **Market Specialist** - handles stock prices, performance, returns, market status, top gainers/losers
2. **Fundamentals Specialist** - handles P/E ratios, EPS, market cap, company profiles, filtering by sector/size
3. **Sentiment Specialist** - handles news sentiment, headlines, bullish/bearish analysis

Your task:
1. Analyze the question
2. Decide which specialists are needed (can be 1, 2, or all 3)
3. Write a specific sub-task for each specialist

Respond with JSON ONLY:
{
    "specialists_needed": ["Market", "Fundamentals", "Sentiment"],  // list of needed specialists
    "tasks": {
        "Market": "specific task for market specialist",
        "Fundamentals": "specific task for fundamentals specialist",
        "Sentiment": "specific task for sentiment specialist"
    },
    "reasoning": "brief explanation of your plan"
}

Examples:
- "What is Apple's P/E ratio?" → Only Fundamentals needed
- "Which energy stocks had best 6-month return?" → Only Market needed (get tickers + prices)
- "For top 3 semiconductor stocks by return, what are their P/E ratios and news sentiment?" → All 3 needed

Be specific in the sub-tasks. Include the question's key constraints (tickers, sectors, time periods, limits).
"""


def run_orchestrator(question: str, verbose: bool = False) -> Dict:
    """
    Orchestrator analyzes the question and creates an execution plan.
    
    Args:
        question: The user's question
        verbose: Whether to print progress
    
    Returns:
        Dict with 'specialists_needed', 'tasks', and 'reasoning'
    """
    if verbose:
        print(f"  📋 Orchestrator planning for: {question[:60]}...")
    
    try:
        response = client.chat.completions.create(
            model=ACTIVE_MODEL,
            messages=[
                {"role": "system", "content": ORCHESTRATOR_PROMPT},
                {"role": "user", "content": f"Question: {question}"}
            ],
            temperature=0.2
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON (handle markdown fences)
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        plan = json.loads(result_text)
        
        if verbose:
            print(f"     Plan: {len(plan.get('specialists_needed', []))} specialist(s)")
            print(f"     {plan.get('specialists_needed', [])}")
        
        return plan
        
    except Exception as e:
        if verbose:
            print(f"     ⚠️  Orchestrator error: {e}, falling back to all specialists")
        
        # Fallback: activate all specialists with the original question
        return {
            "specialists_needed": ["Market", "Fundamentals", "Sentiment"],
            "tasks": {
                "Market": question,
                "Fundamentals": question,
                "Sentiment": question
            },
            "reasoning": f"Orchestrator failed ({str(e)}), activating all specialists"
        }
