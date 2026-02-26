import asyncio
import os
import instructor
from litellm import acompletion
from pydantic import BaseModel

class UserDetail(BaseModel):
    name: str

async def main():
    os.environ["LITELLM_LOG"] = "DEBUG"
    os.environ["VERTEX_PROJECT"] = "quorum"
    os.environ["VERTEX_LOCATION"] = "europe-north1"
    
    # We will simulate a large payload just to be sure, but let's test a simple one first
    client = instructor.from_litellm(acompletion)
    
    print("Testing standard create...")
    user = await client.chat.completions.create(
        model="vertex_ai/gemini-2.5-flash", 
        messages=[{"role": "user", "content": "Extract Jason is 25"}],
        response_model=UserDetail
    )
    
    print("Parsed Object:", user)
    print("Does it have _raw_response?", hasattr(user, "_raw_response"))
    print("Does it have _meta?", hasattr(user, "_meta"))
    
    try:
        print("\nTesting create_with_completion...")
        user2, raw = await client.chat.completions.create_with_completion(
            model="vertex_ai/gemini-2.5-flash", 
            messages=[{"role": "user", "content": "Extract Jason is 25"}],
            response_model=UserDetail
        )
        print("Raw Usage:", raw.usage)
    except Exception as e:
        print(f"Error with create_with_completion: {e}")

if __name__ == "__main__":
    asyncio.run(main())
