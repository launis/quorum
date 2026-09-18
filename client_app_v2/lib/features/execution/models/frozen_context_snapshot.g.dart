// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'frozen_context_snapshot.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_FrozenContextSnapshot _$FrozenContextSnapshotFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_FrozenContextSnapshot',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'version_id',
        'workflow_id',
        'workflow_name',
        'organization_id',
        'user_id',
        'created_at',
        'compiled_prompts',
        'injected_theory',
        'generated_schemas',
        'ui_hints_snapshot',
        'mcp_tool_audit',
      ],
    );
    final val = _FrozenContextSnapshot(
      versionId: $checkedConvert('version_id', (v) => v as String?),
      workflowId: $checkedConvert('workflow_id', (v) => v as String?),
      workflowName: $checkedConvert('workflow_name', (v) => v as String?),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      userId: $checkedConvert('user_id', (v) => v as String?),
      createdAt: $checkedConvert('created_at', (v) => v as String?),
      compiledPrompts: $checkedConvert(
        'compiled_prompts',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as String),
            ) ??
            const {},
      ),
      injectedTheory: $checkedConvert(
        'injected_theory',
        (v) => v as Map<String, dynamic>? ?? const {},
      ),
      generatedSchemas: $checkedConvert(
        'generated_schemas',
        (v) => v as Map<String, dynamic>? ?? const {},
      ),
      uiHintsSnapshot: $checkedConvert(
        'ui_hints_snapshot',
        (v) => v as Map<String, dynamic>? ?? const {},
      ),
      mcpToolAudit: $checkedConvert(
        'mcp_tool_audit',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => e as Map<String, dynamic>)
                .toList() ??
            const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'versionId': 'version_id',
    'workflowId': 'workflow_id',
    'workflowName': 'workflow_name',
    'organizationId': 'organization_id',
    'userId': 'user_id',
    'createdAt': 'created_at',
    'compiledPrompts': 'compiled_prompts',
    'injectedTheory': 'injected_theory',
    'generatedSchemas': 'generated_schemas',
    'uiHintsSnapshot': 'ui_hints_snapshot',
    'mcpToolAudit': 'mcp_tool_audit',
  },
);

Map<String, dynamic> _$FrozenContextSnapshotToJson(
  _FrozenContextSnapshot instance,
) => <String, dynamic>{
  'version_id': instance.versionId,
  'workflow_id': instance.workflowId,
  'workflow_name': instance.workflowName,
  'organization_id': instance.organizationId,
  'user_id': instance.userId,
  'created_at': instance.createdAt,
  'compiled_prompts': instance.compiledPrompts,
  'injected_theory': instance.injectedTheory,
  'generated_schemas': instance.generatedSchemas,
  'ui_hints_snapshot': instance.uiHintsSnapshot,
  'mcp_tool_audit': instance.mcpToolAudit,
};
