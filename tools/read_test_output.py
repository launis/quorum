try:
    with open("test_output.txt", "r", encoding="utf-16le") as f:
        print(f.read())
except Exception as e:
    # Try utf-8
    try:
        with open("test_output.txt", "r", encoding="utf-8") as f:
            print(f.read())
    except Exception as e2:
        print(f"Error reading: {e}, {e2}")
