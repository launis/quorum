import 'package:freezed_annotation/freezed_annotation.dart';

part 'tda_state.freezed.dart';
part 'tda_state.g.dart';

/// Discriminated union representing the evaluation state of a TDA assertion.
@Freezed(equal: false)
sealed class TDAState with _$TDAState {
  const TDAState._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory TDAState.pending() = Pending;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory TDAState.evaluated({
    required bool passed,
    @JsonKey(name: 'display_quote') required String displayQuote,
    @JsonKey(name: 'raw_anchor') required String rawAnchor,
  }) = Evaluated;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory TDAState.dlq({
    @JsonKey(name: 'user_reason') required String userReason,
    @JsonKey(name: 'backend_trace') required String backendTrace,
  }) = Dlq;

  /// Instantiates a strictly typed [TDAState] from raw JSON.
  factory TDAState.fromJson(Map<String, dynamic> json) =>
      _$TDAStateFromJson(json);
}
