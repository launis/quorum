// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'banned_phrase_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$BannedPhraseResponseCWProxy {
  BannedPhraseResponse status(String status);

  BannedPhraseResponse phrase(String phrase);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BannedPhraseResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BannedPhraseResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  BannedPhraseResponse call({String status, String phrase});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfBannedPhraseResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfBannedPhraseResponse.copyWith.fieldName(...)`
class _$BannedPhraseResponseCWProxyImpl
    implements _$BannedPhraseResponseCWProxy {
  const _$BannedPhraseResponseCWProxyImpl(this._value);

  final BannedPhraseResponse _value;

  @override
  BannedPhraseResponse status(String status) => this(status: status);

  @override
  BannedPhraseResponse phrase(String phrase) => this(phrase: phrase);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BannedPhraseResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BannedPhraseResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  BannedPhraseResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? phrase = const $CopyWithPlaceholder(),
  }) {
    return BannedPhraseResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      phrase: phrase == const $CopyWithPlaceholder()
          ? _value.phrase
          // ignore: cast_nullable_to_non_nullable
          : phrase as String,
    );
  }
}

extension $BannedPhraseResponseCopyWith on BannedPhraseResponse {
  /// Returns a callable class that can be used as follows: `instanceOfBannedPhraseResponse.copyWith(...)` or like so:`instanceOfBannedPhraseResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$BannedPhraseResponseCWProxy get copyWith =>
      _$BannedPhraseResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BannedPhraseResponse _$BannedPhraseResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('BannedPhraseResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['status', 'phrase']);
  final val = BannedPhraseResponse(
    status: $checkedConvert('status', (v) => v as String),
    phrase: $checkedConvert('phrase', (v) => v as String),
  );
  return val;
});

Map<String, dynamic> _$BannedPhraseResponseToJson(
  BannedPhraseResponse instance,
) => <String, dynamic>{'status': instance.status, 'phrase': instance.phrase};
