"""Wipe Firestore Executions collection."""

import asyncio
import os

from google.cloud import firestore as google_cloud_firestore

# CONFIG
SERVICE_ACCOUNT_PATH = "service-account.json"
COLLECTION_NAME = "executions"


async def wipe_collection():
    """Deletes all documents in the 'executions' collection."""
    print(f"--- WIPING COLLECTION: {COLLECTION_NAME} ---")

    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"CRITICAL: {SERVICE_ACCOUNT_PATH} not found.")
        return

    # Initialize Async Client directly (like the Repo does)
    db = google_cloud_firestore.AsyncClient.from_service_account_json(SERVICE_ACCOUNT_PATH)

    print(f"Connected to Project: {db.project}")

    # Get all docs
    docs = db.collection(COLLECTION_NAME).stream()

    count = 0
    async for doc in docs:
        print(f"Deleting doc: {doc.id} (Data: {doc.to_dict().get('start_time', '???')})")
        await doc.reference.delete()
        count += 1

    print(f"--- DELETED {count} DOCUMENTS ---")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(wipe_collection())
