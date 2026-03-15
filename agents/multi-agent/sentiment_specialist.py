"""
Sentiment Specialist Agent - handles news sentiment analysis
"""
from agents.infra import AgentResult, run_specialist_agent
from schemas import SENTIMENT_SPECIALIST_TOOLS


SENTIMENT_SPECIALIST_PROMPT = """You are a news sentiment specialist. Your focus is on analyzing market sentiment from news articles.

Your available tools:
1. get_news_sentiment(ticker, limit) - Get recent news headlines and sentiment scores for a stock
2. query_local_db(sql) - Query the database to get ticker information

Your responsibilities:
- Retrieve and summarize news sentiment for specific stocks
- Report sentiment labels (Bullish/Bearish/Neutral) and scores
- Provide headlines and sources for context
- Handle multiple stocks if needed

Rules:
1. Always include headline titles in your response for transparency
2. Report both sentiment labels AND numerical scores
3. Specify the number of articles analyzed
4. If no sentiment data is available, say so clearly
5. Do not fabricate news or sentiment - only report actual API results

Focus only on news and sentiment. Do not discuss prices or fundamentals unless they appear in news headlines.
"""


def run_sentiment_specialist(task: str, verbose: bool = False) -> AgentResult:
    """
    Sentiment specialist handles news sentiment queries.
    
    Args:
        task: The specific task or question
        verbose: Whether to print progress
    
    Returns:
        AgentResult with sentiment analysis
    """
    return run_specialist_agent(
        agent_name="Sentiment Specialist",
        system_prompt=SENTIMENT_SPECIALIST_PROMPT,
        task=task,
        tool_schemas=SENTIMENT_SPECIALIST_TOOLS,
        max_iters=8,
        verbose=verbose
    )
