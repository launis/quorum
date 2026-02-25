// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'knowledge_ingest_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$KnowledgeIngestResponseCWProxy {
  KnowledgeIngestResponse jobId(String jobId);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `KnowledgeIngestResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// KnowledgeIngestResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  KnowledgeIngestResponse call({String jobId});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfKnowledgeIngestResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfKnowledgeIngestResponse.copyWith.fieldName(...)`
class _$KnowledgeIngestResponseCWProxyImpl
    implements _$KnowledgeIngestResponseCWProxy {
  const _$KnowledgeIngestResponseCWProxyImpl(this._value);

  final KnowledgeIngestResponse _value;

  @override
  KnowledgeIngestResponse jobId(String jobId) => this(jobId: jobId);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `KnowledgeIngestResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// KnowledgeIngestResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  KnowledgeIngestResponse call({Object? jobId = const $CopyWithPlaceholder()}) {
    return KnowledgeIngestResponse(
      jobId: jobId == const $CopyWithPlaceholder()
          ? _value.jobId
          // ignore: cast_nullable_to_non_nullable
          : jobId as String,
    );
  }
}

extension $KnowledgeIngestResponseCopyWith on KnowledgeIngestResponse {
  /// Returns a callable class that can be used as follows: `instanceOfKnowledgeIngestResponse.copyWith(...)` or like so:`instanceOfKnowledgeIngestResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$KnowledgeIngestResponseCWProxy get copyWith =>
      _$KnowledgeIngestResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

KnowledgeIngestResponse _$KnowledgeIngestResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('KnowledgeIngestResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['job_id']);
  final val = KnowledgeIngestResponse(
    jobId: $checkedConvert('job_id', (v) => v as String),
  );
  return val;
}, fieldKeyMap: const {'jobId': 'job_id'});

Map<String, dynamic> _$KnowledgeIngestResponseToJson(
  KnowledgeIngestResponse instance,
) => <String, dynamic>{'job_id': instance.jobId};
