with open(r'c:\src\quorum\backend_debug.log', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'exe_fcf075277344441fa67e60634b1c548b' in line or 'Cache Hit' in line:
        print(line.strip())
