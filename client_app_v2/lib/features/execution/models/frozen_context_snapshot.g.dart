// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'frozen_context_snapshot.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_InjectedTheoryManifestDto _$InjectedTheoryManifestDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_InjectedTheoryManifestDto', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['theories']);
  final val = _InjectedTheoryManifestDto(
    theories: $checkedConvert(
      'theories',
      (v) =>
          (v as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, e as String),
          ) ??
          const <String, String>{},
    ),
  );
  return val;
});

Map<String, dynamic> _$InjectedTheoryManifestDtoToJson(
  _InjectedTheoryManifestDto instance,
) => <String, dynamic>{'theories': instance.theories};

_SchemaManifestNodeDto _$SchemaManifestNodeDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_SchemaManifestNodeDto', json, ($checkedConvert) {
  $checkKeys(
    json,
    allowedKeys: const [
      'type',
      'title',
      'description',
      'properties',
      'required',
      'additionalProperties',
      'format',
    ],
  );
  final val = _SchemaManifestNodeDto(
    type: $checkedConvert('type', (v) => v as String?),
    title: $checkedConvert('title', (v) => v as String?),
    description: $checkedConvert('description', (v) => v as String?),
    properties: $checkedConvert(
      'properties',
      (v) =>
          (v as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(
              k,
              SchemaManifestNodeDto.fromJson(e as Map<String, dynamic>),
            ),
          ) ??
          const <String, SchemaManifestNodeDto>{},
    ),
    required: $checkedConvert(
      'required',
      (v) =>
          (v as List<dynamic>?)?.map((e) => e as String).toList() ??
          const <String>[],
    ),
    additionalProperties: $checkedConvert(
      'additionalProperties',
      (v) => v as bool?,
    ),
    format: $checkedConvert('format', (v) => v as String?),
  );
  return val;
});

Map<String, dynamic> _$SchemaManifestNodeDtoToJson(
  _SchemaManifestNodeDto instance,
) => <String, dynamic>{
  'type': instance.type,
  'title': instance.title,
  'description': instance.description,
  'properties': instance.properties.map((k, e) => MapEntry(k, e.toJson())),
  'required': instance.required,
  'additionalProperties': instance.additionalProperties,
  'format': instance.format,
};

_GeneratedSchemaManifestDto _$GeneratedSchemaManifestDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_GeneratedSchemaManifestDto', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['schemas']);
  final val = _GeneratedSchemaManifestDto(
    schemas: $checkedConvert(
      'schemas',
      (v) =>
          (v as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(
              k,
              SchemaManifestNodeDto.fromJson(e as Map<String, dynamic>),
            ),
          ) ??
          const <String, SchemaManifestNodeDto>{},
    ),
  );
  return val;
});

Map<String, dynamic> _$GeneratedSchemaManifestDtoToJson(
  _GeneratedSchemaManifestDto instance,
) => <String, dynamic>{
  'schemas': instance.schemas.map((k, e) => MapEntry(k, e.toJson())),
};

_SystemConfigOptionDto _$SystemConfigOptionDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_SystemConfigOptionDto', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['value', 'label']);
  final val = _SystemConfigOptionDto(
    value: $checkedConvert('value', (v) => v as String),
    label: $checkedConvert('label', (v) => v as String?),
  );
  return val;
});

Map<String, dynamic> _$SystemConfigOptionDtoToJson(
  _SystemConfigOptionDto instance,
) => <String, dynamic>{'value': instance.value, 'label': instance.label};

_SystemValidationRulesDto _$SystemValidationRulesDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_SystemValidationRulesDto', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['min', 'max', 'required', 'pattern']);
  final val = _SystemValidationRulesDto(
    min: $checkedConvert('min', (v) => (v as num?)?.toDouble()),
    max: $checkedConvert('max', (v) => (v as num?)?.toDouble()),
    required: $checkedConvert('required', (v) => v as bool?),
    pattern: $checkedConvert('pattern', (v) => v as String?),
  );
  return val;
});

Map<String, dynamic> _$SystemValidationRulesDtoToJson(
  _SystemValidationRulesDto instance,
) => <String, dynamic>{
  'min': instance.min,
  'max': instance.max,
  'required': instance.required,
  'pattern': instance.pattern,
};

_DataDictionaryField _$DataDictionaryFieldFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_DataDictionaryField',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'field_id',
            'component_type',
            'options',
            'validation_rules',
          ],
        );
        final val = _DataDictionaryField(
          fieldId: $checkedConvert('field_id', (v) => v as String),
          componentType: $checkedConvert('component_type', (v) => v as String),
          options: $checkedConvert(
            'options',
            (v) => (v as List<dynamic>?)
                ?.map(
                  (e) =>
                      SystemConfigOptionDto.fromJson(e as Map<String, dynamic>),
                )
                .toList(),
          ),
          validationRules: $checkedConvert(
            'validation_rules',
            (v) => v == null
                ? null
                : SystemValidationRulesDto.fromJson(v as Map<String, dynamic>),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'fieldId': 'field_id',
        'componentType': 'component_type',
        'validationRules': 'validation_rules',
      },
    );

Map<String, dynamic> _$DataDictionaryFieldToJson(
  _DataDictionaryField instance,
) => <String, dynamic>{
  'field_id': instance.fieldId,
  'component_type': instance.componentType,
  'options': instance.options?.map((e) => e.toJson()).toList(),
  'validation_rules': instance.validationRules?.toJson(),
};

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
            const <String, String>{},
      ),
      injectedTheory: $checkedConvert(
        'injected_theory',
        (v) => v == null
            ? const InjectedTheoryManifestDto()
            : InjectedTheoryManifestDto.fromJson(v as Map<String, dynamic>),
      ),
      generatedSchemas: $checkedConvert(
        'generated_schemas',
        (v) => v == null
            ? const GeneratedSchemaManifestDto()
            : GeneratedSchemaManifestDto.fromJson(v as Map<String, dynamic>),
      ),
      uiHintsSnapshot: $checkedConvert(
        'ui_hints_snapshot',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(
                k,
                DataDictionaryField.fromJson(e as Map<String, dynamic>),
              ),
            ) ??
            const <String, DataDictionaryField>{},
      ),
      mcpToolAudit: $checkedConvert(
        'mcp_tool_audit',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) => McpAuditTraceDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const <McpAuditTraceDto>[],
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
  'injected_theory': instance.injectedTheory.toJson(),
  'generated_schemas': instance.generatedSchemas.toJson(),
  'ui_hints_snapshot': instance.uiHintsSnapshot.map(
    (k, e) => MapEntry(k, e.toJson()),
  ),
  'mcp_tool_audit': instance.mcpToolAudit.map((e) => e.toJson()).toList(),
};
