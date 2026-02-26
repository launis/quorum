import asyncio
import instructor
from litellm import acompletion
from pydantic import BaseModel

class UserDetail(BaseModel):
    name: str

async def main():
    client = instructor.from_litellm(acompletion)
    
    # Standard create
    user = await client.chat.completions.create(
        model="gemini/gemini-2.5-flash", 
        messages=[{"role": "user", "content": "Extract Jason is 25"}],
        response_model=UserDetail
    )
    
    print("Parsed Object:", user)
    print("Does it have _raw_response?", hasattr(user, "_raw_response"))
    print("Does it have _meta?", hasattr(user, "_meta"))
    
    # create_with_completion
    user2, raw = await client.chat.completions.create_with_completion(
        model="gemini/gemini-2.5-flash", 
        messages=[{"role": "user", "content": "Extract Jason is 25"}],
        response_model=UserDetail
    )
    
    print("\nRaw Usage:", raw.usage)

if __name__ == "__main__":
    asyncio.run(main())
