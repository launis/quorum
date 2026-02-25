// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'knowledge_status_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$KnowledgeStatusResponseCWProxy {
  KnowledgeStatusResponse hasDocuments(bool hasDocuments);

  KnowledgeStatusResponse documentCount(int documentCount);

  KnowledgeStatusResponse precedentCount(int precedentCount);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `KnowledgeStatusResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// KnowledgeStatusResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  KnowledgeStatusResponse call({
    bool hasDocuments,
    int documentCount,
    int precedentCount,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfKnowledgeStatusResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfKnowledgeStatusResponse.copyWith.fieldName(...)`
class _$KnowledgeStatusResponseCWProxyImpl
    implements _$KnowledgeStatusResponseCWProxy {
  const _$KnowledgeStatusResponseCWProxyImpl(this._value);

  final KnowledgeStatusResponse _value;

  @override
  KnowledgeStatusResponse hasDocuments(bool hasDocuments) =>
      this(hasDocuments: hasDocuments);

  @override
  KnowledgeStatusResponse documentCount(int documentCount) =>
      this(documentCount: documentCount);

  @override
  KnowledgeStatusResponse precedentCount(int precedentCount) =>
      this(precedentCount: precedentCount);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `KnowledgeStatusResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// KnowledgeStatusResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  KnowledgeStatusResponse call({
    Object? hasDocuments = const $CopyWithPlaceholder(),
    Object? documentCount = const $CopyWithPlaceholder(),
    Object? precedentCount = const $CopyWithPlaceholder(),
  }) {
    return KnowledgeStatusResponse(
      hasDocuments: hasDocuments == const $CopyWithPlaceholder()
          ? _value.hasDocuments
          // ignore: cast_nullable_to_non_nullable
          : hasDocuments as bool,
      documentCount: documentCount == const $CopyWithPlaceholder()
          ? _value.documentCount
          // ignore: cast_nullable_to_non_nullable
          : documentCount as int,
      precedentCount: precedentCount == const $CopyWithPlaceholder()
          ? _value.precedentCount
          // ignore: cast_nullable_to_non_nullable
          : precedentCount as int,
    );
  }
}

extension $KnowledgeStatusResponseCopyWith on KnowledgeStatusResponse {
  /// Returns a callable class that can be used as follows: `instanceOfKnowledgeStatusResponse.copyWith(...)` or like so:`instanceOfKnowledgeStatusResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$KnowledgeStatusResponseCWProxy get copyWith =>
      _$KnowledgeStatusResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

KnowledgeStatusResponse _$KnowledgeStatusResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'KnowledgeStatusResponse',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const [
        'has_documents',
        'document_count',
        'precedent_count',
      ],
    );
    final val = KnowledgeStatusResponse(
      hasDocuments: $checkedConvert('has_documents', (v) => v as bool),
      documentCount: $checkedConvert(
        'document_count',
        (v) => (v as num).toInt(),
      ),
      precedentCount: $checkedConvert(
        'precedent_count',
        (v) => (v as num).toInt(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'hasDocuments': 'has_documents',
    'documentCount': 'document_count',
    'precedentCount': 'precedent_count',
  },
);

Map<String, dynamic> _$KnowledgeStatusResponseToJson(
  KnowledgeStatusResponse instance,
) => <String, dynamic>{
  'has_documents': instance.hasDocuments,
  'document_count': instance.documentCount,
  'precedent_count': instance.precedentCount,
};
