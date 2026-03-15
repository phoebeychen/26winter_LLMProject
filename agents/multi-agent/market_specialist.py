"""
Market Specialist Agent - handles price data, market status, and gainers/losers
"""
from agents.infra import AgentResult, run_specialist_agent
from schemas import MARKET_SPECIALIST_TOOLS


MARKET_SPECIALIST_PROMPT = """You are a market data specialist. Your focus is on stock prices, market status, and market movers.

Your available tools:
1. get_tickers_by_sector(sector) - Get stock tickers for a sector
2. get_price_performance(tickers, period) - Get price changes for stocks
3. get_market_status() - Check if markets are open
4. get_top_gainers_losers() - Get today's top movers

Your responsibilities:
- Answer questions about stock price performance (returns, changes over time)
- Identify top gainers, losers, or best performers in a sector
- Check market operating hours and status
- First obtain ticker lists when needed, then fetch price data

Rules:
1. Always use get_tickers_by_sector FIRST if the question mentions a sector
2. Do not guess stock tickers - always query for them
3. For rankings, retrieve data for ALL relevant stocks and compare
4. Report exact numbers with proper units (%, $)
5. If data is unavailable, say so clearly - do not fabricate

Keep your answer focused on market/price data only. Do not speculate on fundamentals or sentiment.
"""


def run_market_specialist(task: str, verbose: bool = False) -> AgentResult:
    """
    Market specialist handles price, performance, and market status queries.
    
    Args:
        task: The specific task or question
        verbose: Whether to print progress
    
    Returns:
        AgentResult with market data analysis
    """
    return run_specialist_agent(
        agent_name="Market Specialist",
        system_prompt=MARKET_SPECIALIST_PROMPT,
        task=task,
        tool_schemas=MARKET_SPECIALIST_TOOLS,
        max_iters=10,
        verbose=verbose
    )
