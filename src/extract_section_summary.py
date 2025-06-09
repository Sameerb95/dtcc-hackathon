import PyPDF2
import re
import json 
from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from llm_call import VertexAILangchainLLM
from summary_prompt import get_prompt


MAX_SECTIONS_TO_PROCESS_AND_SEND = 999999999

def _parse_toc_line_for_hierarchy(full_name_from_toc):
    stripped_name = full_name_from_toc.strip()
    m_numeric = re.match(r"^(\d+(?:\.\d+)*)\s+(.*)", stripped_name)
    if m_numeric:
        id_str = m_numeric.group(1)
        title = m_numeric.group(2).strip()
        level = len(id_str.split('.'))
        return level, id_str, title
    
    parts = stripped_name.split(None, 1)
    if not parts: return 1, "UnknownSection", "Unknown Title"
    id_str = parts[0].rstrip(':')
    title = parts[1].strip() if len(parts) > 1 else id_str
    if len(id_str) > 25 and id_str == title:
        short_id_candidate = "_".join(title.split()[:2]).lower()
        id_str = "".join(filter(str.isalnum, short_id_candidate))[:15]
        if not id_str : id_str = "section"
    return 1, id_str, title

def build_hierarchical_toc(flat_toc_entries_with_pages):
    structured_toc_root = []
    parent_stack = [(0, structured_toc_root)]
    for full_name, start_p, end_p in flat_toc_entries_with_pages:
        level, id_val, title_val = _parse_toc_line_for_hierarchy(full_name)
        entry = {
            'id': id_val,
            'title': title_val,
            'start_page': start_p,
            'end_page': end_p,
            'subsections': []
        }
        while parent_stack[-1][0] >= level:
            parent_stack.pop()
        _parent_level, parent_children_list = parent_stack[-1]
        parent_children_list.append(entry)
        parent_stack.append((level, entry['subsections']))
    return structured_toc_root

def extract_flat_toc_with_pages(toc_text, total_pdf_pages):
    sections_with_start_pages = []
    lines = toc_text.split('\n')
    pattern = re.compile(r"^(.*?)\s*\.{2,}\s*(\d+)\s*$")
    for line in lines:
        line = line.strip()
        match = pattern.match(line)
        if match:
            section_name = match.group(1).strip()
            section_name = re.sub(r'\s*\.+\s*$', '', section_name).strip()
            if not section_name or len(section_name) < 2: continue
            try:
                page_number = int(match.group(2))
                sections_with_start_pages.append({"full_name": section_name, "start_page": page_number})
            except ValueError:
                print(f"Warning: Could not parse page number for line: '{line}'")
                continue
    sections_with_start_pages.sort(key=lambda x: x["start_page"])
    processed_sections_flat = []
    num_extracted = len(sections_with_start_pages)
    for i in range(num_extracted):
        current_section = sections_with_start_pages[i]
        full_name = current_section["full_name"]
        start_page = current_section["start_page"]
        end_page = total_pdf_pages
        if i + 1 < num_extracted:
            next_section_start_page = sections_with_start_pages[i+1]["start_page"]
            end_page = next_section_start_page - 1 if next_section_start_page > start_page else start_page
        if end_page < start_page: end_page = start_page
        processed_sections_flat.append((full_name, start_page, end_page))
    return processed_sections_flat

def get_hierarchical_toc_from_pdf(pdf_path, toc_actual_start_page, toc_actual_end_page):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pdf_pages = len(reader.pages)
            if not (0 < toc_actual_start_page <= toc_actual_end_page <= total_pdf_pages):
                print("Error: Invalid ToC page range provided.")
                return None, 0 

            toc_text = ""
            for page_num_0_indexed in range(toc_actual_start_page - 1, toc_actual_end_page):
                if page_num_0_indexed < total_pdf_pages:
                    page = reader.pages[page_num_0_indexed]
                    toc_text += page.extract_text() + "\n"
                else:
                    print(f"Warning: Page number {page_num_0_indexed + 1} is out of bounds for ToC.")
                    break
        
        if not toc_text.strip():
            print("Warning: No text extracted from ToC pages.")
            return None, total_pdf_pages
            
        flat_toc_entries = extract_flat_toc_with_pages(toc_text, total_pdf_pages)
        if not flat_toc_entries:
            print("Warning: Could not parse any flat ToC entries.")
            return None, total_pdf_pages
            
        hierarchical_toc = build_hierarchical_toc(flat_toc_entries)
        return hierarchical_toc, total_pdf_pages

    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found.")
        return None, 0
    except PyPDF2.errors.PdfReadError as e:
        print(f"Error: Could not read the PDF file '{pdf_path}'. It might be corrupted or not a valid PDF: {e}")
        return None, 0
    except Exception as e:
        print(f"An unexpected error occurred during ToC extraction: {e}")
        return None, 0

def extract_text_from_page_range(pdf_reader, start_page_1_indexed, end_page_1_indexed):
    text_content = ""
    try:
        num_doc_pages = len(pdf_reader.pages)
        start_idx = max(0, start_page_1_indexed - 1)
        end_idx = min(num_doc_pages -1 , end_page_1_indexed - 1)

        if start_idx > end_idx : 
            print(f"Warning: Invalid page range for text extraction. Start: {start_page_1_indexed}, End: {end_page_1_indexed}")
            return ""

        for page_num in range(start_idx, end_idx + 1):
            if page_num < num_doc_pages:
                page = pdf_reader.pages[page_num]
                extracted = page.extract_text()
                if extracted:
                    text_content += extracted + "\n" 
            else:
                print(f"Warning: Page number {page_num + 1} is out of bounds during text extraction.")
                break 
        return text_content.strip()
    except Exception as e:
        print(f"Error extracting text from pages {start_page_1_indexed}-{end_page_1_indexed}: {e}")
        return ""


def send_data_to_vertex_ai(section_payload, document_name):
    print(f"Document: {document_name}")
    print(f"Section ID: {section_payload.get('id')}")
    print(f"Title: {section_payload.get('title')}")
    print(f"Start Page: {section_payload.get('start_page')}")
    print(f"End Page: {section_payload.get('end_page')}")
    # print(f"Extracted Text:\n{section_payload.get('text_content')[:500]}...") # Print start of text

    if len(section_payload.get('text_content', '')) > 500:
        print(f"Extracted Text (first 500 chars):\n{section_payload.get('text_content')[:500]}...")
    else:
        print(f"Extracted Text:\n{section_payload.get('text_content')}")
    print("----------------------------------------")

    
    if len(section_payload.get('text_content', '')) > 10:
        print(f"--- Sending to Vertex AI (Placeholder) ---")
        messages = []

        template = get_prompt()
        human_template = HumanMessagePromptTemplate.from_template(template)
        messages.append(human_template)
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        section_name = section_payload.get('title')
        request = chat_prompt.format_prompt(section_name=section_name,
                                            text_contents=section_payload.get('text_content'),
                                            ).to_messages()
        
        request_dicts = [{"role": msg.type, "content": msg.content} for msg in request]

        print(f"request_dicts: {request_dicts}")

        with open(f"summary/{section_name}.txt",'w') as f:
            llm = VertexAILangchainLLM({})
            try:
                response = llm._call(prompt=str(request_dicts))
                f.write(response)
                return response

            except Exception as e:
                print("Some error occered"+e)
    return True
 

def process_and_send_sections_to_vertex_ai(pdf_reader_obj, sections_list, document_identifier,sent_sections_count_tracker):
    for section in sections_list:
        print(f"Count: {sent_sections_count_tracker}")
        if sent_sections_count_tracker[0] >= MAX_SECTIONS_TO_PROCESS_AND_SEND:
            print(f"INFO: Reached maximum section processing limit ({MAX_SECTIONS_TO_PROCESS_AND_SEND}). Stopping.")
            return
        section_text = extract_text_from_page_range(
            pdf_reader_obj,
            section['start_page'],
            section['end_page']
        )

        payload = {
            'id': section['id'],
            'title': section['title'],
            'start_page': section['start_page'],
            'end_page': section['end_page'],
            'text_content': section_text, 
           
        }
        success = send_data_to_vertex_ai(payload, document_identifier)
        if success:
            sent_sections_count_tracker[0] += 1 
            print(f"INFO: Sections sent so far: {sent_sections_count_tracker[0]}/{MAX_SECTIONS_TO_PROCESS_AND_SEND}")
        else:
            print(f"Warning: Failed to send data for section '{section['title']}' (ID: {section['id']})")

        if section.get('subsections'):
            if sent_sections_count_tracker[0] < MAX_SECTIONS_TO_PROCESS_AND_SEND:
                process_and_send_sections_to_vertex_ai(
                    pdf_reader_obj,
                    section['subsections'],
                    document_identifier,
                    sent_sections_count_tracker # Pass the same tracker
                )
            else:
                # If limit was reached by processing the parent, no need to go into children
                return
            


if __name__ == "__main__":
    pdf_file = "esma_report.pdf"  
    document_id_for_vertex = pdf_file

    actual_toc_start_page = 1  
    actual_toc_end_page = 4 



    print(f"Attempting to extract Hierarchical ToC from PDF: {pdf_file}")

    hierarchical_toc_data, _ = get_hierarchical_toc_from_pdf(
        pdf_file,
        actual_toc_start_page,
        actual_toc_end_page
    )

    if hierarchical_toc_data:
        print("\nSuccessfully extracted Hierarchical ToC Data.")
        # print(json.dumps(hierarchical_toc_data, indent=2)) # Optional: view ToC

        with open(pdf_file, 'rb') as file_for_text_extraction:
            pdf_reader = PyPDF2.PdfReader(file_for_text_extraction)

            sections_sent_tracker = [0]

            print(f"\n--- Processing sections, extracting text, and sending to Vertex AI for document: {document_id_for_vertex} ---")
            process_and_send_sections_to_vertex_ai(
                pdf_reader, 
                hierarchical_toc_data,
                document_id_for_vertex,
                sections_sent_tracker 
            )
            print("\n--- Finished processing all sections ---")