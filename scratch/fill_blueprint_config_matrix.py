import json

with open("tmp/audit_matrix.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for rule in data["rules"]:
    rid = rule["rule_id"]
    if rid == "silent_json_fallbacks":
        rule["status"] = "PASS"
        rule["justification"] = "BlueprintConfig L14 enforces @JsonSerializable(disallowUnrecognizedKeys: true) forcing instant parsing failure on unknown server keys."
    elif rid == "o1_lists":
        rule["status"] = "PASS"
        rule["justification"] = "BlueprintConfig L10 uses @Freezed(equal: false) to bypass O(N^2) deep equality performance hits."
    elif rid == "no_raw_string_enum_mappings":
        rule["status"] = "PASS"
        rule["justification"] = "BlueprintConfig L18 enforces strict PresetView enum mapping without raw string literals or unknownEnumValue fallback."
    elif rid == "universal_fail_fast":
        rule["status"] = "PASS"
        rule["justification"] = "BlueprintConfig L17 PresetView.metrics1d default uses strongly typed enum member rather than loose string defaults."
    elif rid == "english_language_mandate":
        rule["status"] = "PASS"
        rule["justification"] = "File client_app_v2/lib/features/studio/models/blueprint_config.dart L1-L24 uses 100% English code, comments, and annotations."
    elif rid == "internal_language_and_epic_ban":
        rule["status"] = "PASS"
        rule["justification"] = "File client_app_v2/lib/features/studio/models/blueprint_config.dart L1-L24 contains zero Finnish text or occurrences of the banned word 'Epic'."
    else:
        rule["status"] = "NA"
        rule["justification"] = f"Rule '{rid}' is not applicable to model definition file client_app_v2/lib/features/studio/models/blueprint_config.dart."

with open("tmp/audit_matrix.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Updated audit matrix for blueprint_config.dart successfully.")
