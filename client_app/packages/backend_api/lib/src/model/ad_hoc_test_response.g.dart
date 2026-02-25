// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ad_hoc_test_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AdHocTestResponseCWProxy {
  AdHocTestResponse content(String content);

  AdHocTestResponse latencyMs(num latencyMs);

  AdHocTestResponse status(String status);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AdHocTestResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AdHocTestResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AdHocTestResponse call({String content, num latencyMs, String status});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAdHocTestResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAdHocTestResponse.copyWith.fieldName(...)`
class _$AdHocTestResponseCWProxyImpl implements _$AdHocTestResponseCWProxy {
  const _$AdHocTestResponseCWProxyImpl(this._value);

  final AdHocTestResponse _value;

  @override
  AdHocTestResponse content(String content) => this(content: content);

  @override
  AdHocTestResponse latencyMs(num latencyMs) => this(latencyMs: latencyMs);

  @override
  AdHocTestResponse status(String status) => this(status: status);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AdHocTestResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AdHocTestResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AdHocTestResponse call({
    Object? content = const $CopyWithPlaceholder(),
    Object? latencyMs = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
  }) {
    return AdHocTestResponse(
      content: content == const $CopyWithPlaceholder()
          ? _value.content
          // ignore: cast_nullable_to_non_nullable
          : content as String,
      latencyMs: latencyMs == const $CopyWithPlaceholder()
          ? _value.latencyMs
          // ignore: cast_nullable_to_non_nullable
          : latencyMs as num,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
    );
  }
}

extension $AdHocTestResponseCopyWith on AdHocTestResponse {
  /// Returns a callable class that can be used as follows: `instanceOfAdHocTestResponse.copyWith(...)` or like so:`instanceOfAdHocTestResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AdHocTestResponseCWProxy get copyWith =>
      _$AdHocTestResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AdHocTestResponse _$AdHocTestResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('AdHocTestResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['content', 'latency_ms', 'status']);
      final val = AdHocTestResponse(
        content: $checkedConvert('content', (v) => v as String),
        latencyMs: $checkedConvert('latency_ms', (v) => v as num),
        status: $checkedConvert('status', (v) => v as String),
      );
      return val;
    }, fieldKeyMap: const {'latencyMs': 'latency_ms'});

Map<String, dynamic> _$AdHocTestResponseToJson(AdHocTestResponse instance) =>
    <String, dynamic>{
      'content': instance.content,
      'latency_ms': instance.latencyMs,
      'status': instance.status,
    };
