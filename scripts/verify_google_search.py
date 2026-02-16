
import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv(override=True)

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("❌ ERROR: 'google-api-python-client' not installed.")
    print("   Run: uv pip install google-api-python-client")
    sys.exit(1)

def verify_search():
    print("🔍 Google Custom Search Verification Tool")
    print("---------------------------------------")

    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_CX")

    if not api_key:
        print("❌ ERROR: GOOGLE_SEARCH_API_KEY is missing in .env")
        return
    if not cx:
        print("❌ ERROR: GOOGLE_SEARCH_CX is missing in .env")
        return

    print(f"✅ Credentials found.")
    print(f"   API Key: {api_key[:5]}...{api_key[-5:]}")
    print(f"   CX ID:   {cx}")
    print("\nAttempting test query 'test'...")

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q="test", cx=cx, num=1).execute()
        
        items = res.get("items", [])
        if items:
            print("✅ SUCCESS: Search returned results.")
            print(f"   Title: {items[0].get('title')}")
            print(f"   Link:  {items[0].get('link')}")
        else:
            print("⚠️ WARNING: Search executed but returned no results (Zero Results).")
            print("   This usually means the API works but the CSE is restricted to specific sites.")
            
    except HttpError as e:
        print("\n❌ API ERROR (Check google_search_debug.log)")
        with open("google_search_debug.log", "w", encoding="utf-8") as f:
             f.write(f"Status: {e.resp.status}\n")
             f.write(f"Content: {e.content.decode('utf-8')}\n")
             
        reason = str(e)
        if e.resp.status == 403:
            import re
            match = re.search(r'project (\d+)', reason)
            if match:
                print(f"   🆔 PROJECT ID in Error: {match.group(1)}")
                
            if "Custom Search JSON API" in reason:
                print("   🔴 CAUSE: Custom Search JSON API is NOT ENABLED in Google Cloud Console.")
                print("   👉 ACTION: Go to Cloud Console > APIs & Services > Enable 'Custom Search JSON API'.")
            elif "project" in reason.lower():
                print("   🔴 CAUSE: API Key belongs to a project without the API enabled.")
            else:
                print(f"   Reason: {reason}")
        else:
            print(f"   Reason: {reason}")

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    verify_search()
