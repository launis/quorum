import asyncio
import json
import asyncpg
import os

async def main():
    # Database URL
    db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/quorum")
    
    conn = await asyncpg.connect(db_url)
    row = await conn.fetchrow(
        "SELECT profile_syntheses FROM executions WHERE id = $1", 
        "exe_99086245d3af448f872c408f9dd7445a"
    )
    if not row:
        print("Execution not found")
        await conn.close()
        return
        
    syntheses = json.loads(row['profile_syntheses']) if isinstance(row['profile_syntheses'], str) else row['profile_syntheses']
    
    for pid, cache in syntheses.items():
        print(f"--- Profile: {pid} ---")
        cb = cache.get("content_blocks", [])
        print(f"content_blocks count: {len(cb)}")
        for i, b in enumerate(cb):
            text = str(b.get("text", ""))
            print(f"  [{i}] {b.get('block_type')}: {text[:60]}...")
            
        md = cache.get("synthesized_markdown", "")
        print(f"\nsynthesized_markdown length: {len(md)}")
        print(f"snippet:\n{md[:200]}...")
        
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
