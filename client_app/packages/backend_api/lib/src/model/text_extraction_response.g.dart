// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'text_extraction_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$TextExtractionResponseCWProxy {
  TextExtractionResponse filename(String? filename);

  TextExtractionResponse text(String text);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TextExtractionResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TextExtractionResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  TextExtractionResponse call({String? filename, String text});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfTextExtractionResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfTextExtractionResponse.copyWith.fieldName(...)`
class _$TextExtractionResponseCWProxyImpl
    implements _$TextExtractionResponseCWProxy {
  const _$TextExtractionResponseCWProxyImpl(this._value);

  final TextExtractionResponse _value;

  @override
  TextExtractionResponse filename(String? filename) => this(filename: filename);

  @override
  TextExtractionResponse text(String text) => this(text: text);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TextExtractionResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TextExtractionResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  TextExtractionResponse call({
    Object? filename = const $CopyWithPlaceholder(),
    Object? text = const $CopyWithPlaceholder(),
  }) {
    return TextExtractionResponse(
      filename: filename == const $CopyWithPlaceholder()
          ? _value.filename
          // ignore: cast_nullable_to_non_nullable
          : filename as String?,
      text: text == const $CopyWithPlaceholder()
          ? _value.text
          // ignore: cast_nullable_to_non_nullable
          : text as String,
    );
  }
}

extension $TextExtractionResponseCopyWith on TextExtractionResponse {
  /// Returns a callable class that can be used as follows: `instanceOfTextExtractionResponse.copyWith(...)` or like so:`instanceOfTextExtractionResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$TextExtractionResponseCWProxy get copyWith =>
      _$TextExtractionResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TextExtractionResponse _$TextExtractionResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('TextExtractionResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['text']);
  final val = TextExtractionResponse(
    filename: $checkedConvert('filename', (v) => v as String?),
    text: $checkedConvert('text', (v) => v as String),
  );
  return val;
});

Map<String, dynamic> _$TextExtractionResponseToJson(
  TextExtractionResponse instance,
) => <String, dynamic>{'filename': ?instance.filename, 'text': instance.text};
