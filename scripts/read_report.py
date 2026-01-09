import os

LOG_PATH = "tests/output/round15_final.txt"


def read_log():
    if not os.path.exists(LOG_PATH):
        print("Log file not found.")
        return

    try:
        # Try UTF-16LE first as indicated by previous error
        with open(LOG_PATH, encoding="utf-16-le") as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"Error reading with utf-16-le: {e}")
        try:
            # Fallback to defaults
            with open(LOG_PATH, encoding="utf-8", errors="ignore") as f:
                print(f.read())
        except Exception as e2:
            print(f"Error reading with fallback: {e2}")


if __name__ == "__main__":
    read_log()
