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
    required JsonSchemaPropertyType type,
    String? title,
    @Default('') String description,
    @JsonKey(name: 'enum_values') List<String>? enumValues,
    McpToolSchemaPropertyDto? items,
    Map<String, McpToolSchemaPropertyDto>? properties,
    @JsonKey(name: 'required') List<String>? requiredFields,
    @JsonKey(name: 'additional_properties') bool? additionalProperties,
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
    @Default(<String>[])
    @JsonKey(name: 'required')
    List<String> requiredFields,
    @JsonKey(name: 'additional_properties') bool? additionalProperties,
  }) = _McpToolInputSchemaDto;

  factory McpToolInputSchemaDto.fromJson(Map<String, dynamic> json) =>
      _$McpToolInputSchemaDtoFromJson(json);
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
    @JsonKey(name: 'auth_type')
    @Default(McpAuthType.none)
    McpAuthType authType,
    @JsonKey(name: 'auth_header_name') String? authHeaderName,
    @JsonKey(name: 'auth_env_var') String? authEnvVar,
    @JsonKey(name: 'timeout_seconds') @Default(30) int timeoutSeconds,
    @Default([]) List<AllowedMcpTool> tools,
  }) = _McpGateway;

  factory McpGateway.fromJson(Map<String, dynamic> json) =>
      _$McpGatewayFromJson(json);
}
