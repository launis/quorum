// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'llm_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$LLMResponseCWProxy {
  LLMResponse result(Object? result);

  LLMResponse usage(dynamic usage);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `LLMResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// LLMResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  LLMResponse call({Object? result, dynamic usage});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfLLMResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfLLMResponse.copyWith.fieldName(...)`
class _$LLMResponseCWProxyImpl implements _$LLMResponseCWProxy {
  const _$LLMResponseCWProxyImpl(this._value);

  final LLMResponse _value;

  @override
  LLMResponse result(Object? result) => this(result: result);

  @override
  LLMResponse usage(dynamic usage) => this(usage: usage);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `LLMResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// LLMResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  LLMResponse call({
    Object? result = const $CopyWithPlaceholder(),
    Object? usage = const $CopyWithPlaceholder(),
  }) {
    return LLMResponse(
      result: result == const $CopyWithPlaceholder()
          ? _value.result
          // ignore: cast_nullable_to_non_nullable
          : result as Object?,
      usage: usage == const $CopyWithPlaceholder()
          ? _value.usage
          // ignore: cast_nullable_to_non_nullable
          : usage as dynamic,
    );
  }
}

extension $LLMResponseCopyWith on LLMResponse {
  /// Returns a callable class that can be used as follows: `instanceOfLLMResponse.copyWith(...)` or like so:`instanceOfLLMResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$LLMResponseCWProxy get copyWith => _$LLMResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

LLMResponse _$LLMResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('LLMResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['result']);
      final val = LLMResponse(
        result: $checkedConvert('result', (v) => v),
        usage: $checkedConvert('usage', (v) => v),
      );
      return val;
    });

Map<String, dynamic> _$LLMResponseToJson(LLMResponse instance) =>
    <String, dynamic>{'result': instance.result, 'usage': ?instance.usage};
