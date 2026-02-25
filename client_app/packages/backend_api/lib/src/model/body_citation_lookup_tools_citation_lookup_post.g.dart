// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'body_citation_lookup_tools_citation_lookup_post.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$BodyCitationLookupToolsCitationLookupPostCWProxy {
  BodyCitationLookupToolsCitationLookupPost queries(List<String> queries);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BodyCitationLookupToolsCitationLookupPost(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BodyCitationLookupToolsCitationLookupPost(...).copyWith(id: 12, name: "My name")
  /// ````
  BodyCitationLookupToolsCitationLookupPost call({List<String> queries});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfBodyCitationLookupToolsCitationLookupPost.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfBodyCitationLookupToolsCitationLookupPost.copyWith.fieldName(...)`
class _$BodyCitationLookupToolsCitationLookupPostCWProxyImpl
    implements _$BodyCitationLookupToolsCitationLookupPostCWProxy {
  const _$BodyCitationLookupToolsCitationLookupPostCWProxyImpl(this._value);

  final BodyCitationLookupToolsCitationLookupPost _value;

  @override
  BodyCitationLookupToolsCitationLookupPost queries(List<String> queries) =>
      this(queries: queries);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BodyCitationLookupToolsCitationLookupPost(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BodyCitationLookupToolsCitationLookupPost(...).copyWith(id: 12, name: "My name")
  /// ````
  BodyCitationLookupToolsCitationLookupPost call({
    Object? queries = const $CopyWithPlaceholder(),
  }) {
    return BodyCitationLookupToolsCitationLookupPost(
      queries: queries == const $CopyWithPlaceholder()
          ? _value.queries
          // ignore: cast_nullable_to_non_nullable
          : queries as List<String>,
    );
  }
}

extension $BodyCitationLookupToolsCitationLookupPostCopyWith
    on BodyCitationLookupToolsCitationLookupPost {
  /// Returns a callable class that can be used as follows: `instanceOfBodyCitationLookupToolsCitationLookupPost.copyWith(...)` or like so:`instanceOfBodyCitationLookupToolsCitationLookupPost.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$BodyCitationLookupToolsCitationLookupPostCWProxy get copyWith =>
      _$BodyCitationLookupToolsCitationLookupPostCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BodyCitationLookupToolsCitationLookupPost
_$BodyCitationLookupToolsCitationLookupPostFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('BodyCitationLookupToolsCitationLookupPost', json, (
  $checkedConvert,
) {
  $checkKeys(json, requiredKeys: const ['queries']);
  final val = BodyCitationLookupToolsCitationLookupPost(
    queries: $checkedConvert(
      'queries',
      (v) => (v as List<dynamic>).map((e) => e as String).toList(),
    ),
  );
  return val;
});

Map<String, dynamic> _$BodyCitationLookupToolsCitationLookupPostToJson(
  BodyCitationLookupToolsCitationLookupPost instance,
) => <String, dynamic>{'queries': instance.queries};
