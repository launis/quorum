// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'generic_status_response_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_GenericStatusResponseDto _$GenericStatusResponseDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_GenericStatusResponseDto', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['status', 'message']);
  final val = _GenericStatusResponseDto(
    status: $checkedConvert('status', (v) => v as String? ?? 'ok'),
    message: $checkedConvert('message', (v) => v as String),
  );
  return val;
});

Map<String, dynamic> _$GenericStatusResponseDtoToJson(
  _GenericStatusResponseDto instance,
) => <String, dynamic>{'status': instance.status, 'message': instance.message};
