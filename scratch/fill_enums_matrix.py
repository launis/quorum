import json

with open("tmp/audit_matrix.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for rule in data["rules"]:
    rid = rule["rule_id"]
    if rid == "centralized_frontend_enums":
        rule["status"] = "PASS"
        rule["justification"] = "File client_app_v2/lib/core/models/enums.dart L8-L22 centralizes SystemConcurrency and L376-L384 centralizes SystemUiConstraints with strict value getters."
    elif rid == "no_raw_string_enum_mappings":
        rule["status"] = "PASS"
        rule["justification"] = "Enums L25-L54 (XaiExtensionType), L58-L72 (PresetView), L366-L373 (DisplayScale), and L388-L415 (TargetBlockType) use explicit @JsonEnum() and @JsonValue() string mappings without raw string literals."
    elif rid == "silent_json_fallbacks":
        rule["status"] = "PASS"
        rule["justification"] = "All enums in L4-L416 omit unknownEnumValue fallback properties, forcing instant JSON deserialization failure when unrecognized strings are received."
    elif rid == "universal_fail_fast":
        rule["status"] = "PASS"
        rule["justification"] = "StrictnessLevelExtension.fromInt L140-L145 and XaiExtensionTypeValue.backendValue L189-L222 enforce exact value mapping without silent empty string defaults."
    elif rid == "dropdown_database_alignment":
        rule["status"] = "PASS"
        rule["justification"] = "PromptBlockCategoryGroups L167-L187 defines explicit category grouping lists matching backend database schemas for dropdown filtering."
    elif rid == "english_language_mandate":
        rule["status"] = "PASS"
        rule["justification"] = "File client_app_v2/lib/core/models/enums.dart L1-L416 contains 100% English docstrings, inline comments, class names, and enum members."
    elif rid == "internal_language_and_epic_ban":
        rule["status"] = "PASS"
        rule["justification"] = "File client_app_v2/lib/core/models/enums.dart L1-L416 contains zero Finnish strings or references to the banned term 'Epic'."
    else:
        rule["status"] = "NA"
        rule["justification"] = f"Rule '{rid}' is not applicable to model/enum definition file client_app_v2/lib/core/models/enums.dart."

with open("tmp/audit_matrix.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Updated tmp/audit_matrix.json successfully.")
