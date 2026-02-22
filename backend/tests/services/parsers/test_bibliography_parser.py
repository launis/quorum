import pytest

from backend.exceptions import AppException
from backend.services.parsers.bibliography_parser import BibliographyParser


class TestBibliographyParser:
    def test_detect_bibliography_header(self):
        parser = BibliographyParser()
        text = """
        Some content here.
        More content.

        References
        [1] Smith, J. (2020). AI Ethics.
        [2] Doe, A. (2021). Machine Learning.
        """
        bib_text = parser.detect_bibliography(text)
        assert bib_text is not None
        assert "[1] Smith" in bib_text
        assert "References" in bib_text

    def test_detect_bibliography_finnish(self):
        parser = BibliographyParser()
        text = """
        Jotain tekstiä.

        Lähdeluettelo
        [1] Virtanen, M. (2020). Tekoäly.
        """
        bib_text = parser.detect_bibliography(text)
        assert bib_text is not None
        assert "Lähdeluettelo" in bib_text

    def test_parse_references_simple(self):
        parser = BibliographyParser()
        text = """
        Some text.

        Bibliography
        [1] Smith, J. (2020). AI Ethics.
        [2] Doe, A. (2021). Machine Learning.
        """
        refs = parser.parse_references(text)
        assert len(refs) == 2
        assert refs["1"] == "Smith, J. (2020). AI Ethics."
        assert refs["2"] == "Doe, A. (2021). Machine Learning."

    def test_parse_references_multiline(self):
        parser = BibliographyParser()
        text = """
        References
        [1] Smith, J. (2020).
            AI Ethics and Society.
            Journal of AI.
        [2] Doe, A. (2021). ML.
        """
        refs = parser.parse_references(text)
        assert len(refs) == 2
        assert "AI Ethics and Society" in refs["1"]
        assert "Journal of AI" in refs["1"]

    def test_no_bibliography(self):
        parser = BibliographyParser()
        text = "Just some text without references."
        with pytest.raises(AppException):
            parser.parse_references(text)
