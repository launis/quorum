import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';

part 'mcp_gateway.freezed.dart';
part 'mcp_gateway.g.dart';

/// Recursive JSON Schema property descriptor for an MCP tool parameter.
///
/// Matches backend SSOT `MCPToolSchemaPropertyDTO` in `backend_v2/models/dtos/mcp.py`.
@Freezed(equal: false)
abstract class McpToolSchemaPropertyDto with _$McpToolSchemaPropertyDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory McpToolSchemaPropertyDto({
    JsonSchemaPropertyType? type,
    String? title,
    @Default('') String description,
    @JsonKey(name: 'enum_values') List<String>? enumValues,
    McpToolSchemaPropertyDto? items,
    Map<String, McpToolSchemaPropertyDto>? properties,
    @JsonKey(name: 'required') List<String>? requiredFields,
    @JsonKey(name: 'additional_properties') bool? additionalProperties,
    @JsonKey(name: 'default') Object? defaultValue,
    num? minimum,
    num? maximum,
    @JsonKey(name: 'min_length') int? minLength,
    @JsonKey(name: 'max_length') int? maxLength,
    // Step 2: Add JSON Schema Draft 2020-12 array bounds and constant literal fields for 1:1 DTO parity
    @JsonKey(name: 'min_items') int? minItems,
    @JsonKey(name: 'max_items') int? maxItems,
    @JsonKey(name: 'const') Object? constValue,
    @JsonKey(name: 'any_of') List<McpToolSchemaPropertyDto>? anyOf,
    // Phase 2, Step 2: Add closed JSON Schema Draft 2020-12 validation and composition vocabulary
    String? format,
    String? pattern,
    @JsonKey(name: 'unique_items') bool? uniqueItems,
    @JsonKey(name: 'exclusive_minimum') num? exclusiveMinimum,
    @JsonKey(name: 'exclusive_maximum') num? exclusiveMaximum,
    @JsonKey(name: 'multiple_of') num? multipleOf,
    @JsonKey(name: 'one_of') List<McpToolSchemaPropertyDto>? oneOf,
    @JsonKey(name: 'all_of') List<McpToolSchemaPropertyDto>? allOf,
    List<Object?>? examples,
    bool? deprecated,
    @JsonKey(name: 'read_only') bool? readOnly,
    @JsonKey(name: 'write_only') bool? writeOnly,
    String? ref,
  }) = _McpToolSchemaPropertyDto;

  factory McpToolSchemaPropertyDto.fromJson(Map<String, dynamic> json) =>
      _$McpToolSchemaPropertyDtoFromJson(json);
}

/// Strict root JSON Schema object definition for an MCP tool's input parameters.
///
/// Matches backend SSOT `MCPToolInputSchemaDTO` in `backend_v2/models/dtos/mcp.py`.
@Freezed(equal: false)
abstract class McpToolInputSchemaDto with _$McpToolInputSchemaDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory McpToolInputSchemaDto({
    @Default('object') String type,
    String? title,
    @Default('') String description,
    @Default(<String, McpToolSchemaPropertyDto>{})
    Map<String, McpToolSchemaPropertyDto> properties,
    @Default(<String>[]) @JsonKey(name: 'required') List<String> requiredFields,
    @JsonKey(name: 'additional_properties') bool? additionalProperties,
    @JsonKey(name: 'schema_uri') String? schemaUri,
    // Phase 2, Step 2: Add reusable sub-schema definitions map (defs)
    Map<String, McpToolSchemaPropertyDto>? defs,
  }) = _McpToolInputSchemaDto;

  factory McpToolInputSchemaDto.fromJson(Map<String, dynamic> json) =>
      _$McpToolInputSchemaDtoFromJson(json);
}

/// Execution control metadata for an MCP tool.
///
/// Matches backend SSOT `MCPToolExecutionDTO` in `backend_v2/models/dtos/mcp.py`.
@Freezed(equal: false)
abstract class McpToolExecutionDto with _$McpToolExecutionDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory McpToolExecutionDto({
    @JsonKey(name: 'task_support') String? taskSupport,
  }) = _McpToolExecutionDto;

  factory McpToolExecutionDto.fromJson(Map<String, dynamic> json) =>
      _$McpToolExecutionDtoFromJson(json);
}

/// Declares a single MCP tool available for LLM function calling.
///
/// Matches backend SSOT `AllowedMCPTool` in `backend_v2/models/domain/system_config.py`.
@Freezed(equal: false)
abstract class AllowedMcpTool with _$AllowedMcpTool {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory AllowedMcpTool({
    @JsonKey(name: 'tool_id') required String toolId,
    @Default(ToolCapability.search) ToolCapability capability,
    required I18nText name,
    required String description,
    @JsonKey(name: 'input_schema')
    @Default(McpToolInputSchemaDto())
    McpToolInputSchemaDto inputSchema,
    McpToolExecutionDto? execution,
    @Default(true) bool enabled,
  }) = _AllowedMcpTool;

  factory AllowedMcpTool.fromJson(Map<String, dynamic> json) =>
      _$AllowedMcpToolFromJson(json);
}

/// System-level registry of available MCP tool gateways.
///
/// Matches backend SSOT `SystemConfigMCPGateways` in `backend_v2/models/domain/system_config.py`.
@Freezed(equal: false)
abstract class McpGateway with _$McpGateway {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory McpGateway({
    @StrictOpaqueIdConverter() required String id,
    @Default('mcp_gateways') String type,
    @Default('default_mcp_gateway') String slug,
    @JsonKey(name: 'endpoint_url') @Default('') String endpointUrl,
    @JsonKey(name: 'transport_type')
    @Default(McpTransportType.streamableHttp)
    McpTransportType transportType,
    @JsonKey(name: 'auth_type') @Default(McpAuthType.none) McpAuthType authType,
    @JsonKey(name: 'auth_header_name') String? authHeaderName,
    @JsonKey(name: 'auth_env_var') String? authEnvVar,
    @JsonKey(name: 'timeout_seconds') @Default(30) int timeoutSeconds,
    @Default([]) List<AllowedMcpTool> tools,
  }) = _McpGateway;

  factory McpGateway.fromJson(Map<String, dynamic> json) =>
      _$McpGatewayFromJson(json);
}
