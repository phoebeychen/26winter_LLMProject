"""
Tool functions for financial data retrieval
"""
import sqlite3
import requests
import yfinance as yf
import pandas as pd
from config import DB_PATH, ALPHAVANTAGE_API_KEY


def get_price_performance(tickers: list, period: str = "1y") -> dict:
    """Get % price change for a list of tickers over a period."""

    period_map = {
        '1m': '1mo',   # LLM常见错误
        '3m': '3mo',
        '6m': '6mo',
        '1month': '1mo',
        '3months': '3mo',
        '6months': '6mo',
    }

    if period in period_map:
        period = period_map[period]
        
    results = {}
    for ticker in tickers:
        try:
            data = yf.download(ticker, period=period, progress=False, auto_adjust=True)
            if data.empty:
                results[ticker] = {"error": "No data — possibly delisted"}
                continue
            start = float(data["Close"].iloc[0].item())
            end = float(data["Close"].iloc[-1].item())
            results[ticker] = {
                "start_price": round(start, 2),
                "end_price": round(end, 2),
                "pct_change": round((end - start) / start * 100, 2),
                "period": period,
            }
        except Exception as e:
            results[ticker] = {"error": str(e)}
    return results


def get_market_status() -> dict:
    """Open / closed status for global stock exchanges."""
    return requests.get(
        f"https://www.alphavantage.co/query?function=MARKET_STATUS"
        f"&apikey={ALPHAVANTAGE_API_KEY}", timeout=10
    ).json()


def get_top_gainers_losers() -> dict:
    """Today's top gaining, top losing, and most active tickers."""
    return requests.get(
        f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS"
        f"&apikey={ALPHAVANTAGE_API_KEY}", timeout=10
    ).json()


def get_news_sentiment(ticker: str, limit: int = 5) -> dict:
    """Latest headlines + sentiment for a ticker."""
    data = requests.get(
        f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
        f"&tickers={ticker}&limit={limit}&apikey={ALPHAVANTAGE_API_KEY}", timeout=10
    ).json()
    return {
        "ticker": ticker,
        "articles": [
            {
                "title": a.get("title"),
                "source": a.get("source"),
                "sentiment": a.get("overall_sentiment_label"),
                "score": a.get("overall_sentiment_score"),
            }
            for a in data.get("feed", [])[:limit]
        ],
    }


def query_local_db(sql: str) -> dict:
    """Run any SQL SELECT on stocks.db."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return {"columns": list(df.columns), "rows": df.to_dict(orient="records")}
    except Exception as e:
        return {"error": str(e)}


def get_company_overview(ticker: str) -> dict:
    """Get fundamentals for one stock from Alpha Vantage."""
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHAVANTAGE_API_KEY}"
    data = requests.get(url, timeout=10).json()
    
    if "Name" not in data:
        return {"error": f"No overview data for {ticker}"}
    
    return {
        "ticker": ticker,
        "name": data.get("Name", ""),
        "sector": data.get("Sector", ""),
        "pe_ratio": data.get("PERatio", ""),
        "eps": data.get("EPS", ""),
        "market_cap": data.get("MarketCapitalization", ""),
        "52w_high": data.get("52WeekHigh", ""),
        "52w_low": data.get("52WeekLow", "")
    }


def get_tickers_by_sector(sector: str) -> dict:
    """Query stocks.db for companies matching a sector or industry."""
    conn = sqlite3.connect(DB_PATH)
    
    # First try exact match on sector
    sql = "SELECT ticker, company, industry FROM stocks WHERE LOWER(sector) = LOWER(?) ORDER BY ticker"
    df = pd.read_sql_query(sql, conn, params=(sector,))
    
    # If no results, try fuzzy match on industry column
    if df.empty:
        sql = "SELECT ticker, company, industry FROM stocks WHERE LOWER(industry) LIKE LOWER(?) ORDER BY ticker"
        df = pd.read_sql_query(sql, conn, params=(f"%{sector}%",))
    
    conn.close()
    
    return {
        "sector": sector,
        "stocks": df.to_dict(orient="records")
    }