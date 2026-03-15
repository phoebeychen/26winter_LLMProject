"""
Critic Agent - verifies answers against raw tool data to detect hallucinations
"""
from agents.infra import AgentResult
from config import client, ACTIVE_MODEL
import json


CRITIC_PROMPT = """You are a fact-checking critic. Your job is to verify that an agent's answer is supported by the raw data it retrieved.

Check for these issues:
1. **Hallucinated numbers**: Claims specific values (prices, P/E ratios, percentages) not present in the tool data
2. **Fabricated tickers**: Mentions stock symbols that weren't in the retrieved data
3. **Wrong rankings**: Says "top 3" but shows different stocks than what the data indicates
4. **Contradictions**: Answer contradicts the tool output
5. **Unsupported claims**: Makes definitive statements without tool data to back them

For each agent answer, respond with JSON:
{
    "issues_found": ["issue 1", "issue 2", ...],  // empty list if no issues
    "confidence": 0.85,  // 0.0 to 1.0, how confident you are in the answer's accuracy
    "reasoning": "Brief explanation of your assessment"
}

Be strict but fair. Minor formatting differences are OK. Focus on factual correctness.
"""


def run_critic(agent_result: AgentResult, verbose: bool = False) -> AgentResult:
    """
    Critic reviews an agent's answer against its raw tool data.
    
    Args:
        agent_result: The AgentResult from a specialist to review
        verbose: Whether to print progress
    
    Returns:
        Updated AgentResult with confidence and issues_found populated
    """
    if verbose:
        print(f"  🔍 Critic reviewing {agent_result.agent_name}...")
    
    # Build the review request
    tools_summary = "\n".join([
        f"Tool: {tool_name}\nData: {json.dumps(data, indent=2)[:500]}..."
        for tool_name, data in agent_result.raw_data.items()
    ])
    
    if not tools_summary:
        tools_summary = "(No tools were called)"
    
    review_request = f"""
Agent: {agent_result.agent_name}
Tools Called: {agent_result.tools_called}

Raw Tool Data:
{tools_summary}

Agent's Answer:
{agent_result.answer}

Please fact-check this answer against the raw data. Return JSON only.
"""
    
    try:
        response = client.chat.completions.create(
            model=ACTIVE_MODEL,
            messages=[
                {"role": "system", "content": CRITIC_PROMPT},
                {"role": "user", "content": review_request}
            ],
            temperature=0.2
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON (handle markdown fences)
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        critique = json.loads(result_text)
        
        agent_result.confidence = critique.get("confidence", 0.5)
        agent_result.issues_found = critique.get("issues_found", [])
        agent_result.reasoning = critique.get("reasoning", "")
        
        if verbose:
            print(f"     Confidence: {agent_result.confidence:.0%}")
            if agent_result.issues_found:
                print(f"     Issues: {len(agent_result.issues_found)}")
        
    except Exception as e:
        if verbose:
            print(f"     ⚠️  Critic error: {e}")
        agent_result.confidence = 0.5
        agent_result.issues_found = [f"Critic failed: {str(e)}"]
        agent_result.reasoning = "Critic encountered an error"
    
    return agent_result
