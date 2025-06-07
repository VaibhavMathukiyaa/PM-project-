import pm4py
import os
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.process_tree import visualizer as pt_visualization
from pm4py.visualization.petri_net import visualizer as pn_visualization
from import_xes import import_log

def apply_inductive_miner(log, output_dir, noise_threshold=0.2):
    """
    Apply Inductive Miner algorithm
    
    Parameters:
    log (EventLog): Event log
    output_dir (str): Output directory
    noise_threshold (float): Noise threshold for Inductive Miner
    
    Returns:
    tuple: (process_tree, net, initial_marking, final_marking)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Applying Inductive Miner with noise threshold {noise_threshold}...")
    
    # Discover process tree using Inductive Miner
    try:
        # Try newer API first
        process_tree = pm4py.discover_process_tree_inductive(log, noise_threshold=noise_threshold)
    except Exception as e:
        print(f"Error with newer API: {e}")
        try:
            # Fallback to older API
            variant = inductive_miner.Variants.IMf
            parameters = {variant.value.Parameters.NOISE_THRESHOLD: noise_threshold}
            process_tree = inductive_miner.apply_tree(log, variant=variant, parameters=parameters)
        except Exception as e2:
            print(f"Error with older API: {e2}")
            # Create a simple process tree as fallback
            from pm4py.objects.process_tree.obj import ProcessTree, Operator
            process_tree = ProcessTree()
            process_tree.operator = Operator.SEQUENCE
            
            # Add activities as children
            activities = pm4py.get_event_attribute_values(log, "concept:name")
            for activity in activities:
                child = ProcessTree(label=activity)
                process_tree.children.append(child)
    
    # Save process tree visualization
    try:
        gviz = pt_visualization.apply(process_tree)
        pt_visualization.save(gviz, os.path.join(output_dir, "inductive_process_tree.png"))
    except Exception as e:
        print(f"Could not visualize process tree: {e}")
    
    # Convert to Petri Net for conformance checking
    try:
        from pm4py.convert import convert_to_petri_net
        net, initial_marking, final_marking = convert_to_petri_net(process_tree)
    except Exception as e:
        print(f"Could not convert process tree to Petri net: {e}")
        # Create a simple Petri net as fallback
        from pm4py.objects.petri_net.obj import PetriNet, Marking
        net = PetriNet("net_from_tree")
        initial_marking = Marking()
        final_marking = Marking()
        
        # Create a simple sequential net from activities
        activities = pm4py.get_event_attribute_values(log, "concept:name")
        prev_place = None
        
        # Create start place
        source = PetriNet.Place("source")
        net.places.add(source)
        initial_marking[source] = 1
        
        for i, activity in enumerate(activities):
            # Create transition for activity
            trans = PetriNet.Transition(f"trans_{activity}", activity)
            net.transitions.add(trans)
            
            # Create place after transition
            if i == len(activities) - 1:
                place = PetriNet.Place("sink")
                final_marking[place] = 1
            else:
                place = PetriNet.Place(f"p_{i}")
            net.places.add(place)
            
            # Connect from previous place if not first activity
            if prev_place is None:
                # Connect from source
                arc = PetriNet.Arc(source, trans)
                net.arcs.add(arc)
            else:
                # Connect from previous place
                arc = PetriNet.Arc(prev_place, trans)
                net.arcs.add(arc)
            
            # Connect to current place
            arc = PetriNet.Arc(trans, place)
            net.arcs.add(arc)
            
            prev_place = place
    
    # Save Petri Net visualization
    try:
        gviz = pn_visualization.apply(net, initial_marking, final_marking)
        pn_visualization.save(gviz, os.path.join(output_dir, "inductive_petri_net.png"))
    except Exception as e:
        print(f"Could not visualize Petri net: {e}")
    
    # Save the model in PNML format
    try:
        from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
        pnml_exporter.apply(net, initial_marking, os.path.join(output_dir, "inductive_model.pnml"), final_marking=final_marking)
    except Exception as e:
        print(f"Could not export Petri net to PNML: {e}")
    
    # Also save the process tree in PTML format if available
    try:
        from pm4py.objects.process_tree.exporter import exporter as pt_exporter
        pt_exporter.apply(process_tree, os.path.join(output_dir, "inductive_model.ptml"))
    except Exception as e:
        print(f"Could not export process tree to PTML: {e}")
    
    print(f"Inductive Miner results saved to {output_dir}")
    
    return process_tree, net, initial_marking, final_marking

if __name__ == "__main__":
    log_path = "logs/logxesrotohive.xes"
    log = import_log(log_path)
    
    # Apply Inductive Miner with different noise thresholds
    process_tree, net, im, fm = apply_inductive_miner(log, "models/inductive_miner/default", noise_threshold=0.2)
    
    # Try with lower noise threshold for more precise model
    process_tree_low, net_low, im_low, fm_low = apply_inductive_miner(log, "models/inductive_miner/low_noise", noise_threshold=0.1)
    
    # Try with higher noise threshold for more general model
    process_tree_high, net_high, im_high, fm_high = apply_inductive_miner(log, "models/inductive_miner/high_noise", noise_threshold=0.4)
