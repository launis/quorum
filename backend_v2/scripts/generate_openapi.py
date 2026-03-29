import json
import os
import sys

# Ensure the root quorum directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend_v2.main import app


def main() -> None:
    print("Generating OpenAPI schema from FastAPI app...")
    openapi_schema = app.openapi()

    output_dir = os.path.join(root_dir, "docs", "swagger")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "openapi.json")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
            f.write("\n")  # Add trailing newline standard
        print(f"SUCCESS: TS / Dart Client schemas - OpenAPI JSON generated and saved to {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to write OpenAPI file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
