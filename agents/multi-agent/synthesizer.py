"""
Synthesizer - combines multiple specialist answers into one coherent response
"""
from agents.infra import AgentResult
from config import client, ACTIVE_MODEL
from typing import List


SYNTHESIZER_PROMPT = """You are a synthesis specialist. Your job is to combine answers from multiple specialized agents into one clear, coherent response.

Guidelines:
1. Merge information from all agents without losing important details
2. Resolve any contradictions (prefer higher-confidence agents)
3. Organize the answer logically (e.g., fundamentals → price → sentiment)
4. Include all specific numbers, tickers, and rankings mentioned
5. Keep the answer concise but complete
6. If an agent found no data, mention it briefly

Do NOT:
- Add information that wasn't in any agent's answer
- Speculate or fill gaps with your own knowledge
- Repeat the same information multiple times
- Make the answer unnecessarily long

Format:
- Use clear paragraphs or bullet points
- Lead with the most important information
- End with a brief summary if the answer is complex
"""


def run_synthesizer(
    question: str,
    specialist_results: List[AgentResult],
    verbose: bool = False
) -> str:
    """
    Synthesize multiple specialist answers into one final answer.
    
    Args:
        question: The original user question
        specialist_results: List of AgentResults from specialists
        verbose: Whether to print progress
    
    Returns:
        Final synthesized answer as a string
    """
    if verbose:
        print(f"  🔗 Synthesizing {len(specialist_results)} specialist answers...")
    
    if not specialist_results:
        return "No specialist answers were provided."
    
    # Build synthesis request
    agent_answers = "\n\n".join([
        f"### {result.agent_name} (confidence: {result.confidence:.0%})\n{result.answer}"
        for result in specialist_results
    ])
    
    synthesis_request = f"""
Original Question: {question}

Specialist Answers:
{agent_answers}

Please synthesize these into one coherent answer to the original question.
"""
    
    try:
        response = client.chat.completions.create(
            model=ACTIVE_MODEL,
            messages=[
                {"role": "system", "content": SYNTHESIZER_PROMPT},
                {"role": "user", "content": synthesis_request}
            ],
            temperature=0.3
        )
        
        final_answer = response.choices[0].message.content.strip()
        
        if verbose:
            print(f"     ✓ Synthesis complete ({len(final_answer)} chars)")
        
        return final_answer
        
    except Exception as e:
        if verbose:
            print(f"     ⚠️  Synthesis error: {e}")
        
        # Fallback: concatenate answers
        return "\n\n".join([
            f"**{r.agent_name}**: {r.answer}"
            for r in specialist_results
        ])
