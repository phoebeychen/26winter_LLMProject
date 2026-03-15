"""
app.py — MP3 Streamlit Deployment
Mini Project 3: Agentic AI in FinTech

Usage:
    streamlit run app.py          (from repo root)
    python -m streamlit run app.py

This file lives at repo root alongside agents/, tools.py, config.py.
It imports agent functions from those modules so there is no code duplication.
"""

import os, sys, time
import streamlit as st
import yfinance as yf
from dotenv import load_dotenv
from openai import OpenAI

# ── Ensure repo root is on sys.path so sibling modules can be imported ──
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

load_dotenv()

# ── Import shared config (sets ACTIVE_MODEL, client, API keys) ──
import config

# ── Import agent runner functions from modules ──
from agents.baseline_agent   import run_baseline
from agents.single_agent     import run_single_agent
from agents.multi_agent_runner import run_multi_agent

# ── Patch get_company_overview with yfinance fallback ─────────────────────
# Alpha Vantage free tier has 25 req/day; yfinance has no rate limit.
# We monkey-patch tools.get_company_overview so the agents automatically
# fall back to yfinance when AV is rate-limited.
import tools as _tools

def _get_company_overview_with_fallback(ticker: str) -> dict:
    """Try Alpha Vantage first; fall back to yfinance on rate-limit."""
    import requests
    url = (
        "https://www.alphavantage.co/query"
        f"?function=OVERVIEW&symbol={ticker}&apikey={config.ALPHAVANTAGE_API_KEY}"
    )
    try:
        data = requests.get(url, timeout=10).json()
        if data.get("Name"):
            return {
                "ticker"    : data.get("Symbol", ticker),
                "name"      : data.get("Name", ""),
                "sector"    : data.get("Sector", ""),
                "pe_ratio"  : str(data.get("PERatio", "")),
                "eps"       : str(data.get("EPS", "")),
                "market_cap": str(data.get("MarketCapitalization", "")),
                "52w_high"  : str(data.get("52WeekHigh", "")),
                "52w_low"   : str(data.get("52WeekLow", "")),
            }
    except Exception:
        pass  # fall through to yfinance

    # yfinance fallback
    try:
        info = yf.Ticker(ticker).info
        name = info.get("longName") or info.get("shortName")
        if not name:
            return {"error": f"No overview data for {ticker}"}
        return {
            "ticker"    : ticker,
            "name"      : name,
            "sector"    : info.get("sector", ""),
            "pe_ratio"  : str(info.get("trailingPE", "N/A")),
            "eps"       : str(info.get("trailingEps", "N/A")),
            "market_cap": str(info.get("marketCap", "N/A")),
            "52w_high"  : str(info.get("fiftyTwoWeekHigh", "N/A")),
            "52w_low"   : str(info.get("fiftyTwoWeekLow", "N/A")),
            "source"    : "yfinance",
        }
    except Exception as e:
        return {"error": str(e)}

# Replace the function in the tools module so all agents pick it up
_tools.get_company_overview = _get_company_overview_with_fallback


# ── Helper: inject conversation history into a question string ─────────────
def _enrich_question(prior_messages: list, question: str) -> str:
    """
    Prepend prior conversation turns to the question so agents can resolve
    references like "that", "the two", "it" from earlier exchanges.

    For Single Agent, the full message list is passed directly to the LLM;
    for Multi-Agent we format it as text because run_multi_agent() only
    accepts a plain question string (the orchestrator then sees all context).
    """
    if not prior_messages:
        return question
    lines = []
    for m in prior_messages:
        role = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"{role}: {m['content'][:400]}")
    history = "\n".join(lines)
    return (
        f"Conversation history (use this to resolve pronouns and references):\n"
        f"{history}\n\n"
        f"Current question: {question}"
    )


# ── Agent wrappers that accept (prior_messages, question, model) ───────────

def _call_baseline(prior_messages: list, question: str, model: str):
    """Baseline: single LLM call, no tools."""
    config.ACTIVE_MODEL = model
    enriched = _enrich_question(prior_messages, question)
    return run_baseline(enriched, verbose=False)


def _call_single_agent(prior_messages: list, question: str, model: str):
    """Single Agent: all 7 tools, conversation history injected."""
    config.ACTIVE_MODEL = model
    enriched = _enrich_question(prior_messages, question)
    return run_single_agent(enriched, verbose=False)


def _call_multi_agent(prior_messages: list, question: str, model: str) -> dict:
    """
    Multi-Agent: Orchestrator → Specialists → Critic → Synthesizer.

    Conversation history is injected into the question string so the
    Orchestrator can resolve references before delegating to specialists.
    """
    config.ACTIVE_MODEL = model
    enriched = _enrich_question(prior_messages, question)
    t0     = time.time()
    result = run_multi_agent(enriched, verbose=False)
    result["elapsed_sec"] = round(time.time() - t0, 2)
    return result


# ── Streamlit page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="FinTech AI Agent",
    page_icon="📈",
    layout="wide",
)

# Initialise OpenAI client once in session state
if "client" not in st.session_state:
    st.session_state.client = OpenAI(api_key=config.OPENAI_API_KEY)
    config.client = st.session_state.client   # keep config.client in sync


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    st.divider()

    agent_choice = st.selectbox(
        "Agent Architecture",
        options=["Single Agent", "Multi-Agent"],
        help=(
            "**Single Agent** — one LLM with all 7 tools.\n\n"
            "**Multi-Agent** — Orchestrator delegates to Market / "
            "Fundamentals / Sentiment specialists; Critic verifies; "
            "Synthesizer combines."
        ),
    )

    model_choice = st.selectbox(
        "Model",
        options=[config.MODEL_SMALL, config.MODEL_LARGE],
        help="gpt-4o-mini is faster and cheaper; gpt-4o is more capable on complex questions.",
    )

    st.divider()
    st.caption(
        "**Conversational memory** — full chat history is sent on every "
        "turn so the agent can resolve follow-ups like "
        "*'How does that compare to AMD?'* without repeating context."
    )
    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages      = []
        st.session_state.agent_history = []
        st.rerun()

    st.divider()
    st.caption("MP3 · Agentic AI in FinTech")


# ── Session state ──────────────────────────────────────────────────────────
# messages      → what we render in the chat UI
#   each item: {"role": "user"/"assistant", "content": str, "meta": str}
#
# agent_history → what we pass to the LLM (plain OpenAI message format)
#   each item: {"role": "user"/"assistant", "content": str}

if "messages"      not in st.session_state:
    st.session_state.messages      = []
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []


# ── Main chat UI ───────────────────────────────────────────────────────────
st.title("📈 FinTech AI Agent")
st.caption(
    "Ask about stock prices, fundamentals, news sentiment, and sector data. "
    "Follow-up questions like *'How does that compare to AMD?'* are handled automatically."
)

# Render stored conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("meta"):
            st.caption(msg["meta"])

# Chat input
user_input = st.chat_input("Ask a financial question…")

if user_input:
    # 1. Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Record in both lists
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.agent_history.append({"role": "user", "content": user_input})

    # 3. prior_history = everything except the message just added
    prior = st.session_state.agent_history[:-1]

    # 4. Call the selected agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                if agent_choice == "Single Agent":
                    result       = _call_single_agent(prior, user_input, model_choice)
                    answer       = result.answer
                    tools_used   = result.tools_called
                    architecture = "Single Agent"

                else:  # Multi-Agent
                    ma_out       = _call_multi_agent(prior, user_input, model_choice)
                    answer       = ma_out["final_answer"]
                    tools_used   = [
                        t for r in ma_out.get("agent_results", [])
                        for t in r.tools_called
                    ]
                    architecture = ma_out.get("architecture", "Multi-Agent")

            except Exception as e:
                answer       = f"❌ Error: {e}"
                tools_used   = []
                architecture = agent_choice

        st.markdown(answer)

        # Metadata badge: architecture | model | tools used
        tools_str = ", ".join(dict.fromkeys(tools_used)) if tools_used else "no tools"
        meta = f"🤖 **{architecture}** · 🧠 `{model_choice}` · 🔧 {tools_str}"
        st.caption(meta)

    # 5. Persist assistant reply
    st.session_state.messages.append({
        "role"   : "assistant",
        "content": answer,
        "meta"   : meta,
    })
    st.session_state.agent_history.append({
        "role"   : "assistant",
        "content": answer,
    })
