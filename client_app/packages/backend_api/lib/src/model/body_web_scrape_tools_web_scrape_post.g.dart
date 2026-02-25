// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'body_web_scrape_tools_web_scrape_post.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$BodyWebScrapeToolsWebScrapePostCWProxy {
  BodyWebScrapeToolsWebScrapePost url(String url);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BodyWebScrapeToolsWebScrapePost(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BodyWebScrapeToolsWebScrapePost(...).copyWith(id: 12, name: "My name")
  /// ````
  BodyWebScrapeToolsWebScrapePost call({String url});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfBodyWebScrapeToolsWebScrapePost.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfBodyWebScrapeToolsWebScrapePost.copyWith.fieldName(...)`
class _$BodyWebScrapeToolsWebScrapePostCWProxyImpl
    implements _$BodyWebScrapeToolsWebScrapePostCWProxy {
  const _$BodyWebScrapeToolsWebScrapePostCWProxyImpl(this._value);

  final BodyWebScrapeToolsWebScrapePost _value;

  @override
  BodyWebScrapeToolsWebScrapePost url(String url) => this(url: url);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BodyWebScrapeToolsWebScrapePost(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BodyWebScrapeToolsWebScrapePost(...).copyWith(id: 12, name: "My name")
  /// ````
  BodyWebScrapeToolsWebScrapePost call({
    Object? url = const $CopyWithPlaceholder(),
  }) {
    return BodyWebScrapeToolsWebScrapePost(
      url: url == const $CopyWithPlaceholder()
          ? _value.url
          // ignore: cast_nullable_to_non_nullable
          : url as String,
    );
  }
}

extension $BodyWebScrapeToolsWebScrapePostCopyWith
    on BodyWebScrapeToolsWebScrapePost {
  /// Returns a callable class that can be used as follows: `instanceOfBodyWebScrapeToolsWebScrapePost.copyWith(...)` or like so:`instanceOfBodyWebScrapeToolsWebScrapePost.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$BodyWebScrapeToolsWebScrapePostCWProxy get copyWith =>
      _$BodyWebScrapeToolsWebScrapePostCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BodyWebScrapeToolsWebScrapePost _$BodyWebScrapeToolsWebScrapePostFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('BodyWebScrapeToolsWebScrapePost', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['url']);
  final val = BodyWebScrapeToolsWebScrapePost(
    url: $checkedConvert('url', (v) => v as String),
  );
  return val;
});

Map<String, dynamic> _$BodyWebScrapeToolsWebScrapePostToJson(
  BodyWebScrapeToolsWebScrapePost instance,
) => <String, dynamic>{'url': instance.url};
