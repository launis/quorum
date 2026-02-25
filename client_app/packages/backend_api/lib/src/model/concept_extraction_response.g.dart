// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'concept_extraction_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ConceptExtractionResponseCWProxy {
  ConceptExtractionResponse sourceLength(int sourceLength);

  ConceptExtractionResponse concepts(Object? concepts);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ConceptExtractionResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ConceptExtractionResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ConceptExtractionResponse call({int sourceLength, Object? concepts});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfConceptExtractionResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfConceptExtractionResponse.copyWith.fieldName(...)`
class _$ConceptExtractionResponseCWProxyImpl
    implements _$ConceptExtractionResponseCWProxy {
  const _$ConceptExtractionResponseCWProxyImpl(this._value);

  final ConceptExtractionResponse _value;

  @override
  ConceptExtractionResponse sourceLength(int sourceLength) =>
      this(sourceLength: sourceLength);

  @override
  ConceptExtractionResponse concepts(Object? concepts) =>
      this(concepts: concepts);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ConceptExtractionResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ConceptExtractionResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ConceptExtractionResponse call({
    Object? sourceLength = const $CopyWithPlaceholder(),
    Object? concepts = const $CopyWithPlaceholder(),
  }) {
    return ConceptExtractionResponse(
      sourceLength: sourceLength == const $CopyWithPlaceholder()
          ? _value.sourceLength
          // ignore: cast_nullable_to_non_nullable
          : sourceLength as int,
      concepts: concepts == const $CopyWithPlaceholder()
          ? _value.concepts
          // ignore: cast_nullable_to_non_nullable
          : concepts as Object?,
    );
  }
}

extension $ConceptExtractionResponseCopyWith on ConceptExtractionResponse {
  /// Returns a callable class that can be used as follows: `instanceOfConceptExtractionResponse.copyWith(...)` or like so:`instanceOfConceptExtractionResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ConceptExtractionResponseCWProxy get copyWith =>
      _$ConceptExtractionResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ConceptExtractionResponse _$ConceptExtractionResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'ConceptExtractionResponse',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['source_length', 'concepts']);
    final val = ConceptExtractionResponse(
      sourceLength: $checkedConvert('source_length', (v) => (v as num).toInt()),
      concepts: $checkedConvert('concepts', (v) => v),
    );
    return val;
  },
  fieldKeyMap: const {'sourceLength': 'source_length'},
);

Map<String, dynamic> _$ConceptExtractionResponseToJson(
  ConceptExtractionResponse instance,
) => <String, dynamic>{
  'source_length': instance.sourceLength,
  'concepts': instance.concepts,
};
