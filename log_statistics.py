import pm4py
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from import_xes import import_log

def analyze_log(log, output_dir):
    """
    Analyze log and generate statistics and visualizations
    
    Parameters:
    log (EventLog): Event log
    output_dir (str): Output directory
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 1. Case duration analysis
    try:
        # Updated to handle different API
        case_durations = []
        for case in log:
            if len(case) >= 2:
                start_time = case[0]["time:timestamp"]
                end_time = case[-1]["time:timestamp"]
                duration = (end_time - start_time).total_seconds() / (24*3600)  # Convert to days
                case_durations.append(duration)
        
        if case_durations:
            plt.figure(figsize=(10, 6))
            plt.hist(case_durations, bins=30, alpha=0.7, color='blue')
            plt.title('Case Duration Distribution')
            plt.xlabel('Duration (days)')
            plt.ylabel('Number of Cases')
            plt.grid(True, alpha=0.3)
            plt.savefig(os.path.join(output_dir, 'case_duration_distribution.png'))
            plt.close()
            
            with open(os.path.join(output_dir, 'case_duration_stats.txt'), 'w') as f:
                f.write(f"Average case duration: {np.mean(case_durations):.2f} days\n")
                f.write(f"Median case duration: {np.median(case_durations):.2f} days\n")
                f.write(f"Min case duration: {np.min(case_durations):.2f} days\n")
                f.write(f"Max case duration: {np.max(case_durations):.2f} days\n")
    except Exception as e:
        print(f"Could not analyze case durations: {e}")
    
    # 2. Activity frequency
    activities = pm4py.get_event_attribute_values(log, "concept:name")
    sorted_activities = sorted(activities.items(), key=lambda x: x[1], reverse=True)
    
    plt.figure(figsize=(12, 8))
    activities_names = [a[0] for a in sorted_activities[:10]]
    activities_count = [a[1] for a in sorted_activities[:10]]
    
    plt.bar(activities_names, activities_count, color='skyblue')
    plt.title('Top 10 Activities by Frequency')
    plt.xlabel('Activity')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'activity_frequency.png'))
    plt.close()
    
    # 3. Events over time
    try:
        events_over_time = {}
        for trace in log:
            for event in trace:
                if "time:timestamp" in event:
                    timestamp = event["time:timestamp"]
                    date = timestamp.date()
                    if date in events_over_time:
                        events_over_time[date] += 1
                    else:
                        events_over_time[date] = 1
        
        dates = sorted(events_over_time.keys())
        counts = [events_over_time[date] for date in dates]
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, counts, marker='o', linestyle='-', color='green')
        plt.title('Events Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Events')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'events_over_time.png'))
        plt.close()
    except Exception as e:
        print(f"Could not analyze events over time: {e}")
    
    print(f"Log statistics and visualizations saved to {output_dir}")

if __name__ == "__main__":
    log_path = "logs/logxesrotohive.xes"
    log = import_log(log_path)
    analyze_log(log, "models/log_analysis")
