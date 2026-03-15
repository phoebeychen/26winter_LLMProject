"""
LLM-as-Judge Evaluator for scoring agent answers
"""
from config import client, ACTIVE_MODEL
import json


EVALUATOR_PROMPT = """You are an expert evaluator for financial Q&A systems. Your job is to score answers against expected criteria.

Scoring Rubric (0-3):
3 - Fully correct: All required data present, numbers accurate, conditions met
2 - Partially correct: Key data present but incomplete, minor gaps, or small inaccuracies  
1 - Mostly wrong: Attempted but wrong numbers, missed required conditions, or suspicious claims
0 - Complete failure: Refused to answer, said data unavailable without trying, or completely irrelevant

Hallucination Detection - Flag as TRUE if:
- Specific numbers (prices, P/E ratios, %) with no source or appear fabricated
- Stock tickers that seem invented or irrelevant
- Definitive "current data" claims without having called live data tools
- Contradictions or impossible values

Key Issues to Check:
- Missing required data points
- Wrong tickers or companies
- Incorrect rankings or comparisons
- Vague or evasive non-answers
- Numbers that don't make sense for the question

Respond with JSON ONLY:
{
    "score": 0-3,
    "max_score": 3,
    "reasoning": "one sentence explaining the score",
    "hallucination_detected": true/false,
    "key_issues": ["issue 1", "issue 2", ...]  // empty list if none
}

Be strict but fair. Focus on factual correctness against the expected answer criteria.
"""


def run_evaluator(question: str, expected_answer: str, agent_answer: str) -> dict:
    """
    Score one agent answer against the expected answer description.
    
    Args:
        question: The original question
        expected_answer: Description of what the answer should contain
        agent_answer: The actual answer from the agent
    
    Returns:
        Dict with keys:
            - score: int (0-3)
            - max_score: int (always 3)
            - reasoning: str
            - hallucination_detected: bool
            - key_issues: list[str]
    """
    # Fallback result in case of errors
    fallback = {
        "score": 0,
        "max_score": 3,
        "reasoning": "Evaluator parse error",
        "hallucination_detected": False,
        "key_issues": ["Evaluator failed to parse"]
    }
    
    evaluation_request = f"""
Question: {question}

Expected Answer Criteria:
{expected_answer}

Agent's Actual Answer:
{agent_answer}

Please score this answer. Return JSON only.
"""
    
    try:
        response = client.chat.completions.create(
            model=ACTIVE_MODEL,
            messages=[
                {"role": "system", "content": EVALUATOR_PROMPT},
                {"role": "user", "content": evaluation_request}
            ],
            temperature=0.1  # Low temperature for consistent scoring
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON (handle markdown fences)
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            json_lines = []
            in_code_block = False
            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or not line.strip().startswith("```"):
                    json_lines.append(line)
            result_text = "\n".join(json_lines)
        
        evaluation = json.loads(result_text)
        
        # Validate required fields
        required_fields = ["score", "max_score", "reasoning", "hallucination_detected", "key_issues"]
        for field in required_fields:
            if field not in evaluation:
                return fallback
        
        # Ensure score is in valid range
        evaluation["score"] = max(0, min(3, int(evaluation["score"])))
        evaluation["max_score"] = 3
        
        return evaluation
        
    except json.JSONDecodeError as e:
        fallback["key_issues"] = [f"JSON parse error: {str(e)}"]
        return fallback
    except Exception as e:
        fallback["key_issues"] = [f"Evaluator error: {str(e)}"]
        return fallback
