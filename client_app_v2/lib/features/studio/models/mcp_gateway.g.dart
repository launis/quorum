// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'mcp_gateway.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_McpToolSchemaPropertyDto _$McpToolSchemaPropertyDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_McpToolSchemaPropertyDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'type',
        'title',
        'description',
        'enum_values',
        'items',
        'properties',
        'required',
        'additional_properties',
        'default',
        'minimum',
        'maximum',
        'any_of',
      ],
    );
    final val = _McpToolSchemaPropertyDto(
      type: $checkedConvert(
        'type',
        (v) => $enumDecodeNullable(_$JsonSchemaPropertyTypeEnumMap, v),
      ),
      title: $checkedConvert('title', (v) => v as String?),
      description: $checkedConvert('description', (v) => v as String? ?? ''),
      enumValues: $checkedConvert(
        'enum_values',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
      ),
      items: $checkedConvert(
        'items',
        (v) => v == null
            ? null
            : McpToolSchemaPropertyDto.fromJson(v as Map<String, dynamic>),
      ),
      properties: $checkedConvert(
        'properties',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(
            k,
            McpToolSchemaPropertyDto.fromJson(e as Map<String, dynamic>),
          ),
        ),
      ),
      requiredFields: $checkedConvert(
        'required',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
      ),
      additionalProperties: $checkedConvert(
        'additional_properties',
        (v) => v as bool?,
      ),
      defaultValue: $checkedConvert('default', (v) => v),
      minimum: $checkedConvert('minimum', (v) => v as num?),
      maximum: $checkedConvert('maximum', (v) => v as num?),
      anyOf: $checkedConvert(
        'any_of',
        (v) => (v as List<dynamic>?)
            ?.map(
              (e) =>
                  McpToolSchemaPropertyDto.fromJson(e as Map<String, dynamic>),
            )
            .toList(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'enumValues': 'enum_values',
    'requiredFields': 'required',
    'additionalProperties': 'additional_properties',
    'defaultValue': 'default',
    'anyOf': 'any_of',
  },
);

Map<String, dynamic> _$McpToolSchemaPropertyDtoToJson(
  _McpToolSchemaPropertyDto instance,
) => <String, dynamic>{
  'type': _$JsonSchemaPropertyTypeEnumMap[instance.type],
  'title': instance.title,
  'description': instance.description,
  'enum_values': instance.enumValues,
  'items': instance.items?.toJson(),
  'properties': instance.properties?.map((k, e) => MapEntry(k, e.toJson())),
  'required': instance.requiredFields,
  'additional_properties': instance.additionalProperties,
  'default': instance.defaultValue,
  'minimum': instance.minimum,
  'maximum': instance.maximum,
  'any_of': instance.anyOf?.map((e) => e.toJson()).toList(),
};

const _$JsonSchemaPropertyTypeEnumMap = {
  JsonSchemaPropertyType.string: 'string',
  JsonSchemaPropertyType.number: 'number',
  JsonSchemaPropertyType.integer: 'integer',
  JsonSchemaPropertyType.boolean: 'boolean',
  JsonSchemaPropertyType.array: 'array',
  JsonSchemaPropertyType.object: 'object',
  JsonSchemaPropertyType.nullValue: 'null',
};

_McpToolInputSchemaDto _$McpToolInputSchemaDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_McpToolInputSchemaDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'type',
        'title',
        'description',
        'properties',
        'required',
        'additional_properties',
      ],
    );
    final val = _McpToolInputSchemaDto(
      type: $checkedConvert('type', (v) => v as String? ?? 'object'),
      title: $checkedConvert('title', (v) => v as String?),
      description: $checkedConvert('description', (v) => v as String? ?? ''),
      properties: $checkedConvert(
        'properties',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(
                k,
                McpToolSchemaPropertyDto.fromJson(e as Map<String, dynamic>),
              ),
            ) ??
            const <String, McpToolSchemaPropertyDto>{},
      ),
      requiredFields: $checkedConvert(
        'required',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ??
            const <String>[],
      ),
      additionalProperties: $checkedConvert(
        'additional_properties',
        (v) => v as bool?,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'requiredFields': 'required',
    'additionalProperties': 'additional_properties',
  },
);

Map<String, dynamic> _$McpToolInputSchemaDtoToJson(
  _McpToolInputSchemaDto instance,
) => <String, dynamic>{
  'type': instance.type,
  'title': instance.title,
  'description': instance.description,
  'properties': instance.properties.map((k, e) => MapEntry(k, e.toJson())),
  'required': instance.requiredFields,
  'additional_properties': instance.additionalProperties,
};

_AllowedMcpTool _$AllowedMcpToolFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_AllowedMcpTool',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'tool_id',
            'capability',
            'name',
            'description',
            'input_schema',
            'enabled',
          ],
        );
        final val = _AllowedMcpTool(
          toolId: $checkedConvert('tool_id', (v) => v as String),
          capability: $checkedConvert(
            'capability',
            (v) =>
                $enumDecodeNullable(_$ToolCapabilityEnumMap, v) ??
                ToolCapability.search,
          ),
          name: $checkedConvert(
            'name',
            (v) => I18nText.fromJson(v as Map<String, dynamic>),
          ),
          description: $checkedConvert('description', (v) => v as String),
          inputSchema: $checkedConvert(
            'input_schema',
            (v) => v == null
                ? const McpToolInputSchemaDto()
                : McpToolInputSchemaDto.fromJson(v as Map<String, dynamic>),
          ),
          enabled: $checkedConvert('enabled', (v) => v as bool? ?? true),
        );
        return val;
      },
      fieldKeyMap: const {'toolId': 'tool_id', 'inputSchema': 'input_schema'},
    );

Map<String, dynamic> _$AllowedMcpToolToJson(_AllowedMcpTool instance) =>
    <String, dynamic>{
      'tool_id': instance.toolId,
      'capability': _$ToolCapabilityEnumMap[instance.capability]!,
      'name': instance.name.toJson(),
      'description': instance.description,
      'input_schema': instance.inputSchema.toJson(),
      'enabled': instance.enabled,
    };

const _$ToolCapabilityEnumMap = {
  ToolCapability.search: 'search',
  ToolCapability.documentReader: 'document_reader',
  ToolCapability.action: 'action',
  ToolCapability.general: 'general',
};

_McpGateway _$McpGatewayFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_McpGateway',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'type',
        'slug',
        'endpoint_url',
        'transport_type',
        'auth_type',
        'auth_header_name',
        'auth_env_var',
        'timeout_seconds',
        'tools',
      ],
    );
    final val = _McpGateway(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      type: $checkedConvert('type', (v) => v as String? ?? 'mcp_gateways'),
      slug: $checkedConvert(
        'slug',
        (v) => v as String? ?? 'default_mcp_gateway',
      ),
      endpointUrl: $checkedConvert('endpoint_url', (v) => v as String? ?? ''),
      transportType: $checkedConvert(
        'transport_type',
        (v) =>
            $enumDecodeNullable(_$McpTransportTypeEnumMap, v) ??
            McpTransportType.streamableHttp,
      ),
      authType: $checkedConvert(
        'auth_type',
        (v) => $enumDecodeNullable(_$McpAuthTypeEnumMap, v) ?? McpAuthType.none,
      ),
      authHeaderName: $checkedConvert('auth_header_name', (v) => v as String?),
      authEnvVar: $checkedConvert('auth_env_var', (v) => v as String?),
      timeoutSeconds: $checkedConvert(
        'timeout_seconds',
        (v) => (v as num?)?.toInt() ?? 30,
      ),
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
  fieldKeyMap: const {
    'endpointUrl': 'endpoint_url',
    'transportType': 'transport_type',
    'authType': 'auth_type',
    'authHeaderName': 'auth_header_name',
    'authEnvVar': 'auth_env_var',
    'timeoutSeconds': 'timeout_seconds',
  },
);

Map<String, dynamic> _$McpGatewayToJson(_McpGateway instance) =>
    <String, dynamic>{
      'id': const StrictOpaqueIdConverter().toJson(instance.id),
      'type': instance.type,
      'slug': instance.slug,
      'endpoint_url': instance.endpointUrl,
      'transport_type': _$McpTransportTypeEnumMap[instance.transportType]!,
      'auth_type': _$McpAuthTypeEnumMap[instance.authType]!,
      'auth_header_name': instance.authHeaderName,
      'auth_env_var': instance.authEnvVar,
      'timeout_seconds': instance.timeoutSeconds,
      'tools': instance.tools.map((e) => e.toJson()).toList(),
    };

const _$McpTransportTypeEnumMap = {
  McpTransportType.streamableHttp: 'streamable_http',
  McpTransportType.sse: 'sse',
};

const _$McpAuthTypeEnumMap = {
  McpAuthType.none: 'none',
  McpAuthType.bearer: 'bearer',
  McpAuthType.apiKeyHeader: 'api_key_header',
};
