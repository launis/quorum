// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ingest_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$IngestRequestCWProxy {
  IngestRequest filePath(String? filePath);

  IngestRequest resetDb(bool? resetDb);

  IngestRequest modelStrategy(String? modelStrategy);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `IngestRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// IngestRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  IngestRequest call({String? filePath, bool? resetDb, String? modelStrategy});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfIngestRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfIngestRequest.copyWith.fieldName(...)`
class _$IngestRequestCWProxyImpl implements _$IngestRequestCWProxy {
  const _$IngestRequestCWProxyImpl(this._value);

  final IngestRequest _value;

  @override
  IngestRequest filePath(String? filePath) => this(filePath: filePath);

  @override
  IngestRequest resetDb(bool? resetDb) => this(resetDb: resetDb);

  @override
  IngestRequest modelStrategy(String? modelStrategy) =>
      this(modelStrategy: modelStrategy);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `IngestRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// IngestRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  IngestRequest call({
    Object? filePath = const $CopyWithPlaceholder(),
    Object? resetDb = const $CopyWithPlaceholder(),
    Object? modelStrategy = const $CopyWithPlaceholder(),
  }) {
    return IngestRequest(
      filePath: filePath == const $CopyWithPlaceholder()
          ? _value.filePath
          // ignore: cast_nullable_to_non_nullable
          : filePath as String?,
      resetDb: resetDb == const $CopyWithPlaceholder()
          ? _value.resetDb
          // ignore: cast_nullable_to_non_nullable
          : resetDb as bool?,
      modelStrategy: modelStrategy == const $CopyWithPlaceholder()
          ? _value.modelStrategy
          // ignore: cast_nullable_to_non_nullable
          : modelStrategy as String?,
    );
  }
}

extension $IngestRequestCopyWith on IngestRequest {
  /// Returns a callable class that can be used as follows: `instanceOfIngestRequest.copyWith(...)` or like so:`instanceOfIngestRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$IngestRequestCWProxy get copyWith => _$IngestRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

IngestRequest _$IngestRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'IngestRequest',
      json,
      ($checkedConvert) {
        final val = IngestRequest(
          filePath: $checkedConvert(
            'file_path',
            (v) => v as String? ?? 'data/Holistinen Mestaruus.docx',
          ),
          resetDb: $checkedConvert('reset_db', (v) => v as bool? ?? false),
          modelStrategy: $checkedConvert('model_strategy', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'filePath': 'file_path',
        'resetDb': 'reset_db',
        'modelStrategy': 'model_strategy',
      },
    );

Map<String, dynamic> _$IngestRequestToJson(IngestRequest instance) =>
    <String, dynamic>{
      'file_path': ?instance.filePath,
      'reset_db': ?instance.resetDb,
      'model_strategy': ?instance.modelStrategy,
    };
