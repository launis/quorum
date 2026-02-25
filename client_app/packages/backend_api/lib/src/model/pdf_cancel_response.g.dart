// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pdf_cancel_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PDFCancelResponseCWProxy {
  PDFCancelResponse status(String status);

  PDFCancelResponse message(String message);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PDFCancelResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PDFCancelResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PDFCancelResponse call({String status, String message});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPDFCancelResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPDFCancelResponse.copyWith.fieldName(...)`
class _$PDFCancelResponseCWProxyImpl implements _$PDFCancelResponseCWProxy {
  const _$PDFCancelResponseCWProxyImpl(this._value);

  final PDFCancelResponse _value;

  @override
  PDFCancelResponse status(String status) => this(status: status);

  @override
  PDFCancelResponse message(String message) => this(message: message);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PDFCancelResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PDFCancelResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PDFCancelResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? message = const $CopyWithPlaceholder(),
  }) {
    return PDFCancelResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      message: message == const $CopyWithPlaceholder()
          ? _value.message
          // ignore: cast_nullable_to_non_nullable
          : message as String,
    );
  }
}

extension $PDFCancelResponseCopyWith on PDFCancelResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPDFCancelResponse.copyWith(...)` or like so:`instanceOfPDFCancelResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PDFCancelResponseCWProxy get copyWith =>
      _$PDFCancelResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PDFCancelResponse _$PDFCancelResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('PDFCancelResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['status', 'message']);
      final val = PDFCancelResponse(
        status: $checkedConvert('status', (v) => v as String),
        message: $checkedConvert('message', (v) => v as String),
      );
      return val;
    });

Map<String, dynamic> _$PDFCancelResponseToJson(PDFCancelResponse instance) =>
    <String, dynamic>{'status': instance.status, 'message': instance.message};
