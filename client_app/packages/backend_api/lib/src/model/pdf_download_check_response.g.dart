// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pdf_download_check_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PDFDownloadCheckResponseCWProxy {
  PDFDownloadCheckResponse status(String status);

  PDFDownloadCheckResponse exists(bool exists);

  PDFDownloadCheckResponse localPath(String? localPath);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PDFDownloadCheckResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PDFDownloadCheckResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PDFDownloadCheckResponse call({
    String status,
    bool exists,
    String? localPath,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPDFDownloadCheckResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPDFDownloadCheckResponse.copyWith.fieldName(...)`
class _$PDFDownloadCheckResponseCWProxyImpl
    implements _$PDFDownloadCheckResponseCWProxy {
  const _$PDFDownloadCheckResponseCWProxyImpl(this._value);

  final PDFDownloadCheckResponse _value;

  @override
  PDFDownloadCheckResponse status(String status) => this(status: status);

  @override
  PDFDownloadCheckResponse exists(bool exists) => this(exists: exists);

  @override
  PDFDownloadCheckResponse localPath(String? localPath) =>
      this(localPath: localPath);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PDFDownloadCheckResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PDFDownloadCheckResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PDFDownloadCheckResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? exists = const $CopyWithPlaceholder(),
    Object? localPath = const $CopyWithPlaceholder(),
  }) {
    return PDFDownloadCheckResponse(
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
    );
  }
}

extension $PDFDownloadCheckResponseCopyWith on PDFDownloadCheckResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPDFDownloadCheckResponse.copyWith(...)` or like so:`instanceOfPDFDownloadCheckResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PDFDownloadCheckResponseCWProxy get copyWith =>
      _$PDFDownloadCheckResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PDFDownloadCheckResponse _$PDFDownloadCheckResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('PDFDownloadCheckResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['status', 'exists']);
  final val = PDFDownloadCheckResponse(
    status: $checkedConvert('status', (v) => v as String),
    exists: $checkedConvert('exists', (v) => v as bool),
    localPath: $checkedConvert('local_path', (v) => v as String?),
  );
  return val;
}, fieldKeyMap: const {'localPath': 'local_path'});

Map<String, dynamic> _$PDFDownloadCheckResponseToJson(
  PDFDownloadCheckResponse instance,
) => <String, dynamic>{
  'status': instance.status,
  'exists': instance.exists,
  'local_path': ?instance.localPath,
};
