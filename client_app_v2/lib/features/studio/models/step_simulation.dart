// ignore_for_file: invalid_annotation_target
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'step_simulation.freezed.dart';
part 'step_simulation.g.dart';

@Freezed(equal: false)
abstract class StepSimulationTraceDto with _$StepSimulationTraceDto {
  const StepSimulationTraceDto._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory StepSimulationTraceDto({
    @Default(0.0) @JsonKey(name: 'execution_time_ms') double executionTimeMs,
    @Default(0) @JsonKey(name: 'estimated_tokens') int estimatedTokens,
  }) = _StepSimulationTraceDto;

  factory StepSimulationTraceDto.fromJson(Map<String, dynamic> json) =>
      _$StepSimulationTraceDtoFromJson(json);
}

@Freezed(equal: false)
abstract class LlmMessageDto with _$LlmMessageDto {
  const LlmMessageDto._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory LlmMessageDto({
    required String role,
    required String content,
    @JsonKey(name: 'tool_calls') dynamic toolCalls,
    @JsonKey(name: 'tool_call_id') String? toolCallId,
    String? name,
  }) = _LlmMessageDto;

  factory LlmMessageDto.fromJson(Map<String, dynamic> json) =>
      _$LlmMessageDtoFromJson(json);
}

@Freezed(equal: false)
abstract class PromptContextDto with _$PromptContextDto {
  const PromptContextDto._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory PromptContextDto({
    @Default([])
    @JsonKey(name: 'static_messages')
    List<LlmMessageDto> staticMessages,
    @Default([])
    @JsonKey(name: 'dynamic_messages')
    List<LlmMessageDto> dynamicMessages,
    @Default({}) Map<String, dynamic> metadata,
  }) = _PromptContextDto;

  factory PromptContextDto.fromJson(Map<String, dynamic> json) =>
      _$PromptContextDtoFromJson(json);
}

@Freezed(equal: false)
abstract class StepSimulationRequest with _$StepSimulationRequest {
  const StepSimulationRequest._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory StepSimulationRequest({
    required NodeStrategy step,
    @Default({}) @JsonKey(name: 'mock_inputs') Map<String, dynamic> mockInputs,
    @Default('en') @JsonKey(name: 'target_locale') String targetLocale,
    @Default('[SIMULATED CONTEXT DOCUMENT]')
    @JsonKey(name: 'context_text')
    String contextText,
  }) = _StepSimulationRequest;

  factory StepSimulationRequest.fromJson(Map<String, dynamic> json) =>
      _$StepSimulationRequestFromJson(json);
}

@Freezed(equal: false)
abstract class StepSimulationResponse with _$StepSimulationResponse {
  const StepSimulationResponse._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory StepSimulationResponse({
    @Default(true) bool valid,
    @Default([]) List<String> errors,
    @Default('') @JsonKey(name: 'rendered_prompt') String renderedPrompt,
    @Default(StepSimulationTraceDto()) StepSimulationTraceDto trace,
    @JsonKey(name: 'prompt_context') PromptContextDto? promptContext,
  }) = _StepSimulationResponse;

  factory StepSimulationResponse.fromJson(Map<String, dynamic> json) =>
      _$StepSimulationResponseFromJson(json);
}
