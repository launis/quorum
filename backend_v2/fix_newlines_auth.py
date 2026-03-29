try:
    with open("backend_v2/services/auth.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Universal newline fix for weird carriage return issues
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    with open("backend_v2/services/auth.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("Fixed newlines in auth.py")
except Exception as e:
    print(e)
