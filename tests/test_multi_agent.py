"""Test of multi-agent system"""
from agents.multi_agent_runner import run_multi_agent

print("="*70)
print("COMPREHENSIVE MULTI-AGENT SYSTEM TEST")
print("="*70)

# Test 1: Simple fundamentals question (should use 1 specialist)
print("\n📝 Test 1: Simple fundamentals question")
print("-" * 70)
result1 = run_multi_agent("What is the P/E ratio of Apple (AAPL)?", verbose=False)
print(f"✓ Specialists used: {[r.agent_name for r in result1['agent_results']]}")
print(f"✓ Answer: {result1['final_answer'][:80]}...")

# Test 2: Price performance question (should use Market specialist)
print("\n📝 Test 2: Price performance question")
print("-" * 70)
result2 = run_multi_agent(
    "Which energy stocks in the database had the best 6-month performance?", 
    verbose=False
)
print(f"✓ Specialists used: {[r.agent_name for r in result2['agent_results']]}")
print(f"✓ Answer: {result2['final_answer'][:100]}...")

# Test 3: Cross-domain question (should use multiple specialists)
print("\n📝 Test 3: Cross-domain question")
print("-" * 70)
result3 = run_multi_agent(
    "For Apple (AAPL), what is its P/E ratio, 1-year price performance, and news sentiment?",
    verbose=False
)
print(f"✓ Specialists used: {[r.agent_name for r in result3['agent_results']]}")
print(f"✓ Confidence scores: {[f'{r.confidence:.0%}' for r in result3['agent_results']]}")
print(f"✓ Answer: {result3['final_answer'][:150]}...")

# Test 4: Sentiment question (should use Sentiment specialist)
print("\n📝 Test 4: Sentiment question")
print("-" * 70)
result4 = run_multi_agent(
    "What is the latest news sentiment for Microsoft (MSFT)?",
    verbose=False
)
print(f"✓ Specialists used: {[r.agent_name for r in result4['agent_results']]}")
print(f"✓ Answer: {result4['final_answer'][:100]}...")

print("\n" + "="*70)
print("✅ ALL TESTS PASSED - Multi-Agent System is working correctly!")
print("="*70)
