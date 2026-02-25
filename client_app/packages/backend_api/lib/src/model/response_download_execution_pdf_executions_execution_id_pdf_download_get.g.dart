// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'response_download_execution_pdf_executions_execution_id_pdf_download_get.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGetCWProxy {
  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet status(
    String status,
  );

  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet exists(
    bool exists,
  );

  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet localPath(
    String? localPath,
  );

  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet message(
    String message,
  );

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet(...).copyWith(id: 12, name: "My name")
  /// ````
  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet call({
    String status,
    bool exists,
    String? localPath,
    String message,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet.copyWith.fieldName(...)`
class _$ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGetCWProxyImpl
    implements
        _$ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGetCWProxy {
  const _$ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGetCWProxyImpl(
    this._value,
  );

  final ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet _value;

  @override
  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet status(
    String status,
  ) => this(status: status);

  @override
  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet exists(
    bool exists,
  ) => this(exists: exists);

  @override
  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet localPath(
    String? localPath,
  ) => this(localPath: localPath);

  @override
  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet message(
    String message,
  ) => this(message: message);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet(...).copyWith(id: 12, name: "My name")
  /// ````
  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet call({
    Object? status = const $CopyWithPlaceholder(),
    Object? exists = const $CopyWithPlaceholder(),
    Object? localPath = const $CopyWithPlaceholder(),
    Object? message = const $CopyWithPlaceholder(),
  }) {
    return ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      exists: exists == const $CopyWithPlaceholder()
          ? _value.exists
          // ignore: cast_nullable_to_non_nullable
          : exists as bool,
      localPath: localPath == const $CopyWithPlaceholder()
          ? _value.localPath
          // ignore: cast_nullable_to_non_nullable
          : localPath as String?,
      message: message == const $CopyWithPlaceholder()
          ? _value.message
          // ignore: cast_nullable_to_non_nullable
          : message as String,
    );
  }
}

extension $ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGetCopyWith
    on ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet {
  /// Returns a callable class that can be used as follows: `instanceOfResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet.copyWith(...)` or like so:`instanceOfResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGetCWProxy
  get copyWith =>
      _$ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGetCWProxyImpl(
        this,
      );
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet
_$ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGetFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['status', 'exists', 'message']);
    final val = ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet(
      status: $checkedConvert('status', (v) => v as String),
      exists: $checkedConvert('exists', (v) => v as bool),
      localPath: $checkedConvert('local_path', (v) => v as String?),
      message: $checkedConvert('message', (v) => v as String),
    );
    return val;
  },
  fieldKeyMap: const {'localPath': 'local_path'},
);

Map<String, dynamic>
_$ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGetToJson(
  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet instance,
) => <String, dynamic>{
  'status': instance.status,
  'exists': instance.exists,
  'local_path': ?instance.localPath,
  'message': instance.message,
};
