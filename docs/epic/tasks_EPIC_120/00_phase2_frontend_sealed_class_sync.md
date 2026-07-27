# Phase 2: Frontend Freezed Sealed Class Synchronization

This plan synchronizes the Flutter `SduiBlockDTO` sealed class with the backend's `AnySduiBlock` discriminated union by adding the missing 4 types, extracting it to a shared layer, and typing the `contentBlocks` and `synthesisBlocks` fields.

**Target Files**:
- `@[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart]` [NEW]
- `@[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart]` [MODIFY]
- `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_layout_dto.dart]` [MODIFY]
- `@[c:\src\quorum\client_app_v2\test\shared\models\sdui_block_dto_test.dart]` [NEW]

```xml
<execution_protocol level="2_execute">
  <constraint invariant="sdui_contract_fracture_prevention">Enforce Cross-Domain DTO Parity between Python AnySduiBlock and Dart SduiBlockDTO.</constraint>
  <constraint invariant="the_zero_compromise_pledge">Do not use fallbackUnion in Freezed. Missing data or bad types must crash the Freezed parser natively.</constraint>
  <step id="1" name="Extract SduiBlockDTO to Shared Layer">
    <action>Create `@[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart]`.</action>
    <action>Move the existing `SduiBlockDTO` sealed class from `output_profile.dart` into this new file, using `@Freezed(unionKey: 'block_type')`.</action>
    <action>Add the 4 missing types from Python's AnySduiBlock: `quote_card`, `warning_card`, `n_a_card`, and `grid`, matching the Python schema exactly.</action>
  </step>
  <step id="2" name="Rewire Studio Imports">
    <action>Modify `@[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart]`.</action>
    <demolish>REMOVE: Existing inline `SduiBlockDTO` sealed class definition and its subclasses.</demolish>
    <demolish>REMOVE: `List<dynamic> contentBlocks` in both OutputProfile and EmbeddedOutputProfile.</demolish>
    <action>Import `../../../shared/models/sdui_block_dto.dart`.</action>
    <action>Replace `List<dynamic> contentBlocks` with `@Default([]) List<SduiBlockDTO> contentBlocks`.</action>
  </step>
  <step id="3" name="Rewire Execution Imports">
    <action>Modify `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_layout_dto.dart]`.</action>
    <demolish>REMOVE: `List<Map<String, dynamic>>? synthesisBlocks`.</demolish>
    <action>Import `../../../shared/models/sdui_block_dto.dart`.</action>
    <action>Replace with `List<SduiBlockDTO>? synthesisBlocks` (PRESERVE nullable ?).</action>
  </step>
  <step id="4" name="Strict Deserialization Testing">
    <action>Create `@[c:\src\quorum\client_app_v2\test\shared\models\sdui_block_dto_test.dart]`.</action>
    <action>Write Unit Tests verifying `SduiBlockDTO.fromJson` for all 9 block types.</action>
    <action>Write negative Unit Tests verifying unknown block types explicitly crash.</action>
  </step>
</execution_protocol>
```
## Testing & Quality Gate Plan
- Unit tests: `dart test test/shared/models/sdui_block_dto_test.dart`
- Run global flutter audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`
