// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'mcp_gateway.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_AllowedMcpTool _$AllowedMcpToolFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_AllowedMcpTool',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const ['tool_id', 'name', 'description', 'input_schema'],
        );
        final val = _AllowedMcpTool(
          toolId: $checkedConvert('tool_id', (v) => v as String),
          name: $checkedConvert(
            'name',
            (v) => I18nText.fromJson(v as Map<String, dynamic>),
          ),
          description: $checkedConvert('description', (v) => v as String),
          inputSchema: $checkedConvert(
            'input_schema',
            (v) => v as Map<String, dynamic>? ?? const {},
          ),
        );
        return val;
      },
      fieldKeyMap: const {'toolId': 'tool_id', 'inputSchema': 'input_schema'},
    );

Map<String, dynamic> _$AllowedMcpToolToJson(_AllowedMcpTool instance) =>
    <String, dynamic>{
      'tool_id': instance.toolId,
      'name': instance.name.toJson(),
      'description': instance.description,
      'input_schema': instance.inputSchema,
    };

_McpGateway _$McpGatewayFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_McpGateway',
  json,
  ($checkedConvert) {
    $checkKeys(json, allowedKeys: const ['id', 'type', 'slug', 'tools']);
    final val = _McpGateway(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      type: $checkedConvert('type', (v) => v as String? ?? 'mcp_gateways'),
      slug: $checkedConvert('slug', (v) => v as String?),
      tools: $checkedConvert(
        'tools',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => AllowedMcpTool.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
    );
    return val;
  },
);

Map<String, dynamic> _$McpGatewayToJson(_McpGateway instance) =>
    <String, dynamic>{
      'id': const StrictOpaqueIdConverter().toJson(instance.id),
      'type': instance.type,
      'slug': instance.slug,
      'tools': instance.tools.map((e) => e.toJson()).toList(),
    };
