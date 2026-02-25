// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'generate_phrases_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$GeneratePhrasesRequestCWProxy {
  GeneratePhrasesRequest language(String? language);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `GeneratePhrasesRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// GeneratePhrasesRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  GeneratePhrasesRequest call({String? language});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfGeneratePhrasesRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfGeneratePhrasesRequest.copyWith.fieldName(...)`
class _$GeneratePhrasesRequestCWProxyImpl
    implements _$GeneratePhrasesRequestCWProxy {
  const _$GeneratePhrasesRequestCWProxyImpl(this._value);

  final GeneratePhrasesRequest _value;

  @override
  GeneratePhrasesRequest language(String? language) => this(language: language);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `GeneratePhrasesRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// GeneratePhrasesRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  GeneratePhrasesRequest call({
    Object? language = const $CopyWithPlaceholder(),
  }) {
    return GeneratePhrasesRequest(
      language: language == const $CopyWithPlaceholder()
          ? _value.language
          // ignore: cast_nullable_to_non_nullable
          : language as String?,
    );
  }
}

extension $GeneratePhrasesRequestCopyWith on GeneratePhrasesRequest {
  /// Returns a callable class that can be used as follows: `instanceOfGeneratePhrasesRequest.copyWith(...)` or like so:`instanceOfGeneratePhrasesRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$GeneratePhrasesRequestCWProxy get copyWith =>
      _$GeneratePhrasesRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

GeneratePhrasesRequest _$GeneratePhrasesRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('GeneratePhrasesRequest', json, ($checkedConvert) {
  final val = GeneratePhrasesRequest(
    language: $checkedConvert('language', (v) => v as String? ?? 'en'),
  );
  return val;
});

Map<String, dynamic> _$GeneratePhrasesRequestToJson(
  GeneratePhrasesRequest instance,
) => <String, dynamic>{'language': ?instance.language};
