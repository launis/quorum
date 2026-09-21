// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';

part 'mcp_gateway.freezed.dart';
part 'mcp_gateway.g.dart';

/// Declares a single MCP tool available for LLM function calling.
///
/// Matches backend SSOT `AllowedMCPTool` in `backend_v2/models/domain/system_config.py`.
@Freezed(equal: false)
abstract class AllowedMcpTool with _$AllowedMcpTool {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory AllowedMcpTool({
    @JsonKey(name: 'tool_id') required String toolId,
    required I18nText name,
    required String description,
    @JsonKey(name: 'input_schema')
    @Default({})
    Map<String, dynamic> inputSchema,
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
    String? slug,
    @Default([]) List<AllowedMcpTool> tools,
  }) = _McpGateway;

  factory McpGateway.fromJson(Map<String, dynamic> json) =>
      _$McpGatewayFromJson(json);
}
