// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'batch_llm_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$BatchLLMResponseCWProxy {
  BatchLLMResponse results(List<Map<String, Object>> results);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BatchLLMResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BatchLLMResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  BatchLLMResponse call({List<Map<String, Object>> results});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfBatchLLMResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfBatchLLMResponse.copyWith.fieldName(...)`
class _$BatchLLMResponseCWProxyImpl implements _$BatchLLMResponseCWProxy {
  const _$BatchLLMResponseCWProxyImpl(this._value);

  final BatchLLMResponse _value;

  @override
  BatchLLMResponse results(List<Map<String, Object>> results) =>
      this(results: results);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BatchLLMResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BatchLLMResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  BatchLLMResponse call({Object? results = const $CopyWithPlaceholder()}) {
    return BatchLLMResponse(
      results: results == const $CopyWithPlaceholder()
          ? _value.results
          // ignore: cast_nullable_to_non_nullable
          : results as List<Map<String, Object>>,
    );
  }
}

extension $BatchLLMResponseCopyWith on BatchLLMResponse {
  /// Returns a callable class that can be used as follows: `instanceOfBatchLLMResponse.copyWith(...)` or like so:`instanceOfBatchLLMResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$BatchLLMResponseCWProxy get copyWith => _$BatchLLMResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BatchLLMResponse _$BatchLLMResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('BatchLLMResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['results']);
      final val = BatchLLMResponse(
        results: $checkedConvert(
          'results',
          (v) => (v as List<dynamic>)
              .map(
                (e) => (e as Map<String, dynamic>).map(
                  (k, e) => MapEntry(k, e as Object),
                ),
              )
              .toList(),
        ),
      );
      return val;
    });

Map<String, dynamic> _$BatchLLMResponseToJson(BatchLLMResponse instance) =>
    <String, dynamic>{'results': instance.results};
