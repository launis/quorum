// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'self_test_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$SelfTestResponseCWProxy {
  SelfTestResponse llmStatus(String llmStatus);

  SelfTestResponse dbStatus(String dbStatus);

  SelfTestResponse details(Map<String, Object> details);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SelfTestResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SelfTestResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  SelfTestResponse call({
    String llmStatus,
    String dbStatus,
    Map<String, Object> details,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfSelfTestResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfSelfTestResponse.copyWith.fieldName(...)`
class _$SelfTestResponseCWProxyImpl implements _$SelfTestResponseCWProxy {
  const _$SelfTestResponseCWProxyImpl(this._value);

  final SelfTestResponse _value;

  @override
  SelfTestResponse llmStatus(String llmStatus) => this(llmStatus: llmStatus);

  @override
  SelfTestResponse dbStatus(String dbStatus) => this(dbStatus: dbStatus);

  @override
  SelfTestResponse details(Map<String, Object> details) =>
      this(details: details);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SelfTestResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SelfTestResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  SelfTestResponse call({
    Object? llmStatus = const $CopyWithPlaceholder(),
    Object? dbStatus = const $CopyWithPlaceholder(),
    Object? details = const $CopyWithPlaceholder(),
  }) {
    return SelfTestResponse(
      llmStatus: llmStatus == const $CopyWithPlaceholder()
          ? _value.llmStatus
          // ignore: cast_nullable_to_non_nullable
          : llmStatus as String,
      dbStatus: dbStatus == const $CopyWithPlaceholder()
          ? _value.dbStatus
          // ignore: cast_nullable_to_non_nullable
          : dbStatus as String,
      details: details == const $CopyWithPlaceholder()
          ? _value.details
          // ignore: cast_nullable_to_non_nullable
          : details as Map<String, Object>,
    );
  }
}

extension $SelfTestResponseCopyWith on SelfTestResponse {
  /// Returns a callable class that can be used as follows: `instanceOfSelfTestResponse.copyWith(...)` or like so:`instanceOfSelfTestResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$SelfTestResponseCWProxy get copyWith => _$SelfTestResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SelfTestResponse _$SelfTestResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'SelfTestResponse',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const ['llm_status', 'db_status', 'details'],
        );
        final val = SelfTestResponse(
          llmStatus: $checkedConvert('llm_status', (v) => v as String),
          dbStatus: $checkedConvert('db_status', (v) => v as String),
          details: $checkedConvert(
            'details',
            (v) => (v as Map<String, dynamic>).map(
              (k, e) => MapEntry(k, e as Object),
            ),
          ),
        );
        return val;
      },
      fieldKeyMap: const {'llmStatus': 'llm_status', 'dbStatus': 'db_status'},
    );

Map<String, dynamic> _$SelfTestResponseToJson(SelfTestResponse instance) =>
    <String, dynamic>{
      'llm_status': instance.llmStatus,
      'db_status': instance.dbStatus,
      'details': instance.details,
    };
