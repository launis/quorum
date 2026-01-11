"""Verify Firebase Storage Connection."""
import logging
import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_storage")


def verify_storage():
    """Verifies that the Firebase Storage bucket is accessible."""
    # HARDCODED TEST to bypass env var confusion
    TARGET_BUCKET = "cognitive-quorum.firebasestorage.app"
    print(f"[INFO] Testing connection to SPECIFIC BUCKET: {TARGET_BUCKET}")

    settings = get_settings()

    # Check/Initialize Firebase
    import firebase_admin
    from firebase_admin import credentials, storage

    if not firebase_admin._apps:
        # Mimic wrapper.py logic
        root_dir = os.path.dirname(settings.base_dir)
        sa_path = os.path.join(root_dir, "service-account.json")

        if os.path.exists(sa_path):
            print(f"[INFO] Initializing Firebase with {sa_path}")
            cred = credentials.Certificate(sa_path)
            firebase_admin.initialize_app(cred)
        else:
            print(f"[ERROR] Service Account not found at {sa_path}")
            return

    try:
        # Get specific bucket
        bucket = storage.bucket(name=TARGET_BUCKET)
        print(f"[INFO] Bucket Object retrieved for: {bucket.name}")

        if not bucket.exists():
            print(f"[ERROR] Bucket '{bucket.name}' does not appear to exist (404) or permission denied (403)!")
            return

        # Test Write
        test_blob_name = "verification_test.txt"
        blob = bucket.blob(test_blob_name)
        blob.upload_from_string("This is a test file from Agentic Coding to verify Cloud Storage.")
        print(f"[SUCCESS] Wrote test file to: gs://{bucket.name}/{test_blob_name}")

        # Test Read
        content = blob.download_as_text()
        if "Agentic Coding" in content:
            print("[SUCCESS] Read verification passed.")
        else:
            print("[ERROR] Read content mismatch.")

        # Cleanup
        blob.delete()
        print("[INFO] Cleaned up test file.")

        print("\n[CONCLUSION] Firebase Cloud Storage connection is VERIFIED and WORKING.")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Storage verification failed: {e}")


if __name__ == "__main__":
    verify_storage()
