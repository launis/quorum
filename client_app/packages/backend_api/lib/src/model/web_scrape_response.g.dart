// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'web_scrape_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$WebScrapeResponseCWProxy {
  WebScrapeResponse url(String url);

  WebScrapeResponse content(String content);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WebScrapeResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WebScrapeResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  WebScrapeResponse call({String url, String content});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfWebScrapeResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfWebScrapeResponse.copyWith.fieldName(...)`
class _$WebScrapeResponseCWProxyImpl implements _$WebScrapeResponseCWProxy {
  const _$WebScrapeResponseCWProxyImpl(this._value);

  final WebScrapeResponse _value;

  @override
  WebScrapeResponse url(String url) => this(url: url);

  @override
  WebScrapeResponse content(String content) => this(content: content);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WebScrapeResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WebScrapeResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  WebScrapeResponse call({
    Object? url = const $CopyWithPlaceholder(),
    Object? content = const $CopyWithPlaceholder(),
  }) {
    return WebScrapeResponse(
      url: url == const $CopyWithPlaceholder()
          ? _value.url
          // ignore: cast_nullable_to_non_nullable
          : url as String,
      content: content == const $CopyWithPlaceholder()
          ? _value.content
          // ignore: cast_nullable_to_non_nullable
          : content as String,
    );
  }
}

extension $WebScrapeResponseCopyWith on WebScrapeResponse {
  /// Returns a callable class that can be used as follows: `instanceOfWebScrapeResponse.copyWith(...)` or like so:`instanceOfWebScrapeResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$WebScrapeResponseCWProxy get copyWith =>
      _$WebScrapeResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WebScrapeResponse _$WebScrapeResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('WebScrapeResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['url', 'content']);
      final val = WebScrapeResponse(
        url: $checkedConvert('url', (v) => v as String),
        content: $checkedConvert('content', (v) => v as String),
      );
      return val;
    });

Map<String, dynamic> _$WebScrapeResponseToJson(WebScrapeResponse instance) =>
    <String, dynamic>{'url': instance.url, 'content': instance.content};
