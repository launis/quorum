import re
import os

print("| Tiedosto | N (Atomit) | Self-Consistency | Fleissin Kappa | Shannonin Entropia | Erimielisyydet |")
print("| :--- | :---: | :---: | :---: | :---: | :---: |")

for idx in range(10, 20):
    filename = f"mismatch_traces_raw {idx}.md"
    path = os.path.join("scratch", filename)
    if not os.path.exists(path):
        continue
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    n_match = re.search(r"Yhteisten arvioitujen atomien määrä \(\$N\$\):?\*\*?\s*(\d+)", content)
    consistency_match = re.search(r"Parittainen konsistenssi \([a-zA-Z- ]+\):?\*\*?\s*([\d.]+\s*%)", content)
    kappa_match = re.search(r"Fleissin Kappa \(\$\\kappa(?:_\{Fleiss\})?\$\):?\*\*?\s*([\d.-]+)", content)
    entropy_match = re.search(r"Shannonin Entropia:?\*\*?\s*([\d.-]+)", content)
    mismatch_match = re.search(r"Erimielisyyttä näiden välillä:?\*\*?\s*(\d+)", content)
    
    n = n_match.group(1) if n_match else "N/A"
    consistency = consistency_match.group(1) if consistency_match else "N/A"
    kappa = kappa_match.group(1) if kappa_match else "N/A"
    entropy = entropy_match.group(1) if entropy_match else "N/A"
    mismatches = mismatch_match.group(1) if mismatch_match else "N/A"
    
    print(f"| {filename} | {n} | {consistency} | {kappa} | {entropy} | {mismatches} |")
