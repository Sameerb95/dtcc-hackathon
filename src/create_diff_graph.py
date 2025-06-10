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


# import fitz 
# from difflib import SequenceMatcher, Differ # Using difflib
# from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
# import os
# import re

# # # Assuming VertexAILangchainLLM is in a place accessible by this script
# # try:
# #     import VertexAILangchainLLM # Adjust if your LLM class is elsewhere
# # except ImportError:
# #     print("Warning: Could not import VertexAILangchainLLM. LLM calls will fail." )
# #     VertexAILangchainLLM = None

# def extract_text_from_pdf_pages(pdf_path):
#     """Extracts text from each page of a PDF using PyMuPDF."""
#     pages_text = []
#     if not os.path.exists(pdf_path):
#         print(f"Error: PDF file not found at '{pdf_path}'")
#         return pages_text
#     try:
#         doc = fitz.open(pdf_path)
#         for i, page in enumerate(doc):
#             text = page.get_text("text")
#             pages_text.append(text.strip() if text else "")
#             # print(f"Extracted text from page {i+1} of {os.path.basename(pdf_path)}") # Keep if verbose logging needed
#         doc.close()
#     except Exception as e:
#         print(f"Error reading PDF {pdf_path}: {e}")
#     return pages_text

# def calculate_sequence_similarity_ratio(text1, text2):
#     """Calculates similarity ratio using difflib.SequenceMatcher."""
#     if not text1 and not text2:
#         return 1.0
#     if not text1 or not text2: # If one is empty and the other is not
#         return 0.0
#     return SequenceMatcher(None, text1, text2).ratio()

# def get_detailed_contextual_diff_enhanced(text_v1, text_v2, num_context_lines=4):
#     """
#     Provides contextual diff using difflib, focusing on changed blocks.
#     """
#     lines_v1 = text_v1.splitlines()
#     lines_v2 = text_v2.splitlines()
    
#     # Use unified_diff for a standard diff format
#     # diff_iter = difflib.unified_diff(lines_v1, lines_v2, lineterm='', n=num_context_lines, fromfile='V1', tofile='V2')
#     # diff_output = list(diff_iter)

#     # Or using Differ and manually constructing context for more control if needed:
#     d = Differ()
#     diff_result = list(d.compare(lines_v1, lines_v2))
    
#     output_lines = []
#     has_changes = False
    
#     for i, line in enumerate(diff_result):
#         if line.startswith('+ ') or line.startswith('- '):
#             has_changes = True
#             # Add context before the change block
#             if not output_lines or output_lines[-1] == "---": # Start of a new diff block
#                  if output_lines and output_lines[-1] == "---": output_lines.pop() # Remove previous separator if consecutive
#                  for j in range(max(0, i - num_context_lines), i):
#                     if j < len(diff_result) and diff_result[j].startswith('  '): # Unchanged context line
#                         output_lines.append(diff_result[j])
#             output_lines.append(line)
#         elif line.startswith('  ') and has_changes and (not output_lines or not output_lines[-1].startswith('  ')):
#             # Add context after a change block, but only if it's not already context
#             # Limit trailing context lines
#             trailing_context_count = 0
#             temp_trailing_context = []
#             for k in range(i, min(len(diff_result), i + num_context_lines)):
#                 if diff_result[k].startswith('  '):
#                     temp_trailing_context.append(diff_result[k])
#                     trailing_context_count +=1
#                 else: # Hit another change or end
#                     break
#             output_lines.extend(temp_trailing_context)
#             if temp_trailing_context and i + trailing_context_count < len(diff_result) : # Add separator if more content follows
#                  output_lines.append("---")
#             has_changes = False # Reset for next block
#         elif line.startswith('? '): # Hint lines from Differ
#             # output_lines.append(line) # Optionally include these
#             pass


#     if not output_lines:
#         return "No significant textual differences found by difflib."

#     # Clean up consecutive separators
#     final_output = []
#     if output_lines:
#         final_output.append(output_lines[0])
#         for i in range(1, len(output_lines)):
#             if output_lines[i] == "---" and final_output[-1] == "---":
#                 continue
#             final_output.append(output_lines[i])
#         if final_output and final_output[-1] == "---": # Remove trailing separator
#             final_output.pop()

#     return "\n".join(final_output) if final_output else "No significant textual differences found by difflib."


def analyze_document_similarity_and_send_to_llm(pdf_path_v1, pdf_path_v2, context_lines=2):
    """
    Compares two PDF documents page by page using difflib.SequenceMatcher,
    extracts context around differences, prints similarity, and sends an analysis to an LLM.
    """
    print(f"Starting analysis between '{os.path.basename(pdf_path_v1)}' and '{os.path.basename(pdf_path_v2)}'...")

    text_v1_pages = extract_text_from_pdf_pages(pdf_path_v1)
    text_v2_pages = extract_text_from_pdf_pages(pdf_path_v2)

    if not text_v1_pages or not text_v2_pages:
        print("Could not extract text from one or both documents. Aborting analysis.")
        return

    min_pages = min(len(text_v1_pages), len(text_v2_pages))
    page_analysis_for_llm = []

    print("\n--- Page-by-Page Similarity (SequenceMatcher Ratio) & Contextual Diff ---")
    for i in range(min_pages):
        page_text_v1 = text_v1_pages[i]
        page_text_v2 = text_v2_pages[i]
        
        similarity_ratio = calculate_sequence_similarity_ratio(page_text_v1, page_text_v2)
        
        # print(f"Page {i+1}: Similarity Ratio = {similarity_ratio:.4f}")
        
        context_diff_str = ""
        # Use a threshold slightly less than 1.0 for difflib, as even minor whitespace can change it.
        if similarity_ratio < 0.999: 
            context_diff_str = get_detailed_contextual_diff_enhanced(page_text_v1, page_text_v2, num_context_lines=context_lines)
            if context_diff_str != "No significant textual differences found by difflib.":
                pass
                #  print(f"Contextual Diff for Page {i+1}:\n{context_diff_str}\n")
            else:
                pass
                # print(f"Contextual Diff for Page {i+1}: No significant line-level differences found by difflib, though ratio is < 0.999 (possibly minor whitespace/formatting).\n")
        
        page_analysis_for_llm.append(
            f"Page {i+1}:\n"
            f"- Similarity Ratio: {similarity_ratio:.4f}\n"
            f"- V1 Char Count: {len(page_text_v1)}\n"
            f"- V2 Char Count: {len(page_text_v2)}\n"
            + (f"- Contextual Diff Snippet:\n```diff\n{context_diff_str}\n```\n" if context_diff_str and context_diff_str != "No significant textual differences found by difflib." else "- Context: Pages are highly similar or differences are minor.\n")
        )

    # Handle documents with different number of pages
    if len(text_v1_pages) > min_pages:
        extra_pages_info_v1 = f"Version 1 has {len(text_v1_pages) - min_pages} additional page(s) not present in Version 2 (starting from V1 Page {min_pages + 1})."
        page_analysis_for_llm.append(extra_pages_info_v1)
        print(f"\nNote: {extra_pages_info_v1}")
        for i in range(min_pages, len(text_v1_pages)):
             page_analysis_for_llm.append(f"V1 Additional Page {i+1} Content Snippet:\n```\n{text_v1_pages[i][:200]}...\n```\n")
    if len(text_v2_pages) > min_pages:
        extra_pages_info_v2 = f"Version 2 has {len(text_v2_pages) - min_pages} additional page(s) not present in Version 1 (starting from V2 Page {min_pages + 1})."
        page_analysis_for_llm.append(extra_pages_info_v2)
        print(f"\nNote: {extra_pages_info_v2}")
        for i in range(min_pages, len(text_v2_pages)):
             page_analysis_for_llm.append(f"V2 Additional Page {i+1} Content Snippet:\n```\n{text_v2_pages[i][:200]}...\n```\n")


    llm_input_summary = "\n".join(page_analysis_for_llm)

    # print(llm_input_summary)
    
    if not VertexAILangchainLLM:
        print("\nLLM analysis skipped as VertexAILangchainLLM is not available.")
        return

    print("\n--- Sending Similarity Analysis to LLM ---")
    llm = VertexAILangchainLLM({}) 
    
    prompt_template_str = get_difference_prompt()
    human_template = HumanMessagePromptTemplate.from_template(prompt_template_str)
    chat_prompt = ChatPromptTemplate.from_messages([human_template])

    try:
        prompt_messages = chat_prompt.format_prompt(page_analysis_summary=llm_input_summary.strip()).to_messages()
        request_content_str = "".join([msg.content for msg in prompt_messages])
        
        # print(f"\nFull Formatted Prompt for LLM:\n{request_content_str}\n--------------------") # For debugging the full prompt
        # print(f"\nFormatted Prompt for LLM (first 1000 chars):\n{request_content_str[:1000]}...")


        llm_response = llm._call(prompt=request_content_str)

        print("\n--- LLM Analysis Response ---")
        print(llm_response)
    except Exception as e:
        print(f"Error during LLM interaction: {e}")


# if __name__ == "__main__":
#     pdf_v1_path = "AWPR Version 1.pdf" 
#     pdf_v2_path = "AWPR Version 2.pdf" 

#     if os.path.exists(pdf_v1_path) and os.path.exists(pdf_v2_path):
#         analyze_document_similarity_and_send_to_llm(pdf_v1_path, pdf_v2_path, context_lines=10)
#     else:
#         print(f"Error: Ensure PDF files exist at the specified paths.")
#         print(f"Checked for: '{os.path.abspath(pdf_v1_path)}' and '{os.path.abspath(pdf_v2_path)}'")