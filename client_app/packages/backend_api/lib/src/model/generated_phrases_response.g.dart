// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'generated_phrases_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$GeneratedPhrasesResponseCWProxy {
  GeneratedPhrasesResponse status(String status);

  GeneratedPhrasesResponse message(String message);

  GeneratedPhrasesResponse addedPhrases(List<String> addedPhrases);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `GeneratedPhrasesResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// GeneratedPhrasesResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  GeneratedPhrasesResponse call({
    String status,
    String message,
    List<String> addedPhrases,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfGeneratedPhrasesResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfGeneratedPhrasesResponse.copyWith.fieldName(...)`
class _$GeneratedPhrasesResponseCWProxyImpl
    implements _$GeneratedPhrasesResponseCWProxy {
  const _$GeneratedPhrasesResponseCWProxyImpl(this._value);

  final GeneratedPhrasesResponse _value;

  @override
  GeneratedPhrasesResponse status(String status) => this(status: status);

  @override
  GeneratedPhrasesResponse message(String message) => this(message: message);

  @override
  GeneratedPhrasesResponse addedPhrases(List<String> addedPhrases) =>
      this(addedPhrases: addedPhrases);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `GeneratedPhrasesResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// GeneratedPhrasesResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  GeneratedPhrasesResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? message = const $CopyWithPlaceholder(),
    Object? addedPhrases = const $CopyWithPlaceholder(),
  }) {
    return GeneratedPhrasesResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      message: message == const $CopyWithPlaceholder()
          ? _value.message
          // ignore: cast_nullable_to_non_nullable
          : message as String,
      addedPhrases: addedPhrases == const $CopyWithPlaceholder()
          ? _value.addedPhrases
          // ignore: cast_nullable_to_non_nullable
          : addedPhrases as List<String>,
    );
  }
}

extension $GeneratedPhrasesResponseCopyWith on GeneratedPhrasesResponse {
  /// Returns a callable class that can be used as follows: `instanceOfGeneratedPhrasesResponse.copyWith(...)` or like so:`instanceOfGeneratedPhrasesResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$GeneratedPhrasesResponseCWProxy get copyWith =>
      _$GeneratedPhrasesResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

GeneratedPhrasesResponse _$GeneratedPhrasesResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'GeneratedPhrasesResponse',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const ['status', 'message', 'added_phrases'],
    );
    final val = GeneratedPhrasesResponse(
      status: $checkedConvert('status', (v) => v as String),
      message: $checkedConvert('message', (v) => v as String),
      addedPhrases: $checkedConvert(
        'added_phrases',
        (v) => (v as List<dynamic>).map((e) => e as String).toList(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {'addedPhrases': 'added_phrases'},
);

Map<String, dynamic> _$GeneratedPhrasesResponseToJson(
  GeneratedPhrasesResponse instance,
) => <String, dynamic>{
  'status': instance.status,
  'message': instance.message,
  'added_phrases': instance.addedPhrases,
};
