
import sys
import os
sys.path.append(os.getcwd())

print("Attempting to import backend.models.domain...")
try:
    import backend.models.domain
    print("✅ backend.models.domain imported.")
except ImportError as e:
    print(f"❌ backend.models.domain failed: {e}")

print("Attempting to import backend.agents.judge...")
try:
    import backend.agents.judge
    print("✅ backend.agents.judge imported.")
except ImportError as e:
    print(f"❌ backend.agents.judge failed: {e}")

print("Attempting to import backend.tasks.analysis...")
try:
    import backend.tasks.analysis
    print("✅ backend.tasks.analysis imported.")
except ImportError as e:
    print(f"❌ backend.tasks.analysis failed: {e}")
