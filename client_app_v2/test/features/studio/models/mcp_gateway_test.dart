import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';

void main() {
  group('McpGateway Contract Tests', () {
    test('test_mcp_gateway_json_deserialization_success', () {
      // Input: Valid JSON matching SystemConfigMCPGateways SSOT
      final validJson = {
        'id': 'gw_0195f3a0000070008000000000000001',
        'name': 'Filesystem MCP Gateway',
        'type': 'stdio',
        'slug': 'filesystem_gateway',
        'endpoint_url': 'https://mcp.example.com/v1',
        'transport_type': 'streamable_http',
        'auth_type': 'bearer',
        'auth_env_var': 'MCP_TOKEN',
        'timeout_seconds': 45,
        'tools': [
          {
            'tool_id': 'read_file',
            'name': {
              'translations': {'en': 'Read File'},
            },
            'description': 'Reads local files',
            'enabled': true,
            'input_schema': {
              'type': 'object',
              'properties': {
                'path': {
                  'type': 'string',
                  'description': 'File path',
                  'enum_values': ['/a', '/b'],
                },
              },
              'required': ['path'],
              'additional_properties': false,
            },
          },
        ],
      };

      // Act
      final gateway = McpGateway.fromJson(validJson);

      // Expected: Instantiates McpGateway with correct tools list and recursive schema DTOs
      expect(gateway.id, 'gw_0195f3a0000070008000000000000001');
      expect(gateway.name, 'Filesystem MCP Gateway');
      expect(gateway.type, 'stdio');
      expect(gateway.slug, 'filesystem_gateway');
      expect(gateway.endpointUrl, 'https://mcp.example.com/v1');
      expect(gateway.transportType, McpTransportType.streamableHttp);
      expect(gateway.authType, McpAuthType.bearer);
      expect(gateway.authEnvVar, 'MCP_TOKEN');
      expect(gateway.timeoutSeconds, 45);
      expect(gateway.tools.length, 1);
      expect(gateway.tools.first.toolId, 'read_file');
      expect(gateway.tools.first.capability, ToolCapability.search);
      expect(gateway.tools.first.enabled, isTrue);
      expect(gateway.tools.first.name.translations['en'], 'Read File');
      expect(
        gateway.tools.first.inputSchema.properties['path']?.type,
        JsonSchemaPropertyType.string,
      );
      expect(gateway.tools.first.inputSchema.properties['path']?.enumValues, [
        '/a',
        '/b',
      ]);
      expect(gateway.tools.first.inputSchema.requiredFields, ['path']);
      expect(gateway.tools.first.inputSchema.additionalProperties, isFalse);
    });

    test('test_mcp_gateway_with_explicit_capability', () {
      final validJson = {
        'id': 'gw_0195f3a0000070008000000000000001',
        'name': 'Wikipedia MCP Gateway',
        'type': 'stdio',
        'tools': [
          {
            'tool_id': 'mcp_wikipedia_read',
            'capability': 'document_reader',
            'name': {
              'translations': {'en': 'Wikipedia Article Reader'},
            },
            'description': 'Reads article',
            'input_schema': {'type': 'object'},
          },
        ],
      };

      final gateway = McpGateway.fromJson(validJson);
      expect(gateway.name, 'Wikipedia MCP Gateway');
      expect(gateway.tools.first.capability, ToolCapability.documentReader);
    });

    test('test_mcp_gateway_hallucinated_fields_fail_fast', () {
      // Input: JSON containing hallucinated 'allowed_tools' or 'is_active'
      final hallucinatedJson1 = {
        'id': 'gw_0195f3a0000070008000000000000001',
        'name': 'Filesystem MCP Gateway',
        'type': 'stdio',
        'slug': 'filesystem_gateway',
        'allowed_tools': <Object?>[], // Hallucinated key
        'tools': <Object?>[],
      };

      final hallucinatedJson2 = {
        'id': 'gw_0195f3a0000070008000000000000001',
        'name': 'Filesystem MCP Gateway',
        'type': 'stdio',
        'slug': 'filesystem_gateway',
        'is_active': true, // Hallucinated key
        'tools': <Object?>[],
      };

      // Expected: Throws CheckedFromJsonException/FormatException due to strict schema lockdown
      expect(
        () => McpGateway.fromJson(hallucinatedJson1),
        throwsA(anyOf(isA<FormatException>(), isA<CheckedFromJsonException>())),
      );

      expect(
        () => McpGateway.fromJson(hallucinatedJson2),
        throwsA(anyOf(isA<FormatException>(), isA<CheckedFromJsonException>())),
      );
    });

    test('test_mcp_gateway_invalid_opaque_id_fails_fast', () {
      final invalidIdJson = {
        'id': 'gw_short_id', // Fails 32-hex UUIDv7 boundary check
        'name': 'Filesystem MCP Gateway',
        'type': 'mcp_gateways',
        'slug': 'filesystem_gateway',
        'tools': <Object?>[],
      };

      expect(
        () => McpGateway.fromJson(invalidIdJson),
        throwsA(
          anyOf(
            isA<AppException>(),
            isA<CheckedFromJsonException>(),
            isA<FormatException>(),
          ),
        ),
      );
    });

    test('test_allowed_mcp_tool_missing_required_fields_fails_fast', () {
      final missingRequiredJson = {
        'id': 'gw_0195f3a0000070008000000000000001',
        'name': 'Filesystem MCP Gateway',
        'tools': [
          {
            // Missing required 'tool_id', 'name', and 'description'
            'capability': 'search',
          },
        ],
      };

      expect(
        () => McpGateway.fromJson(missingRequiredJson),
        throwsA(
          anyOf(
            isA<TypeError>(),
            isA<CheckedFromJsonException>(),
            isA<FormatException>(),
          ),
        ),
      );

      final missingGatewayNameJson = {
        'id': 'gw_0195f3a0000070008000000000000001',
        'slug': 'filesystem_gateway',
        'tools': <Object?>[],
      };

      expect(
        () => McpGateway.fromJson(missingGatewayNameJson),
        throwsA(
          anyOf(
            isA<TypeError>(),
            isA<CheckedFromJsonException>(),
            isA<FormatException>(),
          ),
        ),
      );
    });

    test(
      'test_mcp_tool_schema_property_dto_min_items_max_items_and_const_positive_and_negative',
      () {
        final propJson = <String, dynamic>{
          'any_of': <Map<String, dynamic>>[
            <String, dynamic>{
              'type': 'array',
              'min_items': 1,
              'max_items': 5,
              'items': <String, dynamic>{
                'type': 'object',
                'properties': <String, dynamic>{
                  'type': <String, dynamic>{
                    'type': 'string',
                    'const': 'base64',
                  },
                },
              },
            },
          ],
        };

        final parsed = McpToolSchemaPropertyDto.fromJson(propJson);
        expect(parsed.anyOf, isNotNull);
        expect(parsed.anyOf!.first.minItems, equals(1));
        expect(parsed.anyOf!.first.maxItems, equals(5));
        expect(
          parsed.anyOf!.first.items?.properties?['type']?.constValue,
          equals('base64'),
        );

        // Negative 1: Unrecognized key rejected by disallowUnrecognizedKeys: true
        expect(
          () => McpToolSchemaPropertyDto.fromJson(<String, dynamic>{
            'type': 'array',
            'min_items': 1,
            'unrecognized_schema_key': true,
          }),
          throwsA(
            anyOf(isA<FormatException>(), isA<CheckedFromJsonException>()),
          ),
        );

        // Negative 2: Wrong type for min_items (String instead of int) rejected
        expect(
          () => McpToolSchemaPropertyDto.fromJson(<String, dynamic>{
            'type': 'array',
            'min_items': 'not_an_int',
          }),
          throwsA(
            anyOf(
              isA<TypeError>(),
              isA<FormatException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );

    test(
      'test_mcp_tool_schema_draft_2020_12_fields_and_defs_positive_and_negative',
      () {
        final schemaJson = <String, dynamic>{
          'type': 'object',
          'defs': <String, dynamic>{
            'UrlRef': <String, dynamic>{'type': 'string', 'format': 'uri'},
          },
          'properties': <String, dynamic>{
            'url': <String, dynamic>{
              'type': 'string',
              'format': 'uri',
              'pattern': r'^https?://',
              'unique_items': true,
              'exclusive_minimum': 0,
              'exclusive_maximum': 100,
              'multiple_of': 0.5,
              'one_of': <Map<String, dynamic>>[
                <String, dynamic>{'type': 'string'},
              ],
              'all_of': <Map<String, dynamic>>[
                <String, dynamic>{'type': 'string'},
              ],
              'examples': <Object?>['https://jina.ai'],
              'deprecated': false,
              'read_only': false,
              'write_only': false,
              'ref': r'#/$defs/UrlRef',
            },
          },
        };

        final parsed = McpToolInputSchemaDto.fromJson(schemaJson);
        expect(parsed.defs?['UrlRef']?.format, equals('uri'));
        final urlProp = parsed.properties['url']!;
        expect(urlProp.format, equals('uri'));
        expect(urlProp.pattern, equals(r'^https?://'));
        expect(urlProp.uniqueItems, isTrue);
        expect(urlProp.exclusiveMinimum, equals(0));
        expect(urlProp.exclusiveMaximum, equals(100));
        expect(urlProp.multipleOf, equals(0.5));
        expect(urlProp.oneOf?.length, equals(1));
        expect(urlProp.allOf?.length, equals(1));
        expect(urlProp.examples, equals(<Object?>['https://jina.ai']));
        expect(urlProp.deprecated, isFalse);
        expect(urlProp.readOnly, isFalse);
        expect(urlProp.writeOnly, isFalse);
        expect(urlProp.ref, equals(r'#/$defs/UrlRef'));

        // Negative 1: Unrecognized key rejected by disallowUnrecognizedKeys: true
        expect(
          () => McpToolSchemaPropertyDto.fromJson(<String, dynamic>{
            'type': 'string',
            'format': 'uri',
            'unknown_vendor_key': true,
          }),
          throwsA(
            anyOf(isA<FormatException>(), isA<CheckedFromJsonException>()),
          ),
        );

        // Negative 2: Invalid type for unique_items (String instead of bool) rejected
        expect(
          () => McpToolSchemaPropertyDto.fromJson(<String, dynamic>{
            'type': 'array',
            'unique_items': 'not_a_bool',
          }),
          throwsA(
            anyOf(
              isA<TypeError>(),
              isA<FormatException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );
  });
}
