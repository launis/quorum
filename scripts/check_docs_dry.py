import os
import re

def check_docs_dry_violations(docs_dir="c:/src/quorum/docs"):
    violations = {}
    
    # Patterns that we explicitly removed or migrated to specific places.
    # We want to make sure they aren't lingering in other files.
    patterns = {
        "ChangeNotifier_or_StateProvider": r"(?i)\bChangeNotifier\b|\bStateProvider\b",
        "try_except_pass": r"(?i)try-except\s+pass",
        "dict_passing_banned": r"(?i)\bdict\b\s+outputs?|\bdictionary\b\s+outputs?",
        "RFC_7807": r"(?i)RFC\s*7807",
        "Fail_Fast": r"(?i)Fail\s*Fast",
        "SSOT": r"(?i)SSOT|Single\s*Source\s*of\s*Truth",
        "Riverpod_3": r"(?i)Riverpod\s*3",
        "Optimistic_Update": r"(?i)Optimistic\s*Update",
        "Matrix_Approach": r"(?i)Matrix\s*Approach"
    }
    
    # Files we already updated and know are correct. We skip scanning them for "good" terms, 
    # but might scan them for "bad" terms just in case.
    updated_files = [
        "architecture.md", 
        "STRICT MANDATES & ARCHITECTURE PRINCIPLES.md",
        "STRICT FRONTEND MANDATES & ARCHITECTURE PRINCIPLES.md",
        "data_management.md",
        "flutterpromptohje.md",
        "index.md",
        "alku.md"
    ]
    
    for filename in os.listdir(docs_dir):
        if not filename.endswith(".md"):
            continue
            
        filepath = os.path.join(docs_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        file_violations = []
        for pat_name, pat_regex in patterns.items():
            matches = re.finditer(pat_regex, content)
            count = sum(1 for _ in matches)
            if count > 0:
                # If it's a file we DIDN'T update, but it mentions a core concept, it might be a DRY violation
                if filename not in updated_files:
                     file_violations.append(f"Found {count} instances of '{pat_name}'")
                     
        if file_violations:
            violations[filename] = file_violations
            
    if violations:
        print("Potential DRY Violations Found in Un-updated Files:")
        for filename, vils in violations.items():
            print(f"- {filename}:")
            for v in vils:
                print(f"  * {v}")
    else:
        print("No obvious DRY violations found in the remaining documentation files.")

if __name__ == "__main__":
    check_docs_dry_violations()
