"""
Main evaluation script - runs full evaluation for both models
"""
import os
import sys
from evaluation.evaluation_runner import run_full_evaluation
import config

def main():
    print("\n" + "="*70)
    print("MINI PROJECT 3 - FULL EVALUATION")
    print("="*70)

    os.makedirs("results", exist_ok=True)
    
    # Check which model to use
    if len(sys.argv) > 1 and sys.argv[1] == "large":
        model = "gpt-4o"
        output_file = "results/results_gpt4o.xlsx"
        config.ACTIVE_MODEL = config.MODEL_LARGE
        print(f"\n🚀 Running evaluation with: {model}")
    else:
        model = "gpt-4o-mini"
        output_file = "results/results_gpt4o_mini.xlsx"
        config.ACTIVE_MODEL = config.MODEL_SMALL
        print(f"\n🚀 Running evaluation with: {model}")
    
    print(f"📊 Evaluating: 15 questions × 3 architectures")
    print(f"📁 Output: {output_file}")
    print(f"⏱️  Estimated time: 15-30 minutes")
    print(f"\nPress Ctrl+C to cancel...")
    print("="*70 + "\n")
    
    try:
        result = run_full_evaluation(
            output_xlsx=output_file,
            delay_sec=3.0
        )
        
        print("\n" + "="*70)
        print("✅ EVALUATION COMPLETE")
        print("="*70)
        print(f"\nResults saved to: {result}")
        print("\nNext steps:")
        print("  1. Open the Excel file to view detailed results")
        print("  2. Check the Summary sheet for accuracy breakdown")
        print("  3. Complete reflection questions Q0-Q5")
        
        if model == "gpt-4o-mini":
            print(f"\n💡 Tip: Run with 'python run_evaluation.py large' for gpt-4o")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Evaluation cancelled by user")
        print("   Progress has been saved to Excel file")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
