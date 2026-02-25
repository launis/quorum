// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'banned_phrase_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$BannedPhraseRequestCWProxy {
  BannedPhraseRequest phrase(String phrase);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BannedPhraseRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BannedPhraseRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  BannedPhraseRequest call({String phrase});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfBannedPhraseRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfBannedPhraseRequest.copyWith.fieldName(...)`
class _$BannedPhraseRequestCWProxyImpl implements _$BannedPhraseRequestCWProxy {
  const _$BannedPhraseRequestCWProxyImpl(this._value);

  final BannedPhraseRequest _value;

  @override
  BannedPhraseRequest phrase(String phrase) => this(phrase: phrase);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BannedPhraseRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BannedPhraseRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  BannedPhraseRequest call({Object? phrase = const $CopyWithPlaceholder()}) {
    return BannedPhraseRequest(
      phrase: phrase == const $CopyWithPlaceholder()
          ? _value.phrase
          // ignore: cast_nullable_to_non_nullable
          : phrase as String,
    );
  }
}

extension $BannedPhraseRequestCopyWith on BannedPhraseRequest {
  /// Returns a callable class that can be used as follows: `instanceOfBannedPhraseRequest.copyWith(...)` or like so:`instanceOfBannedPhraseRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$BannedPhraseRequestCWProxy get copyWith =>
      _$BannedPhraseRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BannedPhraseRequest _$BannedPhraseRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate('BannedPhraseRequest', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['phrase']);
      final val = BannedPhraseRequest(
        phrase: $checkedConvert('phrase', (v) => v as String),
      );
      return val;
    });

Map<String, dynamic> _$BannedPhraseRequestToJson(
  BannedPhraseRequest instance,
) => <String, dynamic>{'phrase': instance.phrase};
