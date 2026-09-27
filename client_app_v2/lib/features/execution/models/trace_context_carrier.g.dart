// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'trace_context_carrier.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_TraceContextCarrier _$TraceContextCarrierFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_TraceContextCarrier', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['traceparent', 'tracestate']);
      final val = _TraceContextCarrier(
        traceparent: $checkedConvert('traceparent', (v) => v as String),
        tracestate: $checkedConvert('tracestate', (v) => v as String?),
      );
      return val;
    });

Map<String, dynamic> _$TraceContextCarrierToJson(
  _TraceContextCarrier instance,
) => <String, dynamic>{
  'traceparent': instance.traceparent,
  'tracestate': instance.tracestate,
};
