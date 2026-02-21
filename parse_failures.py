import sys

text = open('test_results.txt', 'r', encoding='utf-16le').read()
parts = text.split('=================================== FAILURES ===================================')
if len(parts) > 1:
    failures_section = parts[1].split('=========================== short test summary info ============================')[0]
    out = open('failures.txt', 'w', encoding='utf-8')
    out.write(failures_section)
    out.close()
    print("Wrote to failures.txt")
else:
    print("No failures section found.")
