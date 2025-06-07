# filter_log.py
import pm4py
import os

def filter_log(input_path, output_path, max_cases=500):
    """
    Filter the log to a smaller size
    
    Parameters:
    input_path (str): Path to the input XES file
    output_path (str): Path to save the filtered XES file
    max_cases (int): Maximum number of cases to include
    """
    print(f"Loading log from {input_path}...")
    log = pm4py.read_xes(input_path)
    
    print(f"Original log size: {len(log)} cases")
    
    # Filter to keep only the first max_cases
    filtered_log = log[:max_cases]
    
    print(f"Filtered log size: {len(filtered_log)} cases")
    
    # Save filtered log
    pm4py.write_xes(filtered_log, output_path)
    print(f"Filtered log saved to {output_path}")

if __name__ == "__main__":
    input_path = "logs/logxesrotohive.xes"
    output_path = "logs/filtered_log.xes"
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    filter_log(input_path, output_path, max_cases=100)  # Start with just 100 cases
