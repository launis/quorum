// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'batch_completion_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$BatchCompletionRequestCWProxy {
  BatchCompletionRequest requests(List<CompletionRequest> requests);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BatchCompletionRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BatchCompletionRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  BatchCompletionRequest call({List<CompletionRequest> requests});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfBatchCompletionRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfBatchCompletionRequest.copyWith.fieldName(...)`
class _$BatchCompletionRequestCWProxyImpl
    implements _$BatchCompletionRequestCWProxy {
  const _$BatchCompletionRequestCWProxyImpl(this._value);

  final BatchCompletionRequest _value;

  @override
  BatchCompletionRequest requests(List<CompletionRequest> requests) =>
      this(requests: requests);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BatchCompletionRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BatchCompletionRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  BatchCompletionRequest call({
    Object? requests = const $CopyWithPlaceholder(),
  }) {
    return BatchCompletionRequest(
      requests: requests == const $CopyWithPlaceholder()
          ? _value.requests
          // ignore: cast_nullable_to_non_nullable
          : requests as List<CompletionRequest>,
    );
  }
}

extension $BatchCompletionRequestCopyWith on BatchCompletionRequest {
  /// Returns a callable class that can be used as follows: `instanceOfBatchCompletionRequest.copyWith(...)` or like so:`instanceOfBatchCompletionRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$BatchCompletionRequestCWProxy get copyWith =>
      _$BatchCompletionRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BatchCompletionRequest _$BatchCompletionRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('BatchCompletionRequest', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['requests']);
  final val = BatchCompletionRequest(
    requests: $checkedConvert(
      'requests',
      (v) => (v as List<dynamic>)
          .map((e) => CompletionRequest.fromJson(e as Map<String, dynamic>))
          .toList(),
    ),
  );
  return val;
});

Map<String, dynamic> _$BatchCompletionRequestToJson(
  BatchCompletionRequest instance,
) => <String, dynamic>{
  'requests': instance.requests.map((e) => e.toJson()).toList(),
};
