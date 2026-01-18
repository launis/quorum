
import codecs
import os
import sys

src = r"c:\src\quorum\backend\debug_output_real.txt"
dst = r"c:\src\quorum\backend\debug_output_real_utf8.txt"

if not os.path.exists(src):
    print(f"Source file not found: {src}")
    sys.exit(1)

try:
    with codecs.open(src, "r", "utf-16") as f_in:
        content = f_in.read()
        with codecs.open(dst, "w", "utf-8") as f_out:
            f_out.write(content)
    print("Conversion successful.")
except Exception as e:
    print(f"Conversion failed: {e}")
