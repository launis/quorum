import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';

void main() {
  group('McpGateway Contract Tests', () {
    test('test_mcp_gateway_json_deserialization_success', () {
      // Input: Valid JSON matching SystemConfigMCPGateways SSOT
      final validJson = {
        'id': 'gw_1234567812345678',
        'type': 'stdio',
        'slug': 'filesystem_gateway',
        'tools': [
          {
            'tool_id': 'read_file',
            'name': {
              'translations': {'en': 'Read File'},
            },
            'description': 'Reads local files',
            'input_schema': {
              'type': 'object',
              'properties': {
                'path': {'type': 'string'},
              },
            },
          },
        ],
      };

      // Act
      final gateway = McpGateway.fromJson(validJson);

      // Expected: Instantiates McpGateway with correct tools list
      expect(gateway.id, 'gw_1234567812345678');
      expect(gateway.type, 'stdio');
      expect(gateway.slug, 'filesystem_gateway');
      expect(gateway.tools.length, 1);
      expect(gateway.tools.first.toolId, 'read_file');
      expect(gateway.tools.first.name.translations['en'], 'Read File');
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
