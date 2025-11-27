import fitz  # PyMuPDF
import os
from typing import Dict, Any
from component import BaseComponent

class PDFProcessor(BaseComponent):
    """
    Handles processing of PDF files to extract text.
    """

    def execute(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Executes the PDF extraction.

        Args:
            file_path (str): The absolute path to the PDF file.

        Returns:
            Dict[str, Any]: Dictionary containing the extracted text.
        """
        text = self.extract_text_from_pdf(file_path)
        return {"text": text}

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
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to process PDF {file_path}: {str(e)}")
