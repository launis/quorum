import asyncio
import os
import litellm
from litellm import Router

async def main():
    model_config = {
        "model_name": "vertex_ai/gemini-2.5-flash",
        "litellm_params": {
            "model": "vertex_ai/gemini-2.5-flash",
            # Invalid API key to trigger immediate error or Rate Limit simulator
            "api_key": "fake_key",
        },
    }
    
    router = Router(
        model_list=[model_config],
        num_retries=0,
    )
    
    print("Sending first request...")
    try:
        await router.acompletion(
            model="vertex_ai/gemini-2.5-flash", 
            messages=[{"role": "user", "content": "hello"}],
            mock_response="RateLimitError",
        )
    except Exception as e:
        print(f"First request raised: {type(e).__name__} - {e}")
        
    print("Sending second request...")
    try:
        # Will this hang?
        task = asyncio.create_task(router.acompletion(
            model="vertex_ai/gemini-2.5-flash", 
            messages=[{"role": "user", "content": "hello"}],
            # If mock_response is not supported by router, we can at least observe the fallback mechanic
        ))
        
        # Wait 5 seconds, if not done, it's hanging
        done, pending = await asyncio.wait([task], timeout=5.0)
        if pending:
            print("Second request HANGING indefinitely!")
            task.cancel()
        else:
            print(f"Second request finished with: {done.pop().exception()}")
    except Exception as e:
        print(f"Second request raised: {type(e).__name__} - {e}")

if __name__ == "__main__":
    asyncio.run(main())
