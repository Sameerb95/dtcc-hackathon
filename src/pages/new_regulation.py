# # import streamlit as st
# # import os
# # import pandas as pd
# # import re
# # import json
# # import sqlite3 
# # from extract_pages_summary import extract_embedded_text,create_page_chunks,send_data_to_llm


# # st.set_page_config(layout="wide")

# # DB_PATH = "resources/regulations_master.sqlite" # Define the path for your SQLite database
# # RESOURCE_PATH = "resources"


# # def init_db():
# #     """Initializes the SQLite database and creates the regulations table if it doesn't exist."""
# #     os.makedirs("resources", exist_ok=True) # Ensure the 'resources' directory exists
# #     conn = sqlite3.connect(DB_PATH)
# #     cursor = conn.cursor()
# #     cursor.execute("""
# #         CREATE TABLE IF NOT EXISTS regulations (
# #             id INTEGER PRIMARY KEY AUTOINCREMENT,
# #             name TEXT UNIQUE NOT NULL,
# #             path_key TEXT NOT NULL
# #         )
# #     """)
# #     conn.commit()
# #     conn.close()

# # def add_regulation_to_db(name, path_key):
# #     """Adds a new regulation to the SQLite database."""
# #     conn = sqlite3.connect(DB_PATH)
# #     cursor = conn.cursor()
# #     try:
# #         cursor.execute("INSERT INTO regulations (name, path_key) VALUES (?, ?)", (name, path_key))
# #         conn.commit()
# #         st.sidebar.success(f"Regulation '{name}' recorded in the database.")
# #     except sqlite3.IntegrityError:
# #         st.sidebar.warning(f"Regulation '{name}' already exists in the database.")
# #     except Exception as e:
# #         st.sidebar.error(f"Database error: {e}")
# #     finally:
# #         conn.close()

# # def get_all_regulation_names_from_db():
# #     """Retrieves all regulation names from the database."""
# #     conn = sqlite3.connect(DB_PATH)
# #     cursor = conn.cursor()
# #     cursor.execute("SELECT name FROM regulations ORDER BY name ASC")
# #     rows = cursor.fetchall()
# #     conn.close()
# #     return [row[0] for row in rows]



# # class AddData():

# #     def __init__(self):
# #         init_db()

# #     def upload(self,file,name):
    
# #         pdf_document_path = file
# #         output_txt_file = f"{name}/{name}_text.txt"

# #         print("Starting text extraction (without OCR, using PyMuPDF's get_text())...")

# #         extracted_text = extract_embedded_text(pdf_document_path)
        
# #         if extracted_text.startswith("Error:"):
# #             print(extracted_text) # Error message already formatted
# #         else:
# #             print("\n--- Text Extraction Complete ---")
# #             # Check if any meaningful text was extracted (ignoring whitespace and page processing errors)
# #             meaningful_text_found = any(line.strip() and not line.startswith("[Error processing page") for line in extracted_text.splitlines())

# #             if not meaningful_text_found:
# #                 print(f"No significant embedded text was found in '{pdf_document_path}'.")
# #                 print("The PDF might be image-based or scanned, which would require an OCR engine to extract text.")
# #                 print("This script only extracts pre-existing text layers within the PDF.")
# #             else:
# #                 try:
# #                     with open(output_txt_file, "w", encoding="utf-8") as f:
# #                         f.write(extracted_text)
# #                     print(f"Full extracted text saved to '{output_txt_file}'")
# #                 except IOError as e:
# #                     print(f"Error saving extracted text to file: {e}")
# #                     print("\nFull Extracted Text (first 1000 characters):\n")
# #                     print(extracted_text[:1000])

# #         file_path = "/Users/shirsama/dtcc-hackathon/dtcc-ai-hackathon-2025/AWPR Version 2_text.txt"
        
# #         file_name = os.path.basename(file_path).split('.')[0]

# #         pages = create_page_chunks(file_path)

# #         if pages:
# #             print(f"Successfully created {len(pages)} page chunks from '{file_path}'.\n")
# #             for i, page_content in enumerate(pages):
# #                 print(f"--- Page Chunk {i+1} (approx. {len(page_content.splitlines())} lines) ---")
# #                 # Print first few and last few lines of each chunk for brevity
# #                 lines = page_content.splitlines()
# #                 if len(lines) > 10:
# #                     for line_num in range(5):
# #                         print(lines[line_num])
# #                     print("...")
# #                     for line_num in range(len(lines) - 5, len(lines)):
# #                         print(lines[line_num])
# #                 else:
# #                     print(page_content)
# #                 number = i+1
# #                 print("-" * (len(f"--- Page Chunk {i+1} ---") + 20) + "\n")
# #                 send_data_to_llm(page_content,number,file_name)

# #         else:
# #             print(f"No page chunks were created from '{file_path}'.")
        
# #     def render(self):
# #         st.title("Add New Regulation Report ")
        

# #         reg_names = get_all_regulation_names_from_db()
# #         create_new_workflow = st.toggle("Create New Regulation")

# #         if create_new_workflow:
# #             new_regulation_name = st.text_input("Enter New Regulation Name")
# #             if new_regulation_name:
# #                 new_regulation_path = os.path.join(RESOURCE_PATH, new_regulation_name)
# #                 os.makedirs(new_regulation_path, exist_ok=True)
# #                 add_regulation_to_db(new_regulation_name,new_regulation_path)
# #                 regulation_select = new_regulation_name
                
# #         else:
# #             regulation_select = st.selectbox(
# #                 "Please select the workflow",
# #                 reg_names
# #             )


# #         uploaded_file = st.file_uploader("Choose a file", type=["pdf"])

# #         if uploaded_file is not None:
# #             file_details = {
# #                 "FileName": uploaded_file.name,
# #                 "FileType": uploaded_file.type,
# #                 "FileSize": uploaded_file.size,
# #             }

# #             st.write(file_details)

# #             self.upload(uploaded_file,regulation_select)
            

# # if __name__ == "__main__":
# #     st.sidebar.page_link(page="start.py", label="Home")
# #     ad_obj = AddData()
# #     ad_obj.render()


# import streamlit as st
# import os
# import pandas as pd # Not used in the provided snippet, but kept if used elsewhere
# import re # Not used in the provided snippet, but kept if used elsewhere
# import json # Not used in the provided snippet, but kept if used elsewhere
# import sqlite3 
# from extract_pages_summary import extract_embedded_text, create_page_chunks, send_data_to_llm
# from streamlit_extras.add_vertical_space import add_vertical_space # For consistency if used

# # Ensure this is at the top if you want to set page config for this page
# # st.set_page_config(layout="wide") # Already in the original, good.

# DB_PATH = "resources/regulations_master.sqlite"
# RESOURCE_PATH = "resources"


# def init_db():
#     """Initializes the SQLite database and creates the regulations table if it doesn't exist."""
#     os.makedirs(RESOURCE_PATH, exist_ok=True) 
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS regulations (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT UNIQUE NOT NULL,
#             path_key TEXT NOT NULL
#         )
#     """)
#     conn.commit()
#     conn.close()

# def add_regulation_to_db(name, path_key):
#     """Adds a new regulation to the SQLite database."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     try:
#         cursor.execute("INSERT INTO regulations (name, path_key) VALUES (?, ?)", (name, path_key))
#         conn.commit()
#         st.sidebar.success(f"Regulation '{name}' recorded in the database.")
#     except sqlite3.IntegrityError:
#         st.sidebar.warning(f"Regulation '{name}' already exists in the database.")
#     except Exception as e:
#         st.sidebar.error(f"Database error: {e}")
#     finally:
#         conn.close()

# def get_all_regulation_names_from_db():
#     """Retrieves all regulation names from the database."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("SELECT name FROM regulations ORDER BY name ASC")
#     rows = cursor.fetchall()
#     conn.close()
#     return [row[0] for row in rows]


# class AddData():

#     def __init__(self):
#         init_db() # Initialize DB when class is instantiated

#     def upload(self, uploaded_file_obj, regulation_name):
#         """
#         Processes the uploaded PDF file for the given regulation.
#         - Saves the PDF.
#         - Extracts text.
#         - Saves extracted text.
#         - Creates page chunks from the text.
#         - Sends chunks to LLM for summary.
#         """
#         if uploaded_file_obj is None:
#             st.error("No file uploaded to process.")
#             return

#         regulation_specific_dir = os.path.join(RESOURCE_PATH, regulation_name)
#         os.makedirs(regulation_specific_dir, exist_ok=True)

       
#         saved_pdf_path = os.path.join(regulation_specific_dir, uploaded_file_obj.name)
        
       
#         output_txt_file = os.path.join(regulation_specific_dir, f"{regulation_name}_extracted_text.txt")

#         try:
#             with open(saved_pdf_path, "wb") as f:
#                 f.write(uploaded_file_obj.getbuffer())
#             st.info(f"Uploaded PDF '{uploaded_file_obj.name}' saved to '{saved_pdf_path}'")
#         except Exception as e:
#             st.error(f"Error saving uploaded PDF: {e}")
#             return

#         st.info("Starting text extraction from PDF...")
#         extracted_text = extract_embedded_text(saved_pdf_path)
        
#         if extracted_text.startswith("Error:"):
#             st.error(f"Text extraction failed: {extracted_text}")
#             return
#         else:
#             st.success("Text extraction complete.")
#             meaningful_text_found = any(line.strip() and not line.startswith("[Error processing page") for line in extracted_text.splitlines())

#             if not meaningful_text_found:
#                 st.warning(f"No significant embedded text was found in '{uploaded_file_obj.name}'. "
#                            "The PDF might be image-based or scanned, requiring an OCR engine.")
            
#                 try:
#                     with open(output_txt_file, "w", encoding="utf-8") as f:
#                         f.write(extracted_text) 
#                     st.info(f"Extraction output (even if minimal) saved to '{output_txt_file}'")
#                 except IOError as e:
#                     st.error(f"Error saving extracted text to file: {e}")
#                     return
#                 if not meaningful_text_found: 
#                     st.warning("Skipping chunking and LLM processing due to lack of meaningful text.")
#                     return

#             else: # Meaningful text found
#                 try:
#                     with open(output_txt_file, "w", encoding="utf-8") as f:
#                         f.write(extracted_text)
#                     st.info(f"Full extracted text saved to '{output_txt_file}'")
#                 except IOError as e:
#                     st.error(f"Error saving extracted text to file: {e}")
#                     return

#         st.info(f"Creating page chunks from '{output_txt_file}'...")
#         pages = create_page_chunks(output_txt_file)

#         if pages:
#             st.success(f"Successfully created {len(pages)} page chunks.")
#             progress_bar = st.progress(0)
#             total_pages = len(pages)
            
#             summaries_base_for_this_regulation = os.path.join(RESOURCE_PATH, regulation_name)
#             summaries_leaf_dir_name = "generated_summaries"

#             with st.expander(f"Processing {total_pages} Chunks (Details)...", expanded=False):
#                 for i, page_content in enumerate(pages):
#                     chunk_number = i + 1
                    
#                     send_data_to_llm(
#                         page_content, 
#                         chunk_number, 
#                         regulation_name_for_summary_dir=summaries_leaf_dir_name,
#                         base_summary_output_path=summaries_base_for_this_regulation,
#                         use_streamlit_feedback=True
#                     )
#                     progress_bar.progress((i + 1) / total_pages)
#             st.success(f"All {len(pages)} page chunks processed and sent for summarization.")
#         else:
#             st.warning(f"No page chunks were created from '{output_txt_file}'.")
        
#     def render(self):
#         st.title("Add New Regulation Report")
#         add_vertical_space(1)

#         reg_names = get_all_regulation_names_from_db()
        
#         st.subheader("1. Select or Create Regulation")
#         create_new_workflow = st.toggle("Create New Regulation Workflow", value=True if not reg_names else False)

#         regulation_select = None 

#         if create_new_workflow:
#             new_regulation_name_input = st.text_input("Enter New Regulation Name", key="new_reg_name")
#             if new_regulation_name_input:
#                 regulation_select = new_regulation_name_input
#                 new_regulation_path_key = os.path.join(RESOURCE_PATH, regulation_select)
#                 if st.button(f"Confirm and Create Regulation: '{regulation_select}'"):
#                     os.makedirs(new_regulation_path_key, exist_ok=True) 
#                     add_regulation_to_db(regulation_select, new_regulation_path_key)
#             else:
#                 st.info("Please enter a name for the new regulation.")
#         else:
#             if reg_names:
#                 regulation_select = st.selectbox(
#                     "Select an Existing Regulation Workflow",
#                     options=[""] + reg_names, 
#                     index=0,
#                     key="existing_reg_select"
#                 )
#                 if not regulation_select: 
#                     st.info("Please select a regulation.")
#             else:
#                 st.warning("No existing regulations found. Please toggle to 'Create New Regulation Workflow'.")

#         add_vertical_space(2)
        
#         if regulation_select: 
#             st.subheader(f"2. Upload PDF for '{regulation_select}'")
#             uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], key="pdf_uploader")

#             if uploaded_file is not None:
#                 st.write("File Details:")
#                 st.json({
#                     "FileName": uploaded_file.name,
#                     "FileType": uploaded_file.type,
#                     "FileSize": f"{uploaded_file.size / (1024*1024):.2f} MB",
#                 })

#                 if st.button(f"Process '{uploaded_file.name}' for '{regulation_select}'", key="process_button"):
#                     # Ensure the regulation directory exists before processing
#                     regulation_specific_dir = os.path.join(RESOURCE_PATH, regulation_select)
#                     os.makedirs(regulation_specific_dir, exist_ok=True)
                    
#                     # Path to save the uploaded PDF
#                     saved_pdf_path = os.path.join(regulation_specific_dir, uploaded_file.name)
#                     try:
#                         with open(saved_pdf_path, "wb") as f:
#                             f.write(uploaded_file.getbuffer())
#                         st.info(f"Uploaded PDF '{uploaded_file.name}' saved to '{saved_pdf_path}'")
#                     except Exception as e:
#                         st.error(f"Error saving uploaded PDF: {e}")
#                         return # Stop processing if PDF can't be saved

#                     # Path for the extracted text file
#                     output_txt_file = os.path.join(regulation_specific_dir, f"{regulation_select}_extracted_text.txt")

#                     with st.spinner(f"Extracting text from '{uploaded_file.name}'..."):
#                         extracted_text = extract_embedded_text(saved_pdf_path, use_streamlit_feedback=True)
                    
#                     if extracted_text.startswith("Error:"):
#                         st.error(f"Text extraction failed: {extracted_text}")
#                         return
#                     else:
#                         st.success("Text extraction complete.")
#                         meaningful_text_found = any(line.strip() and not line.startswith("[Error processing page") for line in extracted_text.splitlines())

#                         if not meaningful_text_found:
#                             st.warning(f"No significant embedded text was found in '{uploaded_file.name}'.")
#                             # Save what was extracted anyway
#                         try:
#                             with open(output_txt_file, "w", encoding="utf-8") as f:
#                                 f.write(extracted_text) 
#                             st.info(f"Extraction output saved to '{output_txt_file}'")
#                         except IOError as e:
#                             st.error(f"Error saving extracted text to file: {e}")
#                             return
#                         if not meaningful_text_found:
#                             st.warning("Skipping chunking and LLM processing due to lack of meaningful text.")
#                             return
                    
#                     with st.spinner(f"Processing '{uploaded_file.name}' for regulation '{regulation_select}'... This may take a while."):
#                         self.upload(uploaded_file, regulation_select) # Pass the original uploaded_file_obj
#         elif create_new_workflow and not regulation_select :
#              pass 
#         else: 
#             st.info("Please select or create a regulation name above before uploading a file.")


# if __name__ == "__main__":
#     st.sidebar.page_link(page="pages/home.py", label="Home")
#     ad_obj = AddData()
#     ad_obj.render()

####=================================================

import streamlit as st
import os
import sqlite3 
from streamlit_extras.add_vertical_space import add_vertical_space
from pathlib import Path # Import Path

try:
    from upload_interface import UploadProcessor 
except ImportError:
    try:
        from ..upload_interface import UploadProcessor
    except ImportError:
        st.error("Critical Import Error: Could not import UploadProcessor from upload_interface.py.")
        UploadProcessor = None


DB_PATH = "resources/regulations_master.sqlite"
RESOURCE_PATH = "resources" # This is the top-level resource directory


def init_db():
    """Initializes the SQLite database and creates the regulations table if it doesn't exist."""
    os.makedirs(RESOURCE_PATH, exist_ok=True) 
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            path_key TEXT NOT NULL 
        )
    """)
    conn.commit()
    conn.close()

def add_regulation_to_db(name, path_key_for_regulation_base):
    """
    Adds a new regulation to the SQLite database.
    The path_key stored will be the base path for the regulation, e.g., "resources/MyRegulation".
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO regulations (name, path_key) VALUES (?, ?)", (name, path_key_for_regulation_base))
        conn.commit()
        st.sidebar.success(f"Regulation '{name}' recorded in the database.")
    except sqlite3.IntegrityError:
        st.sidebar.warning(f"Regulation '{name}' already exists in the database.")
    except Exception as e:
        st.sidebar.error(f"Database error: {e}")
    finally:
        conn.close()

def get_all_regulation_names_from_db():
    """Retrieves all regulation names from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM regulations ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


class AddData():

    def __init__(self):
        init_db() 

    def upload_and_process_document(self, uploaded_file_obj, regulation_name_selected, version_subfolder="old"):
        """
        Uses UploadProcessor to handle the uploaded PDF, placing it in the 'old' or 'new' subfolder.
        For "Add New Regulation", this will typically be the 'old' (V1) document.
        """
        if uploaded_file_obj is None:
            st.error("No file uploaded to process.")
            return False

        if not UploadProcessor:
            st.error("UploadProcessor is not available. Cannot process file.")
            return False

        # Base path for this specific regulation, e.g., "resources/MyRegulation"
        regulation_base_path = Path(RESOURCE_PATH) / regulation_name_selected
        
        # Path for the specific version (old/new), e.g., "resources/MyRegulation/old"
        version_specific_path = regulation_base_path / version_subfolder
        version_specific_path.mkdir(parents=True, exist_ok=True) # Ensure it exists

        # The 'regulation_name' for UploadProcessor will be the PDF's stem.
        # This means UploadProcessor will create its output under:
        # resources/<regulation_name_selected>/<version_subfolder>/<pdf_file_stem>/
        pdf_file_stem = Path(uploaded_file_obj.name).stem

        processor = UploadProcessor(
            st_object=st, 
            uploaded_file_obj=uploaded_file_obj, 
            regulation_name=pdf_file_stem, # This becomes the sub-folder name under version_specific_path
            resource_path=str(version_specific_path) # Base for this processor instance
        )
        
        with st.spinner(f"Processing '{uploaded_file_obj.name}' for regulation '{regulation_name_selected}' (as {version_subfolder} version)... This may take a while."):
            success = processor.process()
        
        if success:
            st.success(f"Successfully processed '{uploaded_file_obj.name}' for '{regulation_name_selected}'. Files stored under '{version_specific_path / pdf_file_stem}'.")
        else:
            st.error(f"Failed to fully process '{uploaded_file_obj.name}' for '{regulation_name_selected}'. Check logs above.")
        return success
        
    def render(self):
        st.title("Add New Regulation (Initial Version)")
        add_vertical_space(1)

        reg_names = get_all_regulation_names_from_db()
        
        st.subheader("1. Select or Create Regulation Name")
        default_toggle_value = True if not reg_names else False
        create_new_workflow = st.toggle("Create New Regulation Name", value=default_toggle_value, key="create_new_reg_toggle")

        regulation_select = None 

        if create_new_workflow:
            new_regulation_name_input = st.text_input("Enter New Regulation Name", key="new_reg_name_input")
            if new_regulation_name_input:
                regulation_select = new_regulation_name_input.strip()
                if not regulation_select:
                    st.warning("Regulation name cannot be empty.")
                    regulation_select = None 
                else:
                    regulation_base_dir = Path(RESOURCE_PATH) / regulation_select
                    old_version_dir = regulation_base_dir / "old"
                    new_version_dir = regulation_base_dir / "new"

                    if st.button(f"Confirm and Create Regulation: '{regulation_select}'", key="confirm_create_reg_btn"):
                        try:
                            old_version_dir.mkdir(parents=True, exist_ok=True)
                            new_version_dir.mkdir(parents=True, exist_ok=True)
                            st.caption(f"Created directory structure: '{regulation_base_dir}/[old, new]'")
                            # The path_key stored in DB is the base for the regulation name
                            add_regulation_to_db(regulation_select, str(regulation_base_dir))
                            # Refresh names to include the new one if selectbox is shown later
                            # st.rerun() # Could rerun to update selectbox if needed, or just proceed
                        except Exception as e:
                            st.error(f"Error creating directories for '{regulation_select}': {e}")
                            regulation_select = None # Prevent proceeding if dir creation fails
            else:
                st.info("Please enter a name for the new regulation.")
        else:
            if reg_names:
                regulation_select = st.selectbox(
                    "Select an Existing Regulation (to add/update its initial/V1 document)",
                    options=[""] + reg_names, 
                    index=0, 
                    key="existing_reg_select_new_page"
                )
                if not regulation_select: 
                    st.info("Please select a regulation from the dropdown.")
            else:
                st.warning("No existing regulations found. Please toggle to 'Create New Regulation Name' above.")

        add_vertical_space(2)
        
        if regulation_select: 
            st.subheader(f"2. Upload Initial PDF (V1) for '{regulation_select}'")
            
            # Ensure the 'old' directory exists for the selected regulation
            regulation_old_dir = Path(RESOURCE_PATH) / regulation_select / "old"
            if not regulation_old_dir.exists():
                try:
                    regulation_old_dir.mkdir(parents=True, exist_ok=True)
                    st.caption(f"Ensured 'old' directory exists at: '{regulation_old_dir}'")
                except Exception as e:
                    st.error(f"Could not create 'old' directory for '{regulation_select}': {e}. Upload might fail.")
                    return # Stop if essential directory can't be made

            uploaded_file = st.file_uploader(
                "Choose a PDF file for the initial version", 
                type=["pdf"], 
                key=f"pdf_uploader_new_reg_{regulation_select}" # Unique key
            )

            if uploaded_file is not None:
                st.write("File Details:")
                file_size_mb = uploaded_file.size / (1024*1024)
                st.json({
                    "FileName": uploaded_file.name,
                    "FileType": uploaded_file.type,
                    "FileSize": f"{file_size_mb:.2f} MB",
                })

                if st.button(f"Process '{uploaded_file.name}' as Initial Version for '{regulation_select}'", key=f"process_initial_btn_{regulation_select}"):
                    self.upload_and_process_document(uploaded_file, regulation_select, version_subfolder="old")
        
        elif create_new_workflow and not regulation_select :
             st.info("Enter and confirm a new regulation name above to proceed with file upload.")
        elif not create_new_workflow and not reg_names:
             st.info("Please create a new regulation name first.")
        elif not create_new_workflow and not regulation_select:
             st.info("Please select an existing regulation to proceed with file upload.")


if __name__ == "__main__":
    st.sidebar.page_link(page="pages/home.py", label="Home") 
    st.sidebar.page_link(page="pages/new_regulation.py", label="Add New Regulation (First Version)")

    ad_obj = AddData()
    ad_obj.render()

