import 'package:freezed_annotation/freezed_annotation.dart';

part 'frozen_context_snapshot.freezed.dart';
part 'frozen_context_snapshot.g.dart';

/// Strongly typed frozen context snapshot with multi-payload parity (SSOT).
@Freezed(equal: false)
abstract class FrozenContextSnapshot with _$FrozenContextSnapshot {
  const FrozenContextSnapshot._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory FrozenContextSnapshot({
    @JsonKey(name: 'version_id') String? versionId,
    @JsonKey(name: 'workflow_id') String? workflowId,
    @JsonKey(name: 'workflow_name') String? workflowName,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @JsonKey(name: 'created_at') String? createdAt,
    @JsonKey(name: 'compiled_prompts')
    @Default({})
    Map<String, String> compiledPrompts,
    @JsonKey(name: 'injected_theory')
    @Default({})
    Map<String, Object?> injectedTheory,
    @JsonKey(name: 'generated_schemas')
    @Default({})
    Map<String, Object?> generatedSchemas,
    @JsonKey(name: 'ui_hints_snapshot')
    @Default({})
    Map<String, Object?> uiHintsSnapshot,
    @JsonKey(name: 'mcp_tool_audit')
    @Default([])
    List<Map<String, Object?>> mcpToolAudit,
  }) = _FrozenContextSnapshot;

  /// Instantiates a strictly typed [FrozenContextSnapshot] from raw JSON.
  factory FrozenContextSnapshot.fromJson(Map<String, dynamic> json) =>
      _$FrozenContextSnapshotFromJson(json);
}
