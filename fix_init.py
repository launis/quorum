import glob
import os

for f in glob.glob('backend_v2/tests/**/__init__.py', recursive=True):
    with open(f, 'w') as file:
        file.write('\"\"\"Unit tests.\"\"\"\n')
