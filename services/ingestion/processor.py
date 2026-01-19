from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseProcessor(ABC):
    @abstractmethod
    def process(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a file and return a list of content chunks with metadata."""
        pass

class TextProcessor(BaseProcessor):
    def process(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Simple chunking for now
        chunk_size = 1000
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        
        return [{"content": chunk, "metadata": {"type": "text"}} for chunk in chunks]

class ImageProcessor(BaseProcessor):
    def process(self, file_path: str) -> List[Dict[str, Any]]:
        # Placeholder for OCR/Captioning
        return [{"content": "Image content placeholder (OCR needed)", "metadata": {"type": "image"}}]
