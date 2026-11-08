import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'frozen_context_snapshot.freezed.dart';
part 'frozen_context_snapshot.g.dart';

/// Strongly typed injected theory manifest DTO matching backend `InjectedTheoryManifestDTO`.
@Freezed(equal: false)
abstract class InjectedTheoryManifestDto with _$InjectedTheoryManifestDto {
  const InjectedTheoryManifestDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory InjectedTheoryManifestDto({
    @Default(<String, String>{}) Map<String, String> theories,
  }) = _InjectedTheoryManifestDto;

  factory InjectedTheoryManifestDto.fromJson(Map<String, dynamic> json) =>
      _$InjectedTheoryManifestDtoFromJson(json);
}

/// Strongly typed JSON Schema node within a generated schema manifest.
@Freezed(equal: false)
abstract class SchemaManifestNodeDto with _$SchemaManifestNodeDto {
  const SchemaManifestNodeDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory SchemaManifestNodeDto({
    String? type,
    String? title,
    String? description,
    @Default(<String, SchemaManifestNodeDto>{})
    Map<String, SchemaManifestNodeDto> properties,
    @Default(<String>[]) List<String> required,
    @JsonKey(name: 'additionalProperties') bool? additionalProperties,
    String? format,
  }) = _SchemaManifestNodeDto;

  factory SchemaManifestNodeDto.fromJson(Map<String, dynamic> json) =>
      _$SchemaManifestNodeDtoFromJson(json);
}

/// Strongly typed generated schema manifest DTO matching backend `GeneratedSchemaManifestDTO`.
@Freezed(equal: false)
abstract class GeneratedSchemaManifestDto with _$GeneratedSchemaManifestDto {
  const GeneratedSchemaManifestDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory GeneratedSchemaManifestDto({
    @Default(<String, SchemaManifestNodeDto>{})
    Map<String, SchemaManifestNodeDto> schemas,
  }) = _GeneratedSchemaManifestDto;

  factory GeneratedSchemaManifestDto.fromJson(Map<String, dynamic> json) =>
      _$GeneratedSchemaManifestDtoFromJson(json);
}

/// Strongly typed option DTO matching backend `SystemConfigOptionDTO`.
@Freezed(equal: false)
abstract class SystemConfigOptionDto with _$SystemConfigOptionDto {
  const SystemConfigOptionDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory SystemConfigOptionDto({required String value, String? label}) =
      _SystemConfigOptionDto;

  factory SystemConfigOptionDto.fromJson(Map<String, dynamic> json) =>
      _$SystemConfigOptionDtoFromJson(json);
}

/// Strongly typed validation rules DTO matching backend `SystemValidationRulesDTO`.
@Freezed(equal: false)
abstract class SystemValidationRulesDto with _$SystemValidationRulesDto {
  const SystemValidationRulesDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory SystemValidationRulesDto({
    double? min,
    double? max,
    bool? required,
    String? pattern,
  }) = _SystemValidationRulesDto;

  factory SystemValidationRulesDto.fromJson(Map<String, dynamic> json) =>
      _$SystemValidationRulesDtoFromJson(json);
}

/// Strongly typed UI hint dictionary field matching backend `DataDictionaryField`.
@Freezed(equal: false)
abstract class DataDictionaryField with _$DataDictionaryField {
  const DataDictionaryField._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory DataDictionaryField({
    @JsonKey(name: 'field_id') required String fieldId,
    @JsonKey(name: 'component_type') required String componentType,
    List<SystemConfigOptionDto>? options,
    @JsonKey(name: 'validation_rules')
    SystemValidationRulesDto? validationRules,
  }) = _DataDictionaryField;

  factory DataDictionaryField.fromJson(Map<String, dynamic> json) =>
      _$DataDictionaryFieldFromJson(json);
}

/// Strongly typed frozen context snapshot with multi-payload parity (SSOT).
@Freezed(equal: false)
abstract class FrozenContextSnapshot with _$FrozenContextSnapshot {
  const FrozenContextSnapshot._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory FrozenContextSnapshot({
    @JsonKey(name: 'version_id') String? versionId,
    @JsonKey(name: 'workflow_id') String? workflowId,
    @JsonKey(name: 'workflow_name') String? workflowName,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @JsonKey(name: 'created_at') String? createdAt,
    @JsonKey(name: 'compiled_prompts')
    @Default(<String, String>{})
    Map<String, String> compiledPrompts,
    @JsonKey(name: 'injected_theory')
    @Default(InjectedTheoryManifestDto())
    InjectedTheoryManifestDto injectedTheory,
    @JsonKey(name: 'generated_schemas')
    @Default(GeneratedSchemaManifestDto())
    GeneratedSchemaManifestDto generatedSchemas,
    @JsonKey(name: 'ui_hints_snapshot')
    @Default(<String, DataDictionaryField>{})
    Map<String, DataDictionaryField> uiHintsSnapshot,
    @JsonKey(name: 'mcp_tool_audit')
    @Default(<McpAuditTraceDto>[])
    List<McpAuditTraceDto> mcpToolAudit,
  }) = _FrozenContextSnapshot;

  /// Instantiates a strictly typed [FrozenContextSnapshot] from raw JSON.
  factory FrozenContextSnapshot.fromJson(Map<String, dynamic> json) =>
      _$FrozenContextSnapshotFromJson(json);
}
