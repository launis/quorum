"""Test imports."""

import sys

print(sys.executable)
try:
    import litellm

    print(f"litellm version: {litellm.__version__}")
    # from litellm import cost_per_token # Unused
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Other error: {e}")
