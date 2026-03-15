"""
Test the Evaluator with calibration cases
"""
from evaluation.evaluator import run_evaluator

print("=" * 70)
print("EVALUATOR CALIBRATION TESTS")
print("=" * 70)

# Test 1: Correct answer (expect score=3)
print("\n📝 Calibration Test 1: Correct answer (expect score=3)")
print("-" * 70)
t1 = run_evaluator(
    question="What is the P/E ratio of Apple (AAPL)?",
    expected_answer="Should return AAPL P/E ratio as a single numeric value from Alpha Vantage.",
    agent_answer="The current P/E ratio of Apple Inc. (AAPL) is 33.45."
)
print(f"Score: {t1['score']}/3")
print(f"Hallucination: {t1['hallucination_detected']}")
print(f"Reasoning: {t1['reasoning']}")
print(f"✓ PASS" if t1['score'] >= 2 else "✗ FAIL - Expected high score for correct answer")

# Test 2: Fabricated number (expect hallucination=True, score≤1)
print("\n📝 Calibration Test 2: Fabricated number (expect hallucination=True, score≤1)")
print("-" * 70)
t2 = run_evaluator(
    question="What is the P/E ratio of Apple (AAPL)?",
    expected_answer="Should return AAPL P/E ratio as a single numeric value from Alpha Vantage.",
    agent_answer="Apple's P/E ratio is approximately 28.5 based on current market conditions."
)
print(f"Score: {t2['score']}/3")
print(f"Hallucination: {t2['hallucination_detected']}")
print(f"Reasoning: {t2['reasoning']}")
print(f"Issues: {t2['key_issues']}")
if t2['hallucination_detected']:
    print("✓ PASS - Correctly detected hallucination")
else:
    print("✗ FAIL - Should detect fabricated P/E as hallucination")

# Test 3: Refusal (expect score=0)
print("\n📝 Calibration Test 3: Refusal (expect score=0)")
print("-" * 70)
t3 = run_evaluator(
    question="What is the P/E ratio of Apple (AAPL)?",
    expected_answer="Should return AAPL P/E ratio as a single numeric value from Alpha Vantage.",
    agent_answer="I cannot retrieve real-time financial data. Please check Yahoo Finance."
)
print(f"Score: {t3['score']}/3")
print(f"Hallucination: {t3['hallucination_detected']}")
print(f"Reasoning: {t3['reasoning']}")
print(f"✓ PASS" if t3['score'] == 0 else "✗ FAIL - Refusal should score 0")

# Summary
print("\n" + "=" * 70)
print("CALIBRATION SUMMARY")
print("=" * 70)
all_passed = (
    t1['score'] >= 2 and 
    t2['hallucination_detected'] and 
    t3['score'] == 0
)
if all_passed:
    print("✅ ALL CALIBRATION TESTS PASSED")
    print("   Evaluator is ready for full evaluation run")
else:
    print("⚠️  SOME TESTS FAILED")
    print("   Review evaluator prompt or temperature settings")
