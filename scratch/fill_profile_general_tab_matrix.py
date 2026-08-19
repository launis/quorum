import json

with open("tmp/audit_matrix.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for rule in data["rules"]:
    rid = rule["rule_id"]
    if rid == "sized_box_shrink_ban":
        rule["status"] = "PASS"
        rule["justification"] = "ProfileGeneralTab L23-L25 throws explicit StateError when profile payload is missing instead of returning SizedBox.shrink()."
    elif rid == "horizontal_overflow_prevention":
        rule["status"] = "PASS"
        rule["justification"] = "DropdownButtonFormField L71 sets isExpanded: true and L82, L95 set TextOverflow.ellipsis to prevent RenderFlex overflow."
    elif rid == "freezed_when_ban":
        rule["status"] = "PASS"
        rule["justification"] = "L58 uses Dart 3 native switch (workflowsState) pattern matching expression instead of Freezed .when()."
    elif rid == "no_magic_strings_l10n":
        rule["status"] = "PASS"
        rule["justification"] = "All UI text labels L41, L50, L73, L76, L81, L112, L117, L125, L138 evaluate exclusively via AppLocalizations."
    elif rid == "riverpod_read_vs_watch_ban":
        rule["status"] = "PASS"
        rule["justification"] = "Uses ref.watch L19, L20 inside build() and ref.read L26 inside updatePayload callback."
    elif rid == "english_language_mandate":
        rule["status"] = "PASS"
        rule["justification"] = "File client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart L1-L157 uses 100% English code, comments, and identifiers."
    elif rid == "internal_language_and_epic_ban":
        rule["status"] = "PASS"
        rule["justification"] = "File client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart L1-L157 contains zero Finnish text or occurrences of the banned word 'Epic'."
    else:
        rule["status"] = "NA"
        rule["justification"] = f"Rule '{rid}' is not applicable to tab view widget file client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart."

with open("tmp/audit_matrix.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Updated audit matrix for profile_general_tab.dart successfully.")
