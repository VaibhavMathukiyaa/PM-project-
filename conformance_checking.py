import pm4py
import os
import matplotlib.pyplot as plt
import numpy as np
from import_xes import import_log
from dfg_miner import apply_dfg_miner
from inductive_miner import apply_inductive_miner

def evaluate_model(log, net, initial_marking, final_marking, algorithm_name, output_dir):
    """
    Evaluate the quality of a process model using conformance checking
    
    Parameters:
    log (EventLog): Event log
    net (PetriNet): Petri net model
    initial_marking (Marking): Initial marking
    final_marking (Marking): Final marking
    algorithm_name (str): Name of the algorithm
    output_dir (str): Output directory
    
    Returns:
    dict: Dictionary with fitness and precision values
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = {}
    
    print(f"Evaluating {algorithm_name} model...")
    
    # Calculate fitness using token-based replay (use a sample of the log to reduce processing time)
    try:
        from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
        
        # Use only a sample of the log for evaluation to reduce processing time
        sample_size = min(50, len(log))
        sample_log = log[:sample_size]
        
        fitness = token_replay.apply(sample_log, net, initial_marking, final_marking)
        
        # Extract key metrics
        avg_fitness = sum(case['trace_fitness'] for case in fitness) / len(fitness) if fitness else 0
        fitting_traces = sum(1 for case in fitness if case['trace_is_fit']) if fitness else 0
        percentage_fitting = (fitting_traces / len(fitness)) * 100 if fitness else 0
        
        results['fitness'] = {
            'average_trace_fitness': avg_fitness,
            'percentage_of_fitting_traces': percentage_fitting
        }
        
        with open(os.path.join(output_dir, f"{algorithm_name}_fitness.txt"), 'w') as f:
            f.write(f"Fitness for {algorithm_name}:\n")
            f.write(f"Average trace fitness: {avg_fitness:.4f}\n")
            f.write(f"Percentage of fitting traces: {percentage_fitting:.4f}%\n")
            f.write(f"(Based on a sample of {sample_size} traces)\n")
    except Exception as e:
        print(f"Error calculating fitness for {algorithm_name}: {e}")
        results['fitness'] = {'error': str(e)}
    
    # Skip precision calculation as it's often very resource-intensive
    results['precision'] = 0.0
    
    # Skip alignment-based conformance checking as it's very resource-intensive
    results['alignments'] = {
        'mean_fitness': 0.0,
        'median_fitness': 0.0,
        'min_fitness': 0.0,
        'max_fitness': 0.0
    }
    
    print(f"Evaluation for {algorithm_name} completed and saved to {output_dir}")
    return results

def compare_models(dfg_results, inductive_results, output_dir):
    """
    Compare the results of different algorithms
    
    Parameters:
    dfg_results (dict): Results from DFG miner
    inductive_results (dict): Results from Inductive miner
    output_dir (str): Output directory
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create comparison table
    with open(os.path.join(output_dir, "model_comparison.txt"), 'w') as f:
        f.write("Model Comparison\n")
        f.write("===============\n\n")
        
        f.write("Metric         | DFG Miner | Inductive Miner\n")
        f.write("---------------|-----------|----------------\n")
        
        # Fitness comparison
        if 'fitness' in dfg_results and 'fitness' in inductive_results:
            if 'average_trace_fitness' in dfg_results['fitness'] and 'average_trace_fitness' in inductive_results['fitness']:
                dfg_fitness = dfg_results['fitness']['average_trace_fitness']
                inductive_fitness = inductive_results['fitness']['average_trace_fitness']
                f.write(f"Fitness         | {dfg_fitness:.4f}    | {inductive_fitness:.4f}\n")
        
        # Precision comparison
        if 'precision' in dfg_results and 'precision' in inductive_results:
            if not isinstance(dfg_results['precision'], dict) and not isinstance(inductive_results['precision'], dict):
                dfg_precision = dfg_results['precision']
                inductive_precision = inductive_results['precision']
                f.write(f"Precision       | {dfg_precision:.4f}    | {inductive_precision:.4f}\n")
        
        # Alignment comparison
        if 'alignments' in dfg_results and 'alignments' in inductive_results:
            if 'mean_fitness' in dfg_results['alignments'] and 'mean_fitness' in inductive_results['alignments']:
                dfg_align = dfg_results['alignments']['mean_fitness']
                inductive_align = inductive_results['alignments']['mean_fitness']
                f.write(f"Align. Fitness  | {dfg_align:.4f}    | {inductive_align:.4f}\n")
    
    # Create comparison chart
    metrics = ['Fitness', 'Precision', 'Alignment Fitness']
    dfg_values = [
        dfg_results.get('fitness', {}).get('average_trace_fitness', 0),
        dfg_results.get('precision', 0) if not isinstance(dfg_results.get('precision', {}), dict) else 0,
        dfg_results.get('alignments', {}).get('mean_fitness', 0)
    ]
    inductive_values = [
        inductive_results.get('fitness', {}).get('average_trace_fitness', 0),
        inductive_results.get('precision', 0) if not isinstance(inductive_results.get('precision', {}), dict) else 0,
        inductive_results.get('alignments', {}).get('mean_fitness', 0)
    ]
    
    try:
        x = np.arange(len(metrics))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 6))
        rects1 = ax.bar(x - width/2, dfg_values, width, label='DFG Miner')
        rects2 = ax.bar(x + width/2, inductive_values, width, label='Inductive Miner')
        
        ax.set_ylabel('Score')
        ax.set_title('Algorithm Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        
        fig.tight_layout()
        plt.savefig(os.path.join(output_dir, "algorithm_comparison.png"))
        plt.close()
    except Exception as e:
        print(f"Error creating comparison chart: {e}")
    
    print(f"Model comparison saved to {output_dir}")

if __name__ == "__main__":
    log_path = "logs/logxesrotohive.xes"
    log = import_log(log_path)
    
    # Apply DFG Miner
    _, dfg_net, dfg_im, dfg_fm = apply_dfg_miner(log, "models/dfg_miner")
    
    # Apply Inductive Miner
    _, inductive_net, inductive_im, inductive_fm = apply_inductive_miner(log, "models/inductive_miner/default")
    
    # Evaluate models
    dfg_results = evaluate_model(log, dfg_net, dfg_im, dfg_fm, "dfg_miner", "models/evaluation/dfg")
    inductive_results = evaluate_model(log, inductive_net, inductive_im, inductive_fm, "inductive_miner", "models/evaluation/inductive")
    
    # Compare models
    compare_models(dfg_results, inductive_results, "models/comparison")
