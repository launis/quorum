import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/hydrated_atom_dto.dart';

void main() {
  group('HydratedAtomDTO Contract Tests', () {
    test('test_hydrated_atom_dto_serialization_success', () {
      const dto = HydratedAtomDTO(
        sduiComponent: SDUIComponentType.booleanCard,
        resolvedClaim: 'Claim has been fully verified.',
        sourceQuotes: ['Verified citation segment 1', 'Segment 2'],
      );

      final json = dto.toJson();
      expect(json['sdui_component'], 'boolean_card');
      expect(json['resolved_claim'], 'Claim has been fully verified.');
      expect(json['source_quotes'], [
        'Verified citation segment 1',
        'Segment 2',
      ]);
    });

    test('test_hydrated_atom_dto_deserialization_success', () {
      final json = {
        'sdui_component': 'extracted_value_card',
        'resolved_claim': 'Extracted KPI metric value: 85%',
        'source_quotes': null,
      };

      final dto = HydratedAtomDTO.fromJson(json);
      expect(dto.sduiComponent, SDUIComponentType.extractedValueCard);
      expect(dto.resolvedClaim, 'Extracted KPI metric value: 85%');
      expect(dto.sourceQuotes, isNull);
    });

    test('test_hydrated_atom_dto_hallucinated_fields_fail_fast', () {
      final hallucinatedJson = {
        'sdui_component': 'error_card',
        'resolved_claim': 'Error parsing',
        'illegal_unrecognized_key': 'unexpected',
      };

      expect(
        () => HydratedAtomDTO.fromJson(hallucinatedJson),
        throwsA(
          anyOf(
            isA<FormatException>(),
            isA<TypeError>(),
            isA<CheckedFromJsonException>(),
          ),
        ),
      );
    });

    test('test_hydrated_atom_dto_invalid_enum_throws', () {
      final invalidEnumJson = {
        'sdui_component': 'unknown_component',
        'resolved_claim': 'Invalid component test',
      };

      expect(
        () => HydratedAtomDTO.fromJson(invalidEnumJson),
        throwsA(anything),
      );
    });
  });
}
