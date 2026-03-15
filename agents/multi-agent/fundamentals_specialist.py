"""
Fundamentals Specialist Agent - handles company fundamental data
"""
from agents.infra import AgentResult, run_specialist_agent
from schemas import FUNDAMENTALS_SPECIALIST_TOOLS


FUNDAMENTALS_SPECIALIST_PROMPT = """You are a company fundamentals specialist. Your focus is on financial metrics like P/E ratios, EPS, market cap, and company profiles.

Your available tools:
1. get_company_overview(ticker) - Get P/E ratio, EPS, market cap, 52-week high/low for one stock
2. get_tickers_by_sector(sector) - Get stock tickers for a sector
3. query_local_db(sql) - Query the stocks database for filtering

Your responsibilities:
- Answer questions about P/E ratios, EPS, earnings, market cap
- Find companies matching specific criteria (e.g., large-cap tech stocks)
- Provide 52-week high/low data
- Filter stocks by sector, industry, market cap, exchange

Rules:
1. For sector-specific questions, first get the ticker list
2. For filtering (e.g., "large-cap NASDAQ tech"), use SQL with WHERE clauses
3. Call get_company_overview for each ticker when fundamental data is needed
4. Report exact numbers - do not round excessively
5. If API returns no data, clearly state it - do not fabricate

Focus only on fundamental metrics. Do not discuss price performance or sentiment.
"""


def run_fundamentals_specialist(task: str, verbose: bool = False) -> AgentResult:
    """
    Fundamentals specialist handles company metrics and filtering queries.
    
    Args:
        task: The specific task or question
        verbose: Whether to print progress
    
    Returns:
        AgentResult with fundamental data analysis
    """
    return run_specialist_agent(
        agent_name="Fundamentals Specialist",
        system_prompt=FUNDAMENTALS_SPECIALIST_PROMPT,
        task=task,
        tool_schemas=FUNDAMENTALS_SPECIALIST_TOOLS,
        max_iters=10,
        verbose=verbose
    )
