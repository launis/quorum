import 'package:freezed_annotation/freezed_annotation.dart';

part 'trace_context_carrier.freezed.dart';
part 'trace_context_carrier.g.dart';

/// W3C distributed trace context carrier for OpenTelemetry.
@Freezed(equal: false)
abstract class TraceContextCarrier with _$TraceContextCarrier {
  const TraceContextCarrier._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory TraceContextCarrier({
    required String traceparent,
    String? tracestate,
  }) = _TraceContextCarrier;

  /// Instantiates a strictly typed [TraceContextCarrier] from raw JSON.
  factory TraceContextCarrier.fromJson(Map<String, dynamic> json) =>
      _$TraceContextCarrierFromJson(json);
}
