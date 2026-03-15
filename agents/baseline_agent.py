"""
Baseline agent - no tools, knowledge only
"""
from agents.infra import AgentResult
from config import client, ACTIVE_MODEL


def run_baseline(question: str, verbose: bool = True) -> AgentResult:
    """
    Baseline agent: single LLM call with no tools.
    Answers from training knowledge only.
    
    Args:
        question: The question to answer
        verbose: Whether to print progress
    
    Returns:
        AgentResult with answer and empty tools_called list
    """
    system_prompt = """You are a financial assistant. Please answer the question based on your knowledge.
If you are unsure of the answer, please explain honestly. Don't fabricate data."""
    
    if verbose:
        print(f"Running Baseline agent on: {question[:80]}...")
    
    response = client.chat.completions.create(
        model=ACTIVE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )
    
    answer = response.choices[0].message.content
    
    if verbose:
        print(f"✅ Baseline completed")
    
    return AgentResult(
        agent_name="Baseline",
        answer=answer,
        tools_called=[]
    )