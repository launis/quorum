
def clean():
    with open("pytest_output.txt", "rb") as f:
        data = f.read()
    text = data.decode("utf-8", errors="ignore")
    with open("pytest_clean.txt", "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    clean()
