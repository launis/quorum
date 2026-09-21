// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'llm_platform.freezed.dart';
part 'llm_platform.g.dart';

/// Data Transfer Object representing a supported LLM platform provider.
///
/// Matches backend SSOT `LLMPlatformDTO` in `backend_v2/models/dtos/studio.py`.
@Freezed(equal: false)
abstract class LlmPlatform with _$LlmPlatform {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory LlmPlatform({
    required String id,
    required String label,
    @JsonKey(name: 'has_regions') required bool hasRegions,
  }) = _LlmPlatform;

  factory LlmPlatform.fromJson(Map<String, dynamic> json) =>
      _$LlmPlatformFromJson(json);
}
