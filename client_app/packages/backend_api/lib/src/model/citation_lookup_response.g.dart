// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'citation_lookup_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$CitationLookupResponseCWProxy {
  CitationLookupResponse results(
    Map<String, List<Map<String, Object>>> results,
  );

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CitationLookupResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CitationLookupResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  CitationLookupResponse call({Map<String, List<Map<String, Object>>> results});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfCitationLookupResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfCitationLookupResponse.copyWith.fieldName(...)`
class _$CitationLookupResponseCWProxyImpl
    implements _$CitationLookupResponseCWProxy {
  const _$CitationLookupResponseCWProxyImpl(this._value);

  final CitationLookupResponse _value;

  @override
  CitationLookupResponse results(
    Map<String, List<Map<String, Object>>> results,
  ) => this(results: results);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CitationLookupResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CitationLookupResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  CitationLookupResponse call({
    Object? results = const $CopyWithPlaceholder(),
  }) {
    return CitationLookupResponse(
      results: results == const $CopyWithPlaceholder()
          ? _value.results
          // ignore: cast_nullable_to_non_nullable
          : results as Map<String, List<Map<String, Object>>>,
    );
  }
}

extension $CitationLookupResponseCopyWith on CitationLookupResponse {
  /// Returns a callable class that can be used as follows: `instanceOfCitationLookupResponse.copyWith(...)` or like so:`instanceOfCitationLookupResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$CitationLookupResponseCWProxy get copyWith =>
      _$CitationLookupResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CitationLookupResponse _$CitationLookupResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('CitationLookupResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['results']);
  final val = CitationLookupResponse(
    results: $checkedConvert(
      'results',
      (v) => (v as Map<String, dynamic>).map(
        (k, e) => MapEntry(
          k,
          (e as List<dynamic>)
              .map(
                (e) => (e as Map<String, dynamic>).map(
                  (k, e) => MapEntry(k, e as Object),
                ),
              )
              .toList(),
        ),
      ),
    ),
  );
  return val;
});

Map<String, dynamic> _$CitationLookupResponseToJson(
  CitationLookupResponse instance,
) => <String, dynamic>{'results': instance.results};
