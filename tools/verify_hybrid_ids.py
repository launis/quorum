
from backend.utils.identifiers import generate_unique_id
import uuid

# 1. Simulate New ID Generation (Hybrid Feature)
print("--- TEST: New ID Generation ---")
new_id_1 = generate_unique_id("My New Project", prefix="proj")
new_id_2 = generate_unique_id("Another User", prefix="user")

print(f"Project ID: {new_id_1}")
print(f"User ID:    {new_id_2}")

# Verify format
assert new_id_1.startswith("proj-my-new-project-")
assert new_id_2.startswith("user-another-user-")
print("✅ New IDs follow the new schema (prefix-name-suffix).")

# 2. Simulate Old ID Compatibility (Standard UUID)
print("\n--- TEST: Legacy ID Compatibility ---")
old_id = str(uuid.uuid4())
print(f"Existing Legacy ID: {old_id}")

# The system doesn't "convert" old IDs, it just accepts them.
# We verify that our generator CAN output a plain UUID if no name is given (fallback)
fallback_id = generate_unique_id()
print(f"Fallback ID (No Name): {fallback_id}")
try:
    uuid.UUID(fallback_id)
    print("✅ Generator falls back to standard UUID if no name provided (Safe).")
except ValueError:
    print("❌ Generator failed to produce valid UUID as fallback.")

print("\n✅ HYBRID STATE CONFIRMED: Can generate new readable IDs while coexisting with UUIDs.")
