import fitz  # PyMuPDF
import os

class PDFProcessor:
    """
    Handles processing of PDF files to extract text.
    """

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extracts text from a PDF file.

        Args:
            file_path (str): The absolute path to the PDF file.

        Returns:
            str: The extracted text content.

        Raises:
            Exception: If the file cannot be opened or processed.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            
            # Basic cleaning: remove excessive whitespace if needed, 
            # but for now we keep it raw to preserve structure.
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to process PDF {file_path}: {str(e)}")
