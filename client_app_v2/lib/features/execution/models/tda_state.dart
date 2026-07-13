// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'tda_state.freezed.dart';
part 'tda_state.g.dart';

@freezed
sealed class TDAState with _$TDAState {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory TDAState.pending() = Pending;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory TDAState.evaluated({
    required bool passed,
    required String displayQuote,
    required String rawAnchor,
  }) = Evaluated;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory TDAState.dlq({
    required String userReason,
    required String backendTrace,
  }) = Dlq;

  factory TDAState.fromJson(Map<String, dynamic> json) =>
      _$TDAStateFromJson(json);
}
