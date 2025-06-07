import os
import time
from import_xes import import_log, save_log_summary
from log_statistics import analyze_log
from dfg_miner import apply_dfg_miner
from inductive_miner import apply_inductive_miner
from conformance_checking import evaluate_model, compare_models

def main():
    start_time = time.time()
    
    # Create output directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("models/log_analysis", exist_ok=True)
    os.makedirs("models/dfg_miner", exist_ok=True)
    os.makedirs("models/inductive_miner", exist_ok=True)
    os.makedirs("models/evaluation", exist_ok=True)
    os.makedirs("models/comparison", exist_ok=True)
    
    # 1. Import log - use the filtered log instead
    log_path = "logs/filtered_log.xes"  # Use the filtered log
    print(f"Starting process mining analysis on {log_path}")
    log = import_log(log_path)
    
    # 2. Generate log summary and statistics
    print("\nGenerating log summary and statistics...")
    save_log_summary(log, "models/log_analysis")
    analyze_log(log, "models/log_analysis")
    
    # 3. Apply DFG Miner
    print("\nApplying DFG Miner...")
    _, dfg_net, dfg_im, dfg_fm = apply_dfg_miner(log, "models/dfg_miner")
    
    # 4. Apply Inductive Miner with just one noise threshold to reduce processing time
    print("\nApplying Inductive Miner...")
    _, inductive_net, inductive_im, inductive_fm = apply_inductive_miner(log, "models/inductive_miner/default", noise_threshold=0.2)
    
    # 5. Evaluate models - but with simplified evaluation to reduce processing time
    print("\nEvaluating models...")
    dfg_results = evaluate_model(log, dfg_net, dfg_im, dfg_fm, "dfg_miner", "models/evaluation/dfg")
    inductive_results = evaluate_model(log, inductive_net, inductive_im, inductive_fm, "inductive_miner", "models/evaluation/inductive")
    
    # 6. Compare models
    print("\nComparing models...")
    compare_models(dfg_results, inductive_results, "models/comparison")
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\nProcess mining analysis completed in {execution_time:.2f} seconds.")
    print("All results have been saved to the 'models' directory.")

if __name__ == "__main__":
    main()
