import 'package:freezed_annotation/freezed_annotation.dart';

part 'guided_reflection.freezed.dart';
part 'guided_reflection.g.dart';

/// Data Transfer Object for Guided Reflection form inputs.
/// Maps to `GuidedReflectionDTO` in the backend.
@freezed
sealed class GuidedReflectionDTO with _$GuidedReflectionDTO {
  const factory GuidedReflectionDTO({
    /// Tavoite ja strateginen suunnittelu
    @JsonKey(name: 'q1_goal') String? q1Goal,

    /// Tekoälyn ohjaus ja kriittinen iterointi
    @JsonKey(name: 'q2_falsification') String? q2Falsification,

    /// Oma panos ja luovuus
    @JsonKey(name: 'q3_synthesis') String? q3Synthesis,

    /// Laadunvarmistus ja metakognitio
    @JsonKey(name: 'q4_argumentation') String? q4Argumentation,
  }) = _GuidedReflectionDTO;

  factory GuidedReflectionDTO.fromJson(Map<String, dynamic> json) =>
      _$GuidedReflectionDTOFromJson(json);
}
