from unittest.mock import Mock, patch

import pytest

from src.crm.document_processor import DocumentProcessor


class TestDocumentProcessor:
    @pytest.fixture
    def processor(self) -> DocumentProcessor:
        return DocumentProcessor()

    def test_get_content_hash(self, processor: DocumentProcessor) -> None:
        content1 = b"test content"
        content2 = b"different content"

        hash1 = processor.get_content_hash(content1)
        hash2 = processor.get_content_hash(content2)

        assert hash1 != hash2
        assert len(hash1) == 64  # SHA256 hex length
        assert processor.get_content_hash(content1) == hash1  # Consistent

    def test_is_valid_file_size(self, processor: DocumentProcessor) -> None:
        processor.max_file_size = 1024  # 1KB

        valid, error = processor.is_valid_file("test.pdf", 512)
        assert valid is True
        assert error is None

        invalid, error = processor.is_valid_file("test.pdf", 2048)
        assert invalid is False
        assert "exceeds maximum" in error

    def test_is_valid_file_extension(self, processor: DocumentProcessor) -> None:
        processor.allowed_extensions = {"pdf", "docx", "txt"}

        valid, error = processor.is_valid_file("resume.pdf", 100)
        assert valid is True
        assert error is None

        invalid, error = processor.is_valid_file("resume.exe", 100)
        assert invalid is False
        assert "not allowed" in error

    def test_extract_text_from_docx(self, processor: DocumentProcessor) -> None:
        # Mock docx.Document
        with patch("src.crm.document_processor.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc

            # Mock paragraphs
            mock_paragraph = Mock()
            mock_paragraph.text = "Test paragraph content"
            mock_doc.paragraphs = [mock_paragraph]

            # Mock tables (empty for this test)
            mock_doc.tables = []

            content = b"fake docx content"
            result = processor.extract_text_from_docx(content)

            assert result == "Test paragraph content"
            mock_doc_class.assert_called_once()

    def test_extract_text_from_pdf(self, processor: DocumentProcessor) -> None:
        with patch("src.crm.document_processor.extract_pdf_text") as mock_extract:
            mock_extract.return_value = "  Extracted PDF text  "

            content = b"fake pdf content"
            result = processor.extract_text_from_pdf(content)

            assert result == "Extracted PDF text"
            mock_extract.assert_called_once()

    def test_extract_text_from_doc(self, processor: DocumentProcessor) -> None:
        # Simulate a .doc file with some readable text mixed with binary
        content = b"Some readable text\x00\x01\x02mixed with binary\x00data"
        result = processor.extract_text_from_doc(content)

        assert "Some readable text" in result
        assert "mixed with binary" in result
        # Binary characters should be cleaned up
        assert "\x00" not in result

    def test_extract_text_pdf_file(self, processor: DocumentProcessor) -> None:
        with patch.object(processor, "extract_text_from_pdf") as mock_extract:
            mock_extract.return_value = "PDF content"

            content = b"fake pdf"
            result = processor.extract_text(content, "resume.pdf")

            assert result == "PDF content"
            mock_extract.assert_called_once_with(content)

    def test_extract_text_docx_file(self, processor: DocumentProcessor) -> None:
        with patch.object(processor, "extract_text_from_docx") as mock_extract:
            mock_extract.return_value = "DOCX content"

            content = b"fake docx"
            result = processor.extract_text(content, "resume.docx")

            assert result == "DOCX content"
            mock_extract.assert_called_once_with(content)

    def test_extract_text_doc_file(self, processor: DocumentProcessor) -> None:
        with patch.object(processor, "extract_text_from_doc") as mock_extract:
            mock_extract.return_value = "DOC content"

            content = b"fake doc"
            result = processor.extract_text(content, "resume.doc")

            assert result == "DOC content"
            mock_extract.assert_called_once_with(content)

    def test_extract_text_with_cache(self, processor: DocumentProcessor) -> None:
        processor.enable_cache = True

        with patch.object(processor, "extract_text_from_pdf") as mock_extract:
            mock_extract.return_value = "Cached content"

            content = b"test content"

            # First call
            result1 = processor.extract_text(content, "test.pdf")
            assert result1 == "Cached content"
            assert mock_extract.call_count == 1

            # Second call should use cache
            result2 = processor.extract_text(content, "test.pdf")
            assert result2 == "Cached content"
            assert mock_extract.call_count == 1  # Not called again

    def test_extract_text_invalid_file(self, processor: DocumentProcessor) -> None:
        content = b"test content"

        with pytest.raises(ValueError, match="not allowed"):
            processor.extract_text(content, "malware.exe")

    def test_extract_text_empty_content(self, processor: DocumentProcessor) -> None:
        with patch.object(processor, "extract_text_from_pdf") as mock_extract:
            mock_extract.return_value = ""

            content = b"empty pdf"

            with pytest.raises(ValueError, match="No text could be extracted"):
                processor.extract_text(content, "empty.pdf")
