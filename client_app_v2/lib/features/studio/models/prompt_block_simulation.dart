import 'package:freezed_annotation/freezed_annotation.dart';
import 'prompt_block.dart';
import 'step_simulation.dart';

part 'prompt_block_simulation.freezed.dart';
part 'prompt_block_simulation.g.dart';

/// Simulation configuration inputs for testing dynamic prompt construction.
///
/// Matches backend SSOT `PromptBlockSimulationRequest` in `backend_v2/models/dtos/studio.py`.
@Freezed(equal: false)
abstract class PromptBlockSimulationRequest
    with _$PromptBlockSimulationRequest {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory PromptBlockSimulationRequest({
    required PromptBlock block,
    @JsonKey(name: 'mock_inputs') @Default({}) Map<String, dynamic> mockInputs,
    @JsonKey(name: 'target_scale_score') int? targetScaleScore,
    @JsonKey(name: 'target_locale') @Default('en') String targetLocale,
    @JsonKey(name: 'context_text')
    @Default('[SIMULATED CONTEXT DOCUMENT]')
    String contextText,
  }) = _PromptBlockSimulationRequest;

  factory PromptBlockSimulationRequest.fromJson(Map<String, dynamic> json) =>
      _$PromptBlockSimulationRequestFromJson(json);
}

/// Resulting simulation projection for a dry-run prompt rendering.
///
/// Matches backend SSOT `PromptBlockSimulationResponse` in `backend_v2/models/dtos/studio.py`.
@Freezed(equal: false)
abstract class PromptBlockSimulationResponse
    with _$PromptBlockSimulationResponse {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory PromptBlockSimulationResponse({
    @Default(true) bool valid,
    @Default([]) List<String> errors,
    @JsonKey(name: 'rendered_prompt') @Default('') String renderedPrompt,
    @Default({}) Map<String, dynamic> trace,
    @JsonKey(name: 'prompt_context') PromptContextDto? promptContext,
  }) = _PromptBlockSimulationResponse;

  factory PromptBlockSimulationResponse.fromJson(Map<String, dynamic> json) =>
      _$PromptBlockSimulationResponseFromJson(json);
}
