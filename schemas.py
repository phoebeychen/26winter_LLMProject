"""
JSON schemas for all tools
"""

def _s(name, desc, props, req):
    return {"type":"function","function":{
        "name":name,"description":desc,
        "parameters":{"type":"object","properties":props,"required":req}}}

SCHEMA_TICKERS = _s("get_tickers_by_sector",
    "Return all stocks in a sector or industry from the local database.",
    {"sector":{"type":"string","description":"Sector or industry name"}}, ["sector"])

SCHEMA_PRICE = _s("get_price_performance",
    "Get % price change for a list of tickers over a time period. "
    "Valid periods: '1mo', '3mo', '6mo', 'ytd', '1y'. Use exactly these strings.",
    {"tickers":{"type":"array","items":{"type":"string"}},
     "period":{"type":"string","default":"1y","enum":["1mo","3mo","6mo","ytd","1y"]}}, ["tickers"])

SCHEMA_OVERVIEW = _s("get_company_overview",
    "Get fundamentals for one stock: P/E ratio, EPS, market cap, 52-week high and low.",
    {"ticker":{"type":"string","description":"Ticker symbol"}}, ["ticker"])

SCHEMA_STATUS = _s("get_market_status",
    "Check whether global stock exchanges are currently open or closed.", {}, [])

SCHEMA_MOVERS = _s("get_top_gainers_losers",
    "Get today's top gaining, top losing, and most actively traded stocks.", {}, [])

SCHEMA_NEWS = _s("get_news_sentiment",
    "Get latest news headlines and sentiment scores for a stock.",
    {"ticker":{"type":"string"},"limit":{"type":"integer","default":5}}, ["ticker"])

SCHEMA_SQL = _s("query_local_db",
    "Run a SQL SELECT on stocks.db.",
    {"sql":{"type":"string","description":"A valid SQL SELECT statement"}}, ["sql"])

# All schemas
ALL_SCHEMAS = [SCHEMA_TICKERS, SCHEMA_PRICE, SCHEMA_OVERVIEW,
               SCHEMA_STATUS, SCHEMA_MOVERS, SCHEMA_NEWS, SCHEMA_SQL]

# Tool subsets for specialists
MARKET_SPECIALIST_TOOLS = [SCHEMA_PRICE, SCHEMA_STATUS, SCHEMA_MOVERS, SCHEMA_TICKERS]
FUNDAMENTALS_SPECIALIST_TOOLS = [SCHEMA_OVERVIEW, SCHEMA_SQL, SCHEMA_TICKERS]
SENTIMENT_SPECIALIST_TOOLS = [SCHEMA_NEWS, SCHEMA_SQL]