import pm4py
import os
from pm4py.visualization.dfg import visualizer as dfg_visualization
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from import_xes import import_log

def apply_dfg_miner(log, output_dir):
    """
    Apply Directly-Follows Graph mining algorithm
    
    Parameters:
    log (EventLog): Event log
    output_dir (str): Output directory
    
    Returns:
    dfg (dict): Directly-Follows Graph
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("Applying DFG Miner...")
    
    # Create Directly-Follows Graph
    dfg = pm4py.discover_directly_follows_graph(log)
    
    # Visualize DFG using the visualization module
    try:
        # Try the newer API first
        gviz = dfg_visualization.apply(dfg, log=log)
        dfg_visualization.save(gviz, os.path.join(output_dir, "dfg_model.png"))
    except Exception as e:
        print(f"Error with dfg visualization: {e}")
        try:
            # Fallback to older API
            parameters = {dfg_visualization.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
            gviz = dfg_visualization.apply(dfg, log=log, variant=dfg_visualization.Variants.FREQUENCY, parameters=parameters)
            dfg_visualization.save(gviz, os.path.join(output_dir, "dfg_model.png"))
        except Exception as e2:
            print(f"Could not visualize DFG: {e2}")
    
    # Convert DFG to Petri Net for conformance checking
    try:
        # Try using alpha miner instead if direct conversion is not available
        net, initial_marking, final_marking = alpha_miner.apply(log)
    except Exception as e:
        print(f"Could not convert DFG to Petri net using alpha miner: {e}")
        # Fallback to a simple net
        from pm4py.objects.petri_net.obj import PetriNet, Marking
        net = PetriNet("net_from_dfg")
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
        from pm4py.visualization.petri_net import visualizer as pn_visualizer
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        pn_visualizer.save(gviz, os.path.join(output_dir, "dfg_petri_net.png"))
    except Exception as e:
        print(f"Could not visualize Petri net: {e}")
    
    # Save the model in PNML format
    try:
        from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
        pnml_exporter.apply(net, initial_marking, os.path.join(output_dir, "dfg_model.pnml"), final_marking=final_marking)
    except Exception as e:
        print(f"Could not export Petri net to PNML: {e}")
    
    print(f"DFG mining results saved to {output_dir}")
    
    return dfg, net, initial_marking, final_marking

if __name__ == "__main__":
    log_path = "logs/logxesrotohive.xes"
    log = import_log(log_path)
    dfg, net, initial_marking, final_marking = apply_dfg_miner(log, "models/dfg_miner")
