import sys
import os
import asyncio
import json
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.knowledge_base_service import KnowledgeBaseService
from backend.services.progress import InMemoryProgressTracker

class MockLLMProvider:
    async def generate(self, prompt, system_instruction=None):
        # Simulate LLM response
        print(f"MockLLM received prompt length: {len(prompt)}")
        return """
        ```json
        {
            "concepts": [
                {
                    "term": "Test Concept",
                    "definition": "A concept found by the Mock LLM."
                },
                {
                    "term": "Another Concept", 
                    "definition": "Another definition."
                }
            ]
        }
        ```
        """

class MockRepo:
    def __init__(self):
        self.items = []
    def add_knowledge_base_item(self, item):
        self.items.append(item)
        print(f"Stored item: {item['type']} - {item.get('term')}")

class MockDocService:
    async def process_knowledge_base_file(self, content, filename, job_id):
        return {"concepts": [], "references": []}

async def run_test():
    print("Initializing components...")
    repo = MockRepo()
    llm = MockLLMProvider()
    doc_service = MockDocService()
    
    service = KnowledgeBaseService(repository=repo, document_service=doc_service, llm_provider=llm)
    
    tracker = InMemoryProgressTracker(callback=lambda x: print(f"Progress: {x}"))
    
    # Simulate a file content
    content = b"This is some dummy text content for the LLM to process."
    filename = "test_doc.txt"
    
    print("Running ingest_from_bytes...")
    # We expect this to trigger the LLM path because llm_provider is set
    result = service.ingest_from_bytes(content, filename, tracker, job_id="test_job")
    
    print("Result:", result)
    
    # Assertions
    concepts = [i for i in repo.items if i['type'] == 'concept']
    print(f"Found {len(concepts)} concepts in repo.")
    
    assert len(concepts) >= 2
    assert concepts[0]['term'] == "Test Concept"
    print("SUCCESS: LLM Ingestion Test Passed.")

if __name__ == "__main__":
    # service.ingest_from_bytes uses asyncio.run internally, 
    # but since we are mocking and the method is synchronous wrapper around async logic?
    # Wait, the method is sync.
    # But inside it calls asyncio.run(). 
    # If we call it from here (sync), it works.
    # BUT we mocked DB/Repo which are sync.
    # We mocked LLM as Async.
    
    # Let's just run it.
    try:
        # KnowledgeBaseService.ingest_from_bytes is a regular method, not async
        repo = MockRepo()
        llm = MockLLMProvider()
        doc_service = MockDocService()
        service = KnowledgeBaseService(repository=repo, document_service=doc_service, llm_provider=llm)
        tracker = InMemoryProgressTracker(callback=lambda x: print(f"Progress: {x}"))
        
        service.ingest_from_bytes(b"dummy", "test.txt", tracker)
        
        concepts = [i for i in repo.items if i['type'] == 'concept']
        if len(concepts) >= 2 and concepts[0]['term'] == "Test Concept":
             print("SUCCESS")
        else:
             print("FAILURE: Concepts not found")
             
    except Exception as e:
        print(f"Test Failed with error: {e}")
        import traceback
        traceback.print_exc()
