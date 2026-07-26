import glob
import os
import subprocess

# Ensure scratch directory exists
os.makedirs(r"C:\Users\risto\.gemini\antigravity-ide\brain\bb87cf3e-0f31-4b3f-85eb-6bb2bbfe5d5d\scratch", exist_ok=True)

workflows_dir = r"c:\src\quorum\.agents\workflows"
output_file = r"C:\Users\risto\.gemini\antigravity-ide\brain\bb87cf3e-0f31-4b3f-85eb-6bb2bbfe5d5d\scratch\legacy_workflows_dump.txt"

files = glob.glob(os.path.join(workflows_dir, "*.md"))

with open(output_file, "w", encoding="utf-8") as out:
    for file_path in files:
        file_name = os.path.basename(file_path)
        # get legacy content
        try:
            legacy = subprocess.check_output(
                ["git", "show", f"2014e69b:.agents/workflows/{file_name}"],
                cwd=r"c:\src\quorum",
                stderr=subprocess.DEVNULL,
            ).decode("utf-8")
        except subprocess.CalledProcessError:
            legacy = "FILE DID NOT EXIST IN 2014e69b\n"

        out.write("========================================\n")
        out.write(f"FILE: {file_name}\n")
        out.write("========================================\n")
        out.write(legacy)
        out.write("\n\n")

print(f"Dumped to {output_file}")
