"""
Main script to run Mini Project 3 evaluation
"""

import argparse
from config import MODEL_SMALL, MODEL_LARGE, ACTIVE_MODEL
from evaluation.evaluation_runner import run_full_evaluation


def main():
    parser = argparse.ArgumentParser(description="Run Mini Project 3 Evaluation")
    parser.add_argument(
        "--model",
        choices=["small", "large", "both"],
        default="both",
        help="Which model to run evaluation with"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Delay between questions (seconds)"
    )
    
    args = parser.parse_args()
    
    if args.model in ["small", "both"]:
        print("\n" + "="*60)
        print("Running evaluation with gpt-4o-mini")
        print("="*60)
        run_full_evaluation(
            model=MODEL_SMALL,
            output_xlsx="results/results_gpt4o_mini.xlsx",
            delay_sec=args.delay
        )
    
    if args.model in ["large", "both"]:
        print("\n" + "="*60)
        print("Running evaluation with gpt-4o")
        print("="*60)
        run_full_evaluation(
            model=MODEL_LARGE,
            output_xlsx="results/results_gpt4o.xlsx",
            delay_sec=args.delay
        )
    
    print("\n✅ Evaluation complete!")


if __name__ == "__main__":
    main()