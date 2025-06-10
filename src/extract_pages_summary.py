import os
import re
import fitz 
from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from llm_call import VertexAILangchainLLM
from get_summary_prompt import get_summary_prompt

# # def create_page_chunks(file_path):
# #     """
# #     Reads a file and splits its content into page-wise chunks.

# #     It assumes that each page starts with a specific multi-line header block
# #     that includes a line like "<number> | P a g e".

# #     Args:
# #         file_path (str): The path to the text file.

# #     Returns:
# #         list: A list of strings, where each string is the content of a page.
# #               Returns an empty list if the file cannot be read or no pages are found.
# #     """
# #     try:
# #         with open(file_path, 'r', encoding='utf-8') as f:
# #             text = f.read()
# #     except FileNotFoundError:
# #         print(f"Error: File not found at {file_path}")
# #         return []
# #     except Exception as e:
# #         print(f"Error reading file {file_path}: {e}")
# #         return []

# #     # Define the pattern for the repeating page header.
# #     # This pattern captures the entire header block including the "N | P a g e" line
# #     # and the newline character immediately following it.
# #     # It looks for:
# #     # Line 1: "Revised AWPR Guidelines"
# #     # Line 2: "Ref No.:..."
# #     # Line 3: "Money & Banking Division..."
# #     # Line 4: "Email:..."
# #     # Line 5: "<number> | P a g e  " (with a trailing newline)
# #     header_pattern = re.compile(
# #         r"(^Revised AWPR Guidelines\s*\n"
# #         r"Ref No\.:[^\n]*\n"
# #         r"Money & Banking Division[^\n]*\n"
# #         r"Email:[^\n]*\n"
# #         r"\d+ \| P a g e\s*\n)",  # Matches digits, " | P a g e", optional spaces, and a newline
# #         re.MULTILINE
# #     )

# #     # Split the text by the header pattern. The pattern itself is captured.
# #     # Resulting 'parts' list: [text_before_first_header, header1, content_after_header1, header2, content_after_header2, ...]
# #     parts = header_pattern.split(text)

# #     page_chunks = []

# #     # parts[0] contains text before the first recognized header.
# #     # For the provided document, this is typically " \n \n", which becomes empty after strip().
# #     # If it were substantial content, it might be considered a "zeroth" page or preamble.
# #     # Current logic assumes pages start with the defined header.
# #     # If parts[0].strip() is non-empty, you might want to handle it as a special first chunk.
# #     # For now, we'll focus on pages that start with the identified header.

# #     # Iterate through the 'parts' list to combine headers with their subsequent content.
# #     # Each page chunk will consist of a header (parts[i]) and its content (parts[i+1]).
# #     for i in range(1, len(parts), 2):
# #         header = parts[i]
# #         if (i + 1) < len(parts):
# #             content = parts[i+1]
# #             page_chunks.append(header + content)
# #         else:
# #             # This case handles a document ending with a header but no subsequent content.
# #             page_chunks.append(header)
            
# #     return page_chunks

# # def send_data_to_llm(chunk,number,filename):

# #         print(f"--- Sending to Vertex AI (Placeholder) ---")
# #         messages = []

# #         template = get_prompt()
# #         human_template = HumanMessagePromptTemplate.from_template(template)
# #         messages.append(human_template)
# #         chat_prompt = ChatPromptTemplate.from_messages(messages)
# #         request = chat_prompt.format_prompt(section_name=str(number),
# #                                             text_contents=chunk,
# #                                             ).to_messages()
        
# #         request_dicts = [{"role": msg.type, "content": msg.content} for msg in request]

# #         print(f"request_dicts: {request_dicts}")

# #         path = f"resources/{filename}/summary/{filename}"

# #         from pathlib import Path
# #         Path(path).mkdir(parents=True, exist_ok=True)

# #         with open(f"{path}/chunk_{number}.txt",'w') as f:


# #             llm = VertexAILangchainLLM({})
# #             try:
# #                 response = llm._call(prompt=str(request_dicts))
# #                 f.write(response)
# #                 return response

# #             except Exception as e:
# #                 print("Some error occered"+e)
   

# # def extract_embedded_text(pdf_path: str) -> str:
# #     """
# #     Extracts embedded text from a PDF file.
# #     This does NOT perform OCR and will only work if the PDF contains
# #     actual text, not just images of text.

# #     Args:
# #         pdf_path (str): Path to the PDF file.

# #     Returns:
# #         str: The extracted text, concatenated from all pages.
# #              Returns an error message if the file is not found or other issues occur.
# #     """
# #     if not os.path.exists(pdf_path):
# #         return f"Error: PDF file not found at '{pdf_path}'"

# #     try:
# #         doc = fitz.open(pdf_path)
# #     except Exception as e:
# #         return f"Error opening PDF file '{pdf_path}': {e}"
        
# #     full_text = []
# #     print(f"Attempting to extract embedded text from {len(doc)} pages in '{pdf_path}'...\n")

# #     for page_num in range(len(doc)):
# #         try:
# #             page = doc.load_page(page_num)
# #             # "text" is the default, extracts plain text.
# #             # Other options include "html", "xml", "dict", "json", "rawdict", "rawjson"
# #             text = page.get_text("text") 
# #             full_text.append(text)
# #             print(f"--- Page {page_num + 1} Processed ---")
# #             preview_text = (text[:200].strip() + "...") if len(text) > 200 else text.strip()
# #             if not preview_text:
# #                 preview_text = "[No text found on this page]"
# #             print(f"Preview: {preview_text}\n")
# #         except Exception as e:
# #             error_on_page = f"[Error processing page {page_num + 1}: {e}]"
# #             print(error_on_page)
# #             full_text.append(error_on_page)
            
# #     doc.close()
# #     return "\n".join(full_text)


# # if __name__ == '__main__':
# #     pass

# #     # pdf_document_path = "AWPR Version 2.pdf" 
# #     # output_txt_file = "AWPR Version 2_text.txt"

# #     # print("Starting text extraction (without OCR, using PyMuPDF's get_text())...")

# #     # extracted_text = extract_embedded_text(pdf_document_path)
    
# #     # if extracted_text.startswith("Error:"):
# #     #     print(extracted_text) # Error message already formatted
# #     # else:
# #     #     print("\n--- Text Extraction Complete ---")
# #     #     # Check if any meaningful text was extracted (ignoring whitespace and page processing errors)
# #     #     meaningful_text_found = any(line.strip() and not line.startswith("[Error processing page") for line in extracted_text.splitlines())

# #     #     if not meaningful_text_found:
# #     #         print(f"No significant embedded text was found in '{pdf_document_path}'.")
# #     #         print("The PDF might be image-based or scanned, which would require an OCR engine to extract text.")
# #     #         print("This script only extracts pre-existing text layers within the PDF.")
# #     #     else:
# #     #         try:
# #     #             with open(output_txt_file, "w", encoding="utf-8") as f:
# #     #                 f.write(extracted_text)
# #     #             print(f"Full extracted text saved to '{output_txt_file}'")
# #     #         except IOError as e:
# #     #             print(f"Error saving extracted text to file: {e}")
# #     #             print("\nFull Extracted Text (first 1000 characters):\n")
# #     #             print(extracted_text[:1000])

# #     # file_path = "/Users/shirsama/dtcc-hackathon/dtcc-ai-hackathon-2025/AWPR Version 2_text.txt"
    
# #     # file_name = os.path.basename(file_path).split('.')[0]

# #     # pages = create_page_chunks(file_path)

# #     # if pages:
# #     #     print(f"Successfully created {len(pages)} page chunks from '{file_path}'.\n")
# #     #     for i, page_content in enumerate(pages):
# #     #         print(f"--- Page Chunk {i+1} (approx. {len(page_content.splitlines())} lines) ---")
# #     #         # Print first few and last few lines of each chunk for brevity
# #     #         lines = page_content.splitlines()
# #     #         if len(lines) > 10:
# #     #             for line_num in range(5):
# #     #                 print(lines[line_num])
# #     #             print("...")
# #     #             for line_num in range(len(lines) - 5, len(lines)):
# #     #                 print(lines[line_num])
# #     #         else:
# #     #             print(page_content)
# #     #         number = i+1
# #     #         print("-" * (len(f"--- Page Chunk {i+1} ---") + 20) + "\n")
# #     #         send_data_to_llm(page_content,number,file_name)

# #     # else:
# #     #     print(f"No page chunks were created from '{file_path}'.")



import os
import re
import fitz 
from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from llm_call import VertexAILangchainLLM
from get_summary_prompt import get_summary_prompt
from pathlib import Path
import streamlit as st # For potential UI feedback

def create_page_chunks(file_path):
    # ... (rest of the function remains the same)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        # Use st.error if in Streamlit context, otherwise print
        if 'st' in globals() and hasattr(st, 'error'):
            st.error(f"Error: File not found at {file_path}")
        else:
            print(f"Error: File not found at {file_path}")
        return []
    except Exception as e:
        if 'st' in globals() and hasattr(st, 'error'):
            st.error(f"Error reading file {file_path}: {e}")
        else:
            print(f"Error reading file {file_path}: {e}")
        return []

    header_pattern = re.compile(
        r"(^Revised AWPR Guidelines\s*\n"
        r"Ref No\.:[^\n]*\n"
        r"Money & Banking Division[^\n]*\n"
        r"Email:[^\n]*\n"
        r"\d+ \| P a g e\s*\n)",
        re.MULTILINE
    )
    parts = header_pattern.split(text)
    page_chunks = []
    for i in range(1, len(parts), 2):
        header = parts[i]
        if (i + 1) < len(parts):
            content = parts[i+1]
            page_chunks.append(header + content)
        else:
            page_chunks.append(header)
            
    return page_chunks

def send_data_to_llm(chunk, number, regulation_name_for_summary_dir, base_summary_output_path="summary", use_streamlit_feedback=False):

    if use_streamlit_feedback:
        st.caption(f"--- Sending chunk {number} to LLM for summarization ---")
    else:
        print(f"--- Sending chunk {number} to LLM for summarization ---")

    messages = []
    template = get_summary_prompt()
    human_template = HumanMessagePromptTemplate.from_template(template)
    messages.append(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(messages)
    request = chat_prompt.format_prompt(section_name=str(number), # Assuming section_name is the chunk number
                                        text_contents=chunk,
                                        ).to_messages()
    
    request_dicts = [{"role": msg.type, "content": msg.content} for msg in request]

    # Construct the full path for the summary file
    target_summary_dir = os.path.join(base_summary_output_path, regulation_name_for_summary_dir)
    Path(target_summary_dir).mkdir(parents=True, exist_ok=True)
    
    summary_file_path = os.path.join(target_summary_dir, f"chunk_{number}.txt")

    if use_streamlit_feedback:
        st.caption(f"Attempting to save summary for chunk {number} to: {summary_file_path}")
    else:
        print(f"Attempting to save summary for chunk {number} to: {summary_file_path}")

    llm = VertexAILangchainLLM({})
    try:
        response = llm._call(prompt=str(request_dicts))
        with open(summary_file_path, 'w', encoding='utf-8') as f:
            f.write(response)
        
        if use_streamlit_feedback:
            st.caption(f"Chunk {number} summary saved successfully.")
        else:
            print(f"Chunk {number} summary saved successfully.")
        return response
    except Exception as e:
        error_msg = f"Error processing chunk {number} with LLM or saving summary: {e}"
        if use_streamlit_feedback:
            st.error(error_msg)
        else:
            print(error_msg)
        return None # Or raise e

def extract_embedded_text(pdf_path: str, use_streamlit_feedback=False) -> str:
    if not os.path.exists(pdf_path):
        return f"Error: PDF file not found at '{pdf_path}'"

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return f"Error opening PDF file '{pdf_path}': {e}"
        
    full_text = []
    if use_streamlit_feedback:
        st.caption(f"Extracting text from {len(doc)} pages in '{os.path.basename(pdf_path)}'...")
    else:
        print(f"Attempting to extract embedded text from {len(doc)} pages in '{pdf_path}'...\n")


    for page_num in range(len(doc)):
        try:
            page = doc.load_page(page_num)
            text = page.get_text("text") 
            full_text.append(text)
            # Optional: more granular feedback
            # if use_streamlit_feedback:
            #     st.caption(f"Page {page_num + 1} processed.")
        except Exception as e:
            error_on_page = f"[Error processing page {page_num + 1}: {e}]"
            if use_streamlit_feedback: st.warning(error_on_page)
            else: print(error_on_page)
            full_text.append(error_on_page)
            
    doc.close()
    return "\n".join(full_text)

