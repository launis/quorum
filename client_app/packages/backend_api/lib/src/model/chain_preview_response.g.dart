// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'chain_preview_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ChainPreviewResponseCWProxy {
  ChainPreviewResponse markdownContent(String markdownContent);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ChainPreviewResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ChainPreviewResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ChainPreviewResponse call({String markdownContent});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfChainPreviewResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfChainPreviewResponse.copyWith.fieldName(...)`
class _$ChainPreviewResponseCWProxyImpl
    implements _$ChainPreviewResponseCWProxy {
  const _$ChainPreviewResponseCWProxyImpl(this._value);

  final ChainPreviewResponse _value;

  @override
  ChainPreviewResponse markdownContent(String markdownContent) =>
      this(markdownContent: markdownContent);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ChainPreviewResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ChainPreviewResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ChainPreviewResponse call({
    Object? markdownContent = const $CopyWithPlaceholder(),
  }) {
    return ChainPreviewResponse(
      markdownContent: markdownContent == const $CopyWithPlaceholder()
          ? _value.markdownContent
          // ignore: cast_nullable_to_non_nullable
          : markdownContent as String,
    );
  }
}

extension $ChainPreviewResponseCopyWith on ChainPreviewResponse {
  /// Returns a callable class that can be used as follows: `instanceOfChainPreviewResponse.copyWith(...)` or like so:`instanceOfChainPreviewResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ChainPreviewResponseCWProxy get copyWith =>
      _$ChainPreviewResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ChainPreviewResponse _$ChainPreviewResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'ChainPreviewResponse',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['markdown_content']);
    final val = ChainPreviewResponse(
      markdownContent: $checkedConvert('markdown_content', (v) => v as String),
    );
    return val;
  },
  fieldKeyMap: const {'markdownContent': 'markdown_content'},
);

Map<String, dynamic> _$ChainPreviewResponseToJson(
  ChainPreviewResponse instance,
) => <String, dynamic>{'markdown_content': instance.markdownContent};
