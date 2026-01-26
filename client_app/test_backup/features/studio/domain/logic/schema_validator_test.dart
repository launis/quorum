import 'package:client_app/features/studio/domain/logic/schema_validator.dart';
import 'package:client_app/features/studio/domain/models/json_schema.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SchemaValidator', () {
    test('returns null for null value', () {
      final schema = JsonSchema(type: 'string');
      expect(SchemaValidator.validate(schema, null), isNull);
    });

    group('String', () {
      test('validates minLength', () {
        final schema = JsonSchema(type: 'string', minLength: 3);
        expect(SchemaValidator.validate(schema, 'ab'), contains('Min length'));
        expect(SchemaValidator.validate(schema, 'abc'), isNull);
      });

      test('validates maxLength', () {
        final schema = JsonSchema(type: 'string', maxLength: 3);
        expect(SchemaValidator.validate(schema, 'abcd'), contains('Max length'));
        expect(SchemaValidator.validate(schema, 'abc'), isNull);
      });
    });

    group('Number', () {
      test('validates minimum', () {
        final schema = JsonSchema(type: 'number', minimum: 10);
        expect(SchemaValidator.validate(schema, 9), contains('Minimum'));
        expect(SchemaValidator.validate(schema, 10), isNull);
      });

      test('validates maximum', () {
        final schema = JsonSchema(type: 'number', maximum: 10);
        expect(SchemaValidator.validate(schema, 11), contains('Maximum'));
        expect(SchemaValidator.validate(schema, 10), isNull);
      });
    });

    group('Enum', () {
      test('validates enum values', () {
        final schema = JsonSchema(enumValues: ['A', 'B']);
        expect(SchemaValidator.validate(schema, 'C'), contains('Value must be one of'));
        expect(SchemaValidator.validate(schema, 'A'), isNull);
      });
    });
  });
}
