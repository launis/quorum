// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'hydrated_atom_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_HydratedAtomDTO _$HydratedAtomDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_HydratedAtomDTO',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'sdui_component',
            'resolved_claim',
            'source_quote',
          ],
        );
        final val = _HydratedAtomDTO(
          sduiComponent: $checkedConvert(
            'sdui_component',
            (v) => $enumDecode(_$SDUIComponentTypeEnumMap, v),
          ),
          resolvedClaim: $checkedConvert('resolved_claim', (v) => v as String),
          sourceQuote: $checkedConvert('source_quote', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'sduiComponent': 'sdui_component',
        'resolvedClaim': 'resolved_claim',
        'sourceQuote': 'source_quote',
      },
    );

Map<String, dynamic> _$HydratedAtomDTOToJson(_HydratedAtomDTO instance) =>
    <String, dynamic>{
      'sdui_component': _$SDUIComponentTypeEnumMap[instance.sduiComponent]!,
      'resolved_claim': instance.resolvedClaim,
      'source_quote': instance.sourceQuote,
    };

const _$SDUIComponentTypeEnumMap = {
  SDUIComponentType.booleanCard: 'boolean_card',
  SDUIComponentType.extractedValueCard: 'extracted_value_card',
  SDUIComponentType.errorCard: 'error_card',
  SDUIComponentType.nACard: 'n_a_card',
};
