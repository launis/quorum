with open("test_output_2.txt", "r", encoding="utf-16") as f:
    content = f.read()
with open("test_output_utf8_2.txt", "w", encoding="utf-8") as f:
    f.write(content)
