import networkx as nx
import json
import os
import plotly.express as px
from typing import List, Tuple # Added Tuple

def create_graph_from_diff(diff_json_string):
    try:
        diff_data = json.loads(diff_json_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Problematic JSON string: {diff_json_string[:500]}...")
        return None
        
    graph = nx.DiGraph()

    def add_node_with_attributes(node_label, attributes, change_status):
        if not graph.has_node(node_label):
            graph.add_node(node_label, label=node_label, **attributes, change_status=change_status)
        else:
            # If node exists, update attributes but be careful about overwriting 'change_status'
            # if a more significant status (like 'added' or 'modified') was already set.
            existing_status = graph.nodes[node_label].get('change_status')
            graph.nodes[node_label].update(attributes)
            if change_status == 'added' or \
               (change_status == 'modified' and existing_status != 'added') or \
               (existing_status not in ['added', 'modified']): # only update if new status is more specific or old was less
                graph.nodes[node_label]['change_status'] = change_status
            if 'label' not in graph.nodes[node_label]: # Ensure label is set
                 graph.nodes[node_label]['label'] = node_label

    if 'nodes_diff' in diff_data:
        nodes_diff = diff_data['nodes_diff']
        for node_data in nodes_diff.get('added_in_v2', []):
            attributes = {'description': node_data.get('description')}
            add_node_with_attributes(node_data['label'], attributes, 'added')

        for node_data in nodes_diff.get('modified', []):
            attributes = {'description': node_data.get('v2_description')}
            add_node_with_attributes(node_data['label'], attributes, 'modified')
            graph.nodes[node_data['label']]['v1_description'] = node_data.get('v1_description')

    if 'edges_diff' in diff_data:
        edges_diff = diff_data['edges_diff']
        for edge_data in edges_diff.get('added_in_v2', []):
            source = edge_data['source_label']
            target = edge_data['target_label']
            
            if not graph.has_node(source):
                add_node_with_attributes(source, {}, 'implicit_from_edge') 
            if not graph.has_node(target):
                add_node_with_attributes(target, {}, 'implicit_from_edge') 

            graph.add_edge(
                source,
                target,
                label=edge_data['relationship_label'],
                details=edge_data.get('details'),
                change_status='added'
            )

        for edge_data in edges_diff.get('modified', []):
            source = edge_data['source_label']
            target = edge_data['target_label']

            if not graph.has_node(source):
                add_node_with_attributes(source, {}, 'implicit_from_edge')
            if not graph.has_node(target):
                add_node_with_attributes(target, {}, 'implicit_from_edge')
            
            graph.add_edge(
                source,
                target,
                label=edge_data['v2_relationship_label'], 
                details=edge_data.get('v2_details'),
                change_status='modified',
                v1_relationship_label=edge_data.get('v1_relationship_label'),
                v1_details=edge_data.get('v1_details')
            )
    return graph

def process_all_diff_jsons(folder_path: str) -> List[Tuple[str, nx.DiGraph]]:
    """
    Processes all JSON files in a folder, creates a graph for each,
    and returns a list of (filename, graph) tuples.
    """
    all_graphs_with_names: List[Tuple[str, nx.DiGraph]] = []
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found at {folder_path}")
        return all_graphs_with_names

    for filename in sorted(os.listdir(folder_path)): # Sort for consistent order
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            print(f"\nProcessing file: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_string = f.read()
                    if not json_string.strip() or json_string.strip() == "{}":
                        print(f"  Skipping empty or placeholder JSON file: {filename}")
                        # Still add an empty graph placeholder so chunk selection isn't thrown off
                        all_graphs_with_names.append((filename, nx.DiGraph())) 
                        continue
                    graph = create_graph_from_diff(json_string)
                    if graph:
                        all_graphs_with_names.append((filename, graph))
                        print(f"  Successfully created graph from {filename}. Nodes: {graph.number_of_nodes()}, Edges: {graph.number_of_edges()}")
                    else:
                        all_graphs_with_names.append((filename, nx.DiGraph())) # Add empty for failed creation
                        print(f"  Failed to create graph from {filename} (likely due to JSON error or empty diff).")
            except Exception as e:
                all_graphs_with_names.append((filename, nx.DiGraph())) # Add empty for file processing error
                print(f"  Error processing file {filename}: {e}")
    return all_graphs_with_names

def merge_individual_graphs(list_of_graphs: List[nx.DiGraph]) -> nx.DiGraph:
    """Merges a list of NetworkX DiGraphs into a single DiGraph."""
    merged_graph = nx.DiGraph()
    if not list_of_graphs:
        return merged_graph

    for graph_to_merge in list_of_graphs:
        if not graph_to_merge: continue # Skip if a graph object is None

        for node, data in graph_to_merge.nodes(data=True):
            if not merged_graph.has_node(node):
                merged_graph.add_node(node, **data)
            else:
                # Prioritize more significant change_status
                current_status = merged_graph.nodes[node].get('change_status')
                new_status = data.get('change_status')
                
                should_update_attributes = True # Default to update attributes
                
                if new_status == 'added':
                    merged_graph.nodes[node].update(data) # 'added' takes precedence
                elif new_status == 'modified':
                    if current_status != 'added':
                        merged_graph.nodes[node].update(data)
                    else: # current is 'added', new is 'modified' - keep 'added' status but update other data
                        original_status = merged_graph.nodes[node]['change_status']
                        merged_graph.nodes[node].update(data)
                        merged_graph.nodes[node]['change_status'] = original_status
                elif current_status not in ['added', 'modified']: # new is 'implicit' or 'unknown'
                    merged_graph.nodes[node].update(data) # Update if current is also less significant
                
                # Ensure label is present
                if 'label' in data and 'label' not in merged_graph.nodes[node]:
                     merged_graph.nodes[node]['label'] = data['label']


        for u, v, data in graph_to_merge.edges(data=True):
            if not merged_graph.has_edge(u,v): 
                merged_graph.add_edge(u,v,**data)
            else: 
                # Similar logic for edges: prioritize more significant change_status
                current_edge_data = merged_graph.get_edge_data(u,v)
                new_status = data.get('change_status')
                current_status = current_edge_data.get('change_status')

                if new_status == 'added':
                    current_edge_data.update(data)
                elif new_status == 'modified':
                    if current_status != 'added':
                        current_edge_data.update(data)
                    else: # current is 'added', new is 'modified' - keep 'added' status but update other data
                        original_status = current_edge_data['change_status']
                        current_edge_data.update(data)
                        current_edge_data['change_status'] = original_status
                elif current_status not in ['added', 'modified']:
                     current_edge_data.update(data)
    return merged_graph


def filter_isolated_nodes(graph: nx.DiGraph) -> nx.DiGraph: # Added type hint for return
    """Removes isolated nodes from the graph."""
    if not isinstance(graph, nx.DiGraph): # Check if it's a graph
        print("  filter_isolated_nodes: Input is not a graph. Skipping.")
        return graph if graph is not None else nx.DiGraph()

    isolated = [node for node, degree in graph.degree() if degree == 0]
    graph.remove_nodes_from(isolated)
    print(f"  Removed {len(isolated)} isolated nodes.")
    return graph

def graph_to_json(graph):
    output_json = {
        "nodes": [],
        "edges": []
    }
    for node, data in graph.nodes(data=True):
        node_data = {"id": node, **data} 
        output_json["nodes"].append(node_data)

    for source, target, data in graph.edges(data=True):
        edge_data = {
            "source": source,
            "target": target,
            "relationship": data.get("label", "RELATED_TO"), 
            **data  
        }
        output_json["edges"].append(edge_data)
    return output_json


if __name__ == "__main__":
    DIFF_JSON_FOLDER = "/Users/shirsama/dtcc-hackathon/dtcc-ai-hackathon-2025/graph_diff_json" # Example path
    OUTPUT_JSON_PATH = "merged_graph_output.json"

    # process_all_diff_jsons now returns list of (filename, graph) tuples
    list_of_graphs_with_names = process_all_diff_jsons(DIFF_JSON_FOLDER)

    print(f"\n--- Summary ---")
    print(f"Total graph objects (from files) created: {len(list_of_graphs_with_names)}")

    # Extract just the graph objects for merging
    actual_graphs_to_merge = [graph for _, graph in list_of_graphs_with_names if graph is not None and graph.nodes()]
    
    if actual_graphs_to_merge:
        print(f"\nMerging {len(actual_graphs_to_merge)} non-empty graphs...")
        # Use the new merge function
        merged_graph = merge_individual_graphs(actual_graphs_to_merge)

        print(f"  Total nodes in merged graph before filtering: {merged_graph.number_of_nodes()}")
        print(f"  Total edges in merged graph before filtering: {merged_graph.number_of_edges()}")

        merged_graph = filter_isolated_nodes(merged_graph)

        print(f"  Total nodes in merged graph after filtering: {merged_graph.number_of_nodes()}")
        print(f"  Total edges in merged graph after filtering: {merged_graph.number_of_edges()}")

        final_graph_json = graph_to_json(merged_graph)

        try:
            with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(final_graph_json, f, indent=2, ensure_ascii=False)
            print(f"\nSuccessfully saved merged graph to JSON: {OUTPUT_JSON_PATH}")
        except IOError as e:
            print(f"Error saving JSON file: {e}")
    else:
        print("No non-empty graphs were created to merge or save.")
