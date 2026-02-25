// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'playground_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PlaygroundResponseCWProxy {
  PlaygroundResponse content(String content);

  PlaygroundResponse usage(Map<String, Object>? usage);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PlaygroundResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PlaygroundResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PlaygroundResponse call({String content, Map<String, Object>? usage});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPlaygroundResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPlaygroundResponse.copyWith.fieldName(...)`
class _$PlaygroundResponseCWProxyImpl implements _$PlaygroundResponseCWProxy {
  const _$PlaygroundResponseCWProxyImpl(this._value);

  final PlaygroundResponse _value;

  @override
  PlaygroundResponse content(String content) => this(content: content);

  @override
  PlaygroundResponse usage(Map<String, Object>? usage) => this(usage: usage);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PlaygroundResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PlaygroundResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PlaygroundResponse call({
    Object? content = const $CopyWithPlaceholder(),
    Object? usage = const $CopyWithPlaceholder(),
  }) {
    return PlaygroundResponse(
      content: content == const $CopyWithPlaceholder()
          ? _value.content
          // ignore: cast_nullable_to_non_nullable
          : content as String,
      usage: usage == const $CopyWithPlaceholder()
          ? _value.usage
          // ignore: cast_nullable_to_non_nullable
          : usage as Map<String, Object>?,
    );
  }
}

extension $PlaygroundResponseCopyWith on PlaygroundResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPlaygroundResponse.copyWith(...)` or like so:`instanceOfPlaygroundResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PlaygroundResponseCWProxy get copyWith =>
      _$PlaygroundResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PlaygroundResponse _$PlaygroundResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('PlaygroundResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['content']);
      final val = PlaygroundResponse(
        content: $checkedConvert('content', (v) => v as String),
        usage: $checkedConvert(
          'usage',
          (v) => (v as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, e as Object),
          ),
        ),
      );
      return val;
    });

Map<String, dynamic> _$PlaygroundResponseToJson(PlaygroundResponse instance) =>
    <String, dynamic>{'content': instance.content, 'usage': ?instance.usage};
