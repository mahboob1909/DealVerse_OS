"""
Test document processing pipeline functionality
"""
import pytest
import asyncio
from io import BytesIO
from fastapi import UploadFile
from unittest.mock import Mock, patch, AsyncMock

from app.services.document_processor import DocumentProcessor


@pytest.fixture
def document_processor():
    """Create document processor instance for testing"""
    return DocumentProcessor()


@pytest.fixture
def sample_pdf_file():
    """Create a mock PDF file for testing"""
    # Simple PDF content (minimal valid PDF)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
181
%%EOF"""
    
    file_obj = UploadFile(
        file=BytesIO(pdf_content),
        filename="test_document.pdf",
        headers={"content-type": "application/pdf"}
    )
    return file_obj


@pytest.fixture
def sample_text_file():
    """Create a mock text file for testing"""
    text_content = b"This is a sample document for testing the processing pipeline. It contains some text for analysis."
    
    file_obj = UploadFile(
        file=BytesIO(text_content),
        filename="test_document.txt",
        headers={"content-type": "text/plain"}
    )
    return file_obj


class TestDocumentProcessor:
    """Test document processor functionality"""
    
    @pytest.mark.asyncio
    async def test_validate_file_enhanced(self, document_processor, sample_text_file):
        """Test enhanced file validation"""
        result = await document_processor._validate_file_enhanced(sample_text_file)
        
        assert result["is_valid"] is True
        assert result["file_size"] > 0
        assert result["mime_type"] == "text/plain"
        assert result["file_extension"] == ".txt"
    
    @pytest.mark.asyncio
    async def test_virus_scanning(self, document_processor, sample_text_file):
        """Test virus scanning functionality"""
        result = await document_processor._scan_for_viruses(sample_text_file)
        
        assert result["is_safe"] is True
        assert result["threats_detected"] == []
        assert result["scan_method"] == "pattern_detection"
    
    @pytest.mark.asyncio
    async def test_extract_enhanced_metadata(self, document_processor, sample_text_file):
        """Test enhanced metadata extraction"""
        await sample_text_file.seek(0)
        file_content = await sample_text_file.read()
        
        result = await document_processor._extract_enhanced_metadata(sample_text_file, file_content)
        
        assert result["filename"] == "test_document.txt"
        assert result["file_size"] > 0
        assert result["mime_type"] == "text/plain"
        assert result["file_extension"] == ".txt"
        assert "creation_date" in result
    
    @pytest.mark.asyncio
    async def test_extract_text_content(self, document_processor, sample_text_file):
        """Test text content extraction"""
        await sample_text_file.seek(0)
        file_content = await sample_text_file.read()
        
        result = await document_processor._extract_text_content_enhanced(
            sample_text_file, file_content, "text/plain"
        )
        
        assert "sample document" in result.lower()
        assert "testing" in result.lower()
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_generate_thumbnail(self, document_processor, sample_text_file):
        """Test thumbnail generation"""
        await sample_text_file.seek(0)
        file_content = await sample_text_file.read()
        
        result = await document_processor._generate_thumbnail(
            sample_text_file, file_content, "text/plain"
        )
        
        assert result is not None
        assert len(result) > 0  # Should have thumbnail data
    
    @pytest.mark.asyncio
    async def test_analyze_text_content(self, document_processor):
        """Test text analysis functionality"""
        sample_text = "This is a sample document for testing. It contains financial data and legal terms."
        
        result = await document_processor._analyze_text_content(sample_text)
        
        assert result["word_count"] > 0
        assert result["character_count"] > 0
        assert "readability_score" in result
        assert "language" in result
        assert "entities" in result
        assert "key_phrases" in result
    
    @pytest.mark.asyncio
    async def test_create_search_index(self, document_processor):
        """Test search index creation"""
        sample_text = "This is a financial document with important legal terms and conditions."
        metadata = {"filename": "test.txt", "document_type": "legal"}
        text_analysis = {"entities": ["financial", "legal"], "key_phrases": ["important terms"]}
        
        result = await document_processor._create_search_index(sample_text, metadata, text_analysis)
        
        assert "keywords" in result
        assert "content_classification" in result
        assert "searchable_content" in result
        assert len(result["keywords"]) > 0
    
    @pytest.mark.asyncio
    @patch('app.services.document_processor.get_s3_storage')
    async def test_store_processing_artifacts(self, mock_get_s3_storage, document_processor):
        """Test storing processing artifacts"""
        mock_s3_service = AsyncMock()
        mock_s3_service.upload_file_direct = AsyncMock(return_value={
            "file_key": "test/artifact.jpg",
            "file_size": 1024,
            "content_type": "image/jpeg"
        })
        mock_get_s3_storage.return_value = mock_s3_service
        
        thumbnail_data = b"fake_thumbnail_data"
        text_content = "extracted text content"
        search_index = {"keywords": ["test", "document"]}
        
        result = await document_processor._store_processing_artifacts(
            "doc123", "org456", thumbnail_data, text_content, search_index
        )
        
        assert "thumbnail" in result
        assert "extracted_text" in result
        assert "search_index" in result
        assert mock_s3_service.upload_file_direct.call_count == 3
    
    @pytest.mark.asyncio
    @patch('app.services.document_processor.get_s3_storage')
    async def test_process_document_pipeline_success(self, mock_get_s3_storage, document_processor, sample_text_file):
        """Test complete document processing pipeline"""
        mock_s3_service = AsyncMock()
        mock_s3_service.upload_file_direct = AsyncMock(return_value={
            "file_key": "test/artifact.jpg",
            "file_size": 1024,
            "content_type": "image/jpeg",
            "s3_key": "test/artifact.jpg"
        })
        mock_get_s3_storage.return_value = mock_s3_service
        
        result = await document_processor.process_document_pipeline(
            file=sample_text_file,
            document_id="doc123",
            organization_id="org456"
        )
        
        assert result["validation"]["is_valid"] is True
        assert result["virus_scan"]["is_safe"] is True
        assert "metadata" in result
        assert "text_content" in result
        assert "thumbnail" in result
        assert "text_analysis" in result
        assert "search_index" in result
        assert "artifacts" in result
    
    @pytest.mark.asyncio
    async def test_scan_for_viruses_direct(self, document_processor):
        """Test virus scanning method directly"""
        # Create a file with EICAR test string
        suspicious_content = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"

        suspicious_file = UploadFile(
            file=BytesIO(suspicious_content),
            filename="suspicious.txt",
            headers={"content-type": "text/plain"}
        )

        result = await document_processor._scan_for_viruses(suspicious_file)
        assert result["is_safe"] is False
        assert "eicar" in str(result["threats_detected"]).lower()

    @pytest.mark.asyncio
    async def test_process_document_pipeline_virus_detected(self, document_processor):
        """Test pipeline behavior when virus is detected"""
        # Enable virus scanning for this test
        document_processor.virus_scan_enabled = True

        # Create a file with suspicious content
        suspicious_content = b"X5O!P%@AP[4\\PZX554(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"

        suspicious_file = UploadFile(
            file=BytesIO(suspicious_content),
            filename="suspicious.txt",
            headers={"content-type": "text/plain"}
        )

        with pytest.raises(Exception) as exc_info:
            await document_processor.process_document_pipeline(
                file=suspicious_file,
                document_id="doc123",
                organization_id="org456"
            )

        assert "virus" in str(exc_info.value).lower() or "threat" in str(exc_info.value).lower()


class TestDocumentProcessingIntegration:
    """Integration tests for document processing"""
    
    @pytest.mark.asyncio
    async def test_processing_pipeline_performance(self, document_processor, sample_text_file):
        """Test processing pipeline performance"""
        import time
        
        start_time = time.time()
        
        with patch('app.services.document_processor.s3_storage') as mock_s3:
            mock_s3.upload_file_direct = AsyncMock(return_value={
                "file_key": "test/artifact.jpg",
                "file_size": 1024,
                "content_type": "image/jpeg",
                "s3_key": "test/artifact.jpg"
            })
            
            result = await document_processor.process_document_pipeline(
                file=sample_text_file,
                document_id="doc123",
                organization_id="org456"
            )
        
        processing_time = time.time() - start_time
        
        # Processing should complete within reasonable time
        assert processing_time < 10.0  # 10 seconds max
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_multiple_file_processing(self, document_processor):
        """Test processing multiple files concurrently"""
        files = []
        for i in range(3):
            content = f"This is test document {i} with unique content for processing.".encode()
            file_obj = UploadFile(
                file=BytesIO(content),
                filename=f"test_doc_{i}.txt",
                headers={"content-type": "text/plain"}
            )
            files.append(file_obj)
        
        with patch('app.services.document_processor.s3_storage') as mock_s3:
            mock_s3.upload_file_direct = AsyncMock(return_value={
                "file_key": "test/artifact.jpg",
                "file_size": 1024,
                "content_type": "image/jpeg",
                "s3_key": "test/artifact.jpg"
            })
            
            # Process files concurrently
            tasks = [
                document_processor.process_document_pipeline(
                    file=file_obj,
                    document_id=f"doc{i}",
                    organization_id="org456"
                )
                for i, file_obj in enumerate(files)
            ]
            
            results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        for result in results:
            assert result["validation"]["is_valid"] is True
            assert result["virus_scan"]["is_safe"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
