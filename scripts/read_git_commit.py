import subprocess

def run():
    print("Luetaan input_processing.py vanhasta commitista bfe410c...")
    result = subprocess.run(
        ["git", "show", "bfe410c507eddbdb818df5afcc1cff659c6d2e4e:backend_v2/hooks/input_processing.py"],
        capture_output=True, text=True, encoding='utf-8', errors='ignore'
    )
    if result.returncode != 0:
        print("Git-komento epäonnistui:", result.stderr)
        return
        
    lines = result.stdout.splitlines()
    for i, line in enumerate(lines):
        if "content_base64" in line or "resolve_input" in line:
            start = max(0, i - 5)
            end = min(len(lines), i + 20)
            print("======== LÖYTYI ======== ")
            for j in range(start, end):
                print(f"{j+1}: {lines[j]}")
            break

if __name__ == "__main__":
    run()
