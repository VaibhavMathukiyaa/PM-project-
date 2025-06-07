import pm4py
import os
import matplotlib.pyplot as plt

def import_log(log_path):
    """
    Import XES log file
    
    Parameters:
    log_path (str): Path to the XES log file
    
    Returns:
    log (EventLog): Imported event log
    """
    print(f"Importing log from {log_path}...")
    log = pm4py.read_xes(log_path)
    print("Log imported successfully.")
    return log

def save_log_summary(log, output_dir):
    """
    Save log summary to a text file
    
    Parameters:
    log (EventLog): Event log
    output_dir (str): Output directory
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, "log_summary.txt")
    
    with open(output_path, 'w') as f:
        f.write("Log Summary\n")
        f.write("===========\n\n")
        
        # Basic statistics
        f.write(f"Number of traces: {len(log)}\n")
        f.write(f"Number of events: {sum(len(trace) for trace in log)}\n")
        
        # Activities
        activities = pm4py.get_event_attribute_values(log, "concept:name")
        f.write(f"Number of unique activities: {len(activities)}\n")
        f.write("Activities:\n")
        for activity, count in activities.items():
            f.write(f"  - {activity}: {count}\n")
        
        # Variants
        try:
            variants = pm4py.get_variants(log)
            f.write(f"\nNumber of variants: {len(variants)}\n")
            
            # Check the structure of variants to handle it correctly
            if isinstance(variants, dict):
                # Handle dictionary format
                try:
                    # Try sorting by value length if values are lists/traces
                    sorted_variants = sorted(variants.items(), key=lambda x: len(x[1]) if hasattr(x[1], "__len__") else x[1], reverse=True)[:5]
                    f.write("Top 5 variants:\n")
                    for i, (variant, traces) in enumerate(sorted_variants):
                        f.write(f"  Variant {i+1}")
                        if hasattr(traces, "__len__"):
                            f.write(f" (occurs {len(traces)} times):\n")
                            if traces and hasattr(traces[0], "__getitem__") and "concept:name" in traces[0][0]:
                                activities = [event["concept:name"] for event in traces[0]]
                                f.write(f"    {' -> '.join(activities)}\n")
                            else:
                                f.write(f"    {variant}\n")
                        else:
                            f.write(f" (occurs {traces} times):\n")
                            f.write(f"    {variant}\n")
                except Exception as e:
                    f.write(f"Error processing variants: {str(e)}\n")
                    # Alternative approach: just list the variants
                    f.write("Variants (format could not be processed in detail):\n")
                    for i, (variant, count) in enumerate(list(variants.items())[:5]):
                        f.write(f"  Variant {i+1}: {variant} (count: {count})\n")
            else:
                # Handle other formats
                f.write("Variants (format could not be processed in detail):\n")
                f.write(f"  Variants data type: {type(variants)}\n")
        except Exception as e:
            f.write(f"\nError analyzing variants: {str(e)}\n")
    
    print(f"Log summary saved to {output_path}")

if __name__ == "__main__":
    log_path = "logs/logxesrotohive.xes"  # Updated log path
    log = import_log(log_path)
    save_log_summary(log, "models/log_analysis")
