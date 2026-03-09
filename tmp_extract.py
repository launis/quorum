import os

filepath = 'mypy_actual.txt'
try:
    with open(filepath, 'r', encoding='utf-16le') as f:
        text = f.read()
except:
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

with open('extracted_errors.txt', 'w', encoding='utf-8') as f_out:
    for line in text.split('\n'):
        if 'error:' in line.lower() or 'unused' in line.lower():
            f_out.write(line + '\n')
