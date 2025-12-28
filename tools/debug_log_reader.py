
import sys

def search_log():
    # Use the specific target string we're interested in
    # target = "Running step: JudgeAgent (Step ID: step_judge_cognitive)"
    # Actually, let's search for "step_judge_cognitive" generally to capture updates too
    target = "step_judge_cognitive"
    found = False
    count = 0
    output = []
    
    # We want to catch the LAST occurrence if there are multiple runs, 
    # but the log might be huge.
    # Let's read the whole file, identify the LAST start of the execution containing this step.
    
    # Simpler approach: capturing all occurrences of 'step_judge_cognitive' and ~10 lines after each context matches
    
def read_last_lines(filepath, n=500):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_lines = lines[-n:]
            
            with open("debug_result.txt", "w", encoding="utf-8") as out:
                for line in last_lines:
                    out.write(line)
        print(f"Wrote last {n} lines to debug_result.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    LOG_FILE = r"c:\Users\risto\OneDrive\quorum\backend_debug.log"
    read_last_lines(LOG_FILE, 1000)
