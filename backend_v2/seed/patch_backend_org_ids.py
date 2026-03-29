import os

# Yksilöidyt korvaukset tarkalla syntaksilla virheiden (kuten LLM system-roolin korvaamisen) välttämiseksi
files_to_patch = {
    r"c:\src\quorum\backend_v2\services\auth.py": [
        ('target_org_id != "system"', 'target_org_id != "org_system000000"'),
        ('target_org_id == "system"', 'target_org_id == "org_system000000"'),
        ('target_org_id = "system"  # Redundant', 'target_org_id = "org_system000000"  # Redundant'),
        ('root.organization_id != "system"', 'root.organization_id != "org_system000000"'),
    ],
    r"c:\src\quorum\backend_v2\services\execution.py": [
        ('organization_id not in [org_id, "system", None]', 'organization_id not in [org_id, "org_system000000", None]'),
    ],
    r"c:\src\quorum\backend_v2\services\usage_service.py": [
        ('upsert_usage_aggregate("system"', 'upsert_usage_aggregate("org_system000000"'),
    ],
    r"c:\src\quorum\backend_v2\database\repository.py": [
        ('in [target, "system"]', 'in [target, "org_system000000"]'),
        ('Filter("organization_id", "in", [organization_id, "system"])', 'Filter("organization_id", "in", [organization_id, "org_system000000"])'),
    ]
}

def main():
    modifications = 0
    for filepath, replacements in files_to_patch.items():
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            for old, new in replacements:
                content = content.replace(old, new)
                
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Päivitetty hardkoodatut viittaukset: {filepath}")
                modifications += 1
                
    print(f"\nKorjaus valmis. {modifications} backend-tiedostoa puskettiin Opaque ID -aikaan.")

if __name__ == "__main__":
    main()
