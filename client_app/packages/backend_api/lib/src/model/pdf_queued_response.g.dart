// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pdf_queued_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PDFQueuedResponseCWProxy {
  PDFQueuedResponse status(String status);

  PDFQueuedResponse message(String message);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PDFQueuedResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PDFQueuedResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PDFQueuedResponse call({String status, String message});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPDFQueuedResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPDFQueuedResponse.copyWith.fieldName(...)`
class _$PDFQueuedResponseCWProxyImpl implements _$PDFQueuedResponseCWProxy {
  const _$PDFQueuedResponseCWProxyImpl(this._value);

  final PDFQueuedResponse _value;

  @override
  PDFQueuedResponse status(String status) => this(status: status);

  @override
  PDFQueuedResponse message(String message) => this(message: message);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PDFQueuedResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PDFQueuedResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PDFQueuedResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? message = const $CopyWithPlaceholder(),
  }) {
    return PDFQueuedResponse(
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

extension $PDFQueuedResponseCopyWith on PDFQueuedResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPDFQueuedResponse.copyWith(...)` or like so:`instanceOfPDFQueuedResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PDFQueuedResponseCWProxy get copyWith =>
      _$PDFQueuedResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PDFQueuedResponse _$PDFQueuedResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('PDFQueuedResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['status', 'message']);
      final val = PDFQueuedResponse(
        status: $checkedConvert('status', (v) => v as String),
        message: $checkedConvert('message', (v) => v as String),
      );
      return val;
    });

Map<String, dynamic> _$PDFQueuedResponseToJson(PDFQueuedResponse instance) =>
    <String, dynamic>{'status': instance.status, 'message': instance.message};
