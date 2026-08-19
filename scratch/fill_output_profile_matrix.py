import json

with open("tmp/audit_matrix.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for rule in data["rules"]:
    rid = rule["rule_id"]
    if rid == "silent_json_fallbacks":
        rule["status"] = "PASS"
        rule["justification"] = "OutputLayoutBlock L15, SynthesisConfigDTO L52, OutputProfile L70 enforce @JsonSerializable(disallowUnrecognizedKeys: true) forcing instant parsing failure on unknown server keys."
    elif rid == "o1_lists":
        rule["status"] = "PASS"
        rule["justification"] = "OutputLayoutBlock L11, SynthesisConfigDTO L48, OutputProfile L66 use @Freezed(equal: false) to bypass O(N^2) deep equality performance hits on list collections."
    elif rid == "no_raw_string_enum_mappings":
        rule["status"] = "PASS"
        rule["justification"] = "OutputProfile L82-L86, L119 and OutputLayoutBlock L19, L26, L35 enforce strict enum types (DisplayScale, TargetBlockType, PresetView, ScoringStrategy) without raw string mappings."
    elif rid == "sdui_contract_fracture_prevention":
        rule["status"] = "PASS"
        rule["justification"] = "OutputProfile L70-L123 fields match Python backend OutputProfileResponseDTO 1:1 using camelCase to snake_case @JsonKey annotations."
    elif rid == "universal_fail_fast":
        rule["status"] = "PASS"
        rule["justification"] = "Mandatory fields id L72, workflowId L74, name L76 are typed required, causing immediate Freezed parsing exception if null/missing from API."
    elif rid == "english_language_mandate":
        rule["status"] = "PASS"
        rule["justification"] = "File client_app_v2/lib/features/studio/models/output_profile.dart L1-L128 uses 100% English code, comments, and annotations."
    elif rid == "internal_language_and_epic_ban":
        rule["status"] = "PASS"
        rule["justification"] = "File client_app_v2/lib/features/studio/models/output_profile.dart L1-L128 contains zero Finnish text or occurrences of the banned word 'Epic'."
    else:
        rule["status"] = "NA"
        rule["justification"] = f"Rule '{rid}' is not applicable to model definition file client_app_v2/lib/features/studio/models/output_profile.dart."

with open("tmp/audit_matrix.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Updated audit matrix for output_profile.dart successfully.")
