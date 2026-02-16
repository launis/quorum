
try:
    with open('verify_output.txt', encoding='utf-16-le') as f:
        print(f.read())
except Exception as e:
    print(f"Error reading utf-16-le: {e}")
    try:
        with open('verify_output.txt', encoding='mbcs') as f:
            print(f.read())
    except Exception as e2:
        print(f"Error reading mbcs: {e2}")
