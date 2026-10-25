import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';

void main() {
  group('McpGateway Contract Tests', () {
    test('test_mcp_gateway_json_deserialization_success', () {
      // Input: Valid JSON matching SystemConfigMCPGateways SSOT
      final validJson = {
        'id': 'gw_1234567812345678',
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
      expect(gateway.id, 'gw_1234567812345678');
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
        'id': 'gw_1234567812345678',
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
      expect(gateway.tools.first.capability, ToolCapability.documentReader);
    });

    test('test_mcp_gateway_hallucinated_fields_fail_fast', () {
      // Input: JSON containing hallucinated 'allowed_tools' or 'is_active'
      final hallucinatedJson1 = {
        'id': 'gw_1234567812345678',
        'type': 'stdio',
        'slug': 'filesystem_gateway',
        'allowed_tools': [], // Hallucinated key
        'tools': [],
      };

      final hallucinatedJson2 = {
        'id': 'gw_1234567812345678',
        'type': 'stdio',
        'slug': 'filesystem_gateway',
        'is_active': true, // Hallucinated key
        'tools': [],
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
  });
}
