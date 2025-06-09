import os
import streamlit as st
from extract_pages_summary import extract_embedded_text, create_page_chunks, send_data_to_llm
from pathlib import Path

class UploadProcessor:
    def __init__(self, st_object, uploaded_file_obj, regulation_name, resource_path):
        self.st = st_object
        self.uploaded_file_obj = uploaded_file_obj
        self.regulation_name = regulation_name
        self.resource_path = resource_path
        
        # Define paths specific to this regulation and upload
        self.regulation_specific_dir = Path(self.resource_path) / self.regulation_name
        self.saved_pdf_path = self.regulation_specific_dir / self.uploaded_file_obj.name
        self.output_txt_file = self.regulation_specific_dir / f"{self.regulation_name}_extracted_text.txt"
        
        # Ensure the regulation-specific directory exists
        self.regulation_specific_dir.mkdir(parents=True, exist_ok=True)

    def _save_pdf(self):
        """Saves the uploaded PDF to the designated path."""
        try:
            with open(self.saved_pdf_path, "wb") as f:
                f.write(self.uploaded_file_obj.getbuffer())
            self.st.info(f"Uploaded PDF '{self.uploaded_file_obj.name}' saved to '{self.saved_pdf_path}'")
            return True
        except Exception as e:
            self.st.error(f"Error saving uploaded PDF: {e}")
            return False

    def _extract_and_save_text(self):
        """Extracts text from the saved PDF and saves it to a text file."""
        self.st.info(f"Starting text extraction from '{self.saved_pdf_path.name}'...")
        extracted_text = extract_embedded_text(str(self.saved_pdf_path), use_streamlit_feedback=True)
        
        if extracted_text.startswith("Error:"):
            self.st.error(f"Text extraction failed: {extracted_text}")
            return None # Indicate error
        
        self.st.success("Text extraction complete.")
        meaningful_text_found = any(line.strip() and not line.startswith("[Error processing page") for line in extracted_text.splitlines())

        if not meaningful_text_found:
            self.st.warning(f"No significant embedded text was found in '{self.uploaded_file_obj.name}'. "
                       "The PDF might be image-based or scanned, requiring an OCR engine.")
        
        try:
            with open(self.output_txt_file, "w", encoding="utf-8") as f:
                f.write(extracted_text) 
            self.st.info(f"Extraction output saved to '{self.output_txt_file}'")
        except IOError as e:
            self.st.error(f"Error saving extracted text to file: {e}")
            return None # Indicate error
            
        return meaningful_text_found # Return status of meaningful text

    def _chunk_and_summarize(self):
        """Creates page chunks from the extracted text and sends them for summarization."""
        self.st.info(f"Creating page chunks from '{self.output_txt_file.name}'...")
        pages = create_page_chunks(str(self.output_txt_file))

        if not pages:
            self.st.warning(f"No page chunks were created from '{self.output_txt_file.name}'. Summarization skipped.")
            return True # Not an error, but no summaries generated

        self.st.success(f"Successfully created {len(pages)} page chunks.")
        progress_bar = self.st.progress(0)
        total_pages = len(pages)
        
        # Define where summaries for this specific regulation instance will be stored
        # base_summary_output_path will be "resources/REGULATION_NAME"
        # regulation_name_for_summary_dir will be a sub-directory like "generated_summaries"
        summaries_base_dir = self.regulation_specific_dir 
        summaries_leaf_dir_name = f"{Path(self.uploaded_file_obj.name).stem}_summaries" # e.g. "MyDocument_summaries"

        self.st.info(f"Sending {total_pages} chunks for summarization. This may take a while...")
        with self.st.expander(f"Summarization Log (Processing {total_pages} Chunks)...", expanded=False):
            for i, page_content in enumerate(pages):
                chunk_number = i + 1
                
                send_data_to_llm(
                    chunk=page_content, 
                    number=chunk_number, 
                    regulation_name_for_summary_dir=summaries_leaf_dir_name,
                    base_summary_output_path=str(summaries_base_dir),
                    use_streamlit_feedback=True 
                )
                progress_bar.progress((i + 1) / total_pages)
        self.st.success(f"All {len(pages)} page chunks processed and sent for summarization.")
        return True

    def process(self):
        """
        Orchestrates the entire PDF processing workflow:
        1. Save PDF
        2. Extract and save text
        3. Chunk text and generate summaries (if meaningful text is found)
        Returns True if all critical steps succeed, False otherwise.
        """
        if not self._save_pdf():
            return False

        meaningful_text_status = self._extract_and_save_text()
        if meaningful_text_status is None: # Error during text extraction/saving
            return False
        
        if not meaningful_text_status: # No meaningful text found, but extraction itself was okay
            self.st.warning("Skipping chunking and LLM processing due to lack of meaningful text.")
            return True # Processing "succeeded" in the sense that it handled the empty case

        if not self._chunk_and_summarize():
            # This path might not be hit if _chunk_and_summarize always returns True
            # but kept for robustness if it were to signal critical summarization failures.
            return False 
            
        return True

