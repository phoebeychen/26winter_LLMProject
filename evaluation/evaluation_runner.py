"""
Full Evaluation Runner - evaluates all 3 architectures on 15 benchmark questions
Saves results to Excel with progress tracking
"""
import time
import pandas as pd
from dataclasses import dataclass, field
from typing import List

from agents.baseline_agent import run_baseline
from agents.single_agent import run_single_agent
from agents.multi_agent_runner import run_multi_agent
from evaluation.evaluator import run_evaluator
from benchmark_questions import BENCHMARK_QUESTIONS
from config import ACTIVE_MODEL


@dataclass
class EvalRecord:
    # Question
    question_id: str
    question: str
    complexity: str
    category: str
    expected: str
    
    # Baseline
    bl_answer: str = ""
    bl_time: float = 0.0
    bl_score: int = -1
    bl_reasoning: str = ""
    bl_hallucination: str = ""
    bl_issues: str = ""
    
    # Single agent
    sa_answer: str = ""
    sa_tools: str = ""
    sa_tool_count: int = 0
    sa_time: float = 0.0
    sa_score: int = -1
    sa_reasoning: str = ""
    sa_hallucination: str = ""
    sa_issues: str = ""
    
    # Multi agent
    ma_answer: str = ""
    ma_tools: str = ""
    ma_tool_count: int = 0
    ma_time: float = 0.0
    ma_confidence: str = ""
    ma_critic_issues: int = 0
    ma_agents: str = ""
    ma_architecture: str = ""
    ma_score: int = -1
    ma_reasoning: str = ""
    ma_hallucination: str = ""
    ma_issues: str = ""


# Column rename map
_COL_NAMES = {
    "question_id": "Question ID", "question": "Question", "complexity": "Difficulty",
    "category": "Category", "expected": "Expected Answer",
    "bl_answer": "Baseline Answer", "bl_time": "Baseline Time (s)",
    "bl_score": "Baseline Score /3", "bl_reasoning": "Baseline Eval Reasoning",
    "bl_hallucination": "Baseline Hallucination", "bl_issues": "Baseline Issues",
    "sa_answer": "SA Answer", "sa_tools": "SA Tools Used", "sa_tool_count": "SA Tool Count",
    "sa_time": "SA Time (s)", "sa_score": "SA Score /3", "sa_reasoning": "SA Eval Reasoning",
    "sa_hallucination": "SA Hallucination", "sa_issues": "SA Issues",
    "ma_answer": "MA Answer", "ma_tools": "MA Tools Used", "ma_tool_count": "MA Tool Count",
    "ma_time": "MA Time (s)", "ma_confidence": "MA Avg Confidence",
    "ma_critic_issues": "MA Critic Issue Count", "ma_agents": "MA Agents Activated",
    "ma_architecture": "MA Architecture", "ma_score": "MA Score /3",
    "ma_reasoning": "MA Eval Reasoning", "ma_hallucination": "MA Hallucination",
    "ma_issues": "MA Issues",
}


def _save_excel(records: List[EvalRecord], path: str):
    """Save evaluation results to Excel with Results and Summary sheets"""
    df = pd.DataFrame([r.__dict__ for r in records]).rename(columns=_COL_NAMES)
    
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        # Sheet 1: Full results
        df.to_excel(writer, index=False, sheet_name="Results")
        
        # Sheet 2: Summary by architecture × difficulty
        rows = []
        for arch, sc, tc, hc in [
            ("Baseline", "Baseline Score /3", "Baseline Time (s)", "Baseline Hallucination"),
            ("Single Agent", "SA Score /3", "SA Time (s)", "SA Hallucination"),
            ("Multi Agent", "MA Score /3", "MA Time (s)", "MA Hallucination"),
        ]:
            for tier in ["easy", "medium", "hard", "all"]:
                subset = df if tier == "all" else df[df["Difficulty"] == tier]
                valid = subset[subset[sc] >= 0]
                avg_s = valid[sc].mean() if len(valid) else 0
                rows.append({
                    "Architecture": arch,
                    "Difficulty": tier,
                    "Questions Scored": len(valid),
                    "Avg Score /3": round(avg_s, 2),
                    "Accuracy %": round(avg_s / 3 * 100, 1),
                    "Avg Time (s)": round(subset[tc].mean(), 1) if len(subset) > 0 else 0,
                    "Hallucinations": (subset[hc] == "True").sum(),
                })
        pd.DataFrame(rows).to_excel(writer, index=False, sheet_name="Summary")


def run_full_evaluation(output_xlsx: str = "results.xlsx", delay_sec: float = 3.0):
    """
    Run all 15 questions through baseline, single agent, and multi agent.
    Score each answer. Write results to Excel after every question.
    
    Args:
        output_xlsx: Output Excel file name
        delay_sec: Delay between questions (rate limiting)
    """
    records = []
    total = len(BENCHMARK_QUESTIONS)
    
    print(f"\n{'='*62}")
    print(f"  FULL EVALUATION  |  {total} questions × 3 architectures")
    print(f"  Model: {ACTIVE_MODEL}  |  Output: {output_xlsx}")
    print(f"{'='*62}\n")
    
    for i, q in enumerate(BENCHMARK_QUESTIONS, 1):
        print(f"[{i:02d}/{total}] {q['id']} ({q['complexity']:6s}) {q['question'][:52]}...")
        rec = EvalRecord(
            question_id=q["id"], question=q["question"],
            complexity=q["complexity"], category=q["category"],
            expected=q["expected"]
        )
        
        # ── Baseline ───────────────────────────────────────────
        print("         baseline  ...", end=" ", flush=True)
        try:
            t0 = time.time()
            bl = run_baseline(q["question"], verbose=False)
            rec.bl_answer = bl.answer.replace("\n", " ")
            rec.bl_time = round(time.time() - t0, 2)
            
            ev = run_evaluator(q["question"], q["expected"], bl.answer)
            rec.bl_score = ev.get("score", -1)
            rec.bl_reasoning = ev.get("reasoning", "")
            rec.bl_hallucination = str(ev.get("hallucination_detected", False))
            rec.bl_issues = " | ".join(ev.get("key_issues", []))
            print(f"  {rec.bl_time:5.1f}s  score {rec.bl_score}/3")
        except Exception as e:
            print(f"  ERROR: {e}")
        
        # ── Single Agent ───────────────────────────────────────
        print("         single    ...", end=" ", flush=True)
        try:
            t0 = time.time()
            sa = run_single_agent(q["question"], verbose=False)
            rec.sa_answer = sa.answer.replace("\n", " ")
            rec.sa_tools = ", ".join(sa.tools_called)
            rec.sa_tool_count = len(sa.tools_called)
            rec.sa_time = round(time.time() - t0, 2)
            
            ev = run_evaluator(q["question"], q["expected"], sa.answer)
            rec.sa_score = ev.get("score", -1)
            rec.sa_reasoning = ev.get("reasoning", "")
            rec.sa_hallucination = str(ev.get("hallucination_detected", False))
            rec.sa_issues = " | ".join(ev.get("key_issues", []))
            print(f"  {rec.sa_time:5.1f}s  score {rec.sa_score}/3")
        except Exception as e:
            print(f"  ERROR: {e}")
        
        # ── Multi Agent ────────────────────────────────────────
        print("         multi     ...", end=" ", flush=True)
        try:
            t0 = time.time()
            ma = run_multi_agent(q["question"], verbose=False)
            res = ma.get("agent_results", [])
            all_tools = [t for r in res for t in r.tools_called]
            all_issues = [iss for r in res for iss in r.issues_found]
            avg_conf = sum(r.confidence for r in res) / len(res) if res else 0.0
            
            rec.ma_answer = ma["final_answer"].replace("\n", " ")
            rec.ma_tools = ", ".join(dict.fromkeys(all_tools))
            rec.ma_tool_count = len(all_tools)
            rec.ma_time = round(time.time() - t0, 2)
            rec.ma_confidence = f"{avg_conf:.0%}"
            rec.ma_critic_issues = len(all_issues)
            rec.ma_agents = ", ".join(r.agent_name for r in res)
            rec.ma_architecture = ma.get("architecture", "")
            
            ev = run_evaluator(q["question"], q["expected"], ma["final_answer"])
            rec.ma_score = ev.get("score", -1)
            rec.ma_reasoning = ev.get("reasoning", "")
            rec.ma_hallucination = str(ev.get("hallucination_detected", False))
            rec.ma_issues = " | ".join(ev.get("key_issues", []))
            print(f"  {rec.ma_time:5.1f}s  score {rec.ma_score}/3")
        except Exception as e:
            print(f"  ERROR: {e}")
        
        records.append(rec)
        _save_excel(records, output_xlsx)
        
        if i < total:
            print(f"         ⏳ waiting {delay_sec}s ...\n")
            time.sleep(delay_sec)
    
    # ── Print summary ──────────────────────────────────────────
    print(f"\n{'='*62}  RESULTS")
    print(f"{'Architecture':<18} {'Easy':>8} {'Medium':>8} {'Hard':>8} {'Overall':>8}")
    print("─" * 52)
    for arch, sk in [("Baseline", "bl_score"), ("Single Agent", "sa_score"), ("Multi Agent", "ma_score")]:
        def pct(tier):
            s = [getattr(r, sk) for r in records
                 if getattr(r, sk) >= 0 and (tier == "all" or r.complexity == tier)]
            return f"{sum(s)/len(s)/3*100:.0f}%" if s else "—"
        print(f"{arch:<18} {pct('easy'):>8} {pct('medium'):>8} {pct('hard'):>8} {pct('all'):>8}")
    
    print(f"\n✅ Saved → {output_xlsx}")
    return output_xlsx


if __name__ == "__main__":
    run_full_evaluation(output_xlsx="results_gpt4o_mini.xlsx", delay_sec=3.0)
