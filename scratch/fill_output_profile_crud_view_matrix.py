import json

with open("tmp/audit_matrix.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for rule in data["rules"]:
    rid = rule["rule_id"]
    if rid == "freezed_when_ban":
        rule["status"] = "PASS"
        rule["justification"] = "OutputProfileCrudView L28 uses Dart 3 native switch (formState) expression pattern matching destructuring instead of Freezed .when()."
    elif rid == "monolithic_god_widgets":
        rule["status"] = "PASS"
        rule["justification"] = "OutputProfileCrudView is a 201-line dumb shell delegating layout tabs to ProfileGeneralTab L90, ProfileScoringTab L91, and ProfileLayoutsTab L92."
    elif rid == "async_build_context_mounted_ban":
        rule["status"] = "PASS"
        rule["justification"] = "Methods _saveProfile L125, L134 and _deleteProfile L188 enforce if (!context.mounted) return; after every asynchronous gap."
    elif rid == "riverpod_read_vs_watch_ban":
        rule["status"] = "PASS"
        rule["justification"] = "Uses ref.watch L26 inside build() and ref.read L122, L136, L186 exclusively inside event callbacks."
    elif rid == "the_no_pass_rule":
        rule["status"] = "PASS"
        rule["justification"] = "Exception blocks L133-L144 and L189-L197 log errors via loggerServiceProvider and present error feedback via ScaffoldMessenger snackbars."
    elif rid == "sized_box_shrink_ban":
        rule["status"] = "PASS"
        rule["justification"] = "Uses AppExceptionBoundary L44 and ErrorView L35 without SizedBox.shrink() fallbacks."
    elif rid == "no_magic_strings_l10n":
        rule["status"] = "PASS"
        rule["justification"] = "All UI labels L30, L34, L47, L50-L52, L75, L81, L165, L170, L177 evaluate exclusively via AppLocalizations."
    elif rid == "english_language_mandate":
        rule["status"] = "PASS"
        rule["justification"] = "File client_app_v2/lib/features/studio/views/output_profile_crud_view.dart L1-L201 uses 100% English code, comments, and identifiers."
    elif rid == "internal_language_and_epic_ban":
        rule["status"] = "PASS"
        rule["justification"] = "File client_app_v2/lib/features/studio/views/output_profile_crud_view.dart L1-L201 contains zero Finnish text or occurrences of the banned word 'Epic'."
    else:
        rule["status"] = "NA"
        rule["justification"] = f"Rule '{rid}' is not applicable to view file client_app_v2/lib/features/studio/views/output_profile_crud_view.dart."

with open("tmp/audit_matrix.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Updated audit matrix for output_profile_crud_view.dart successfully.")
