import pytest
from services.ingestion.processor import TextProcessor, ImageProcessor

def test_text_processor(tmp_path):
    d = tmp_path / "test.txt"
    d.write_text("This is a test. " * 100)
    processor = TextProcessor()
    chunks = processor.process(str(d))
    assert len(chunks) > 0
    assert isinstance(chunks[0], dict)
    assert "content" in chunks[0]

def test_image_processor(tmp_path):
    d = tmp_path / "test.png"
    d.write_bytes(b"fake_image_bytes")
    processor = ImageProcessor()
    result = processor.process(str(d))
    assert isinstance(result, list)
    assert len(result) == 1
    assert "metadata" in result[0]

def test_storage_service_mock(mock_s3):
    from services.storage import StorageService
    # Mocking boto3 client inside StorageService if possible or just the service method
    service = StorageService(tenant_id="tenant1")
    service.s3 = mock_s3
    
    # Mocking upload_file
    mock_s3.put_object.return_value = {}
    
    url = service.upload_file(b"content", "test.txt")
    assert "test.txt" in url
    assert "tenant1" in url
