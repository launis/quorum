import 'package:client_app/features/studio/models/workflow.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'step_simulation.freezed.dart';
part 'step_simulation.g.dart';

/// Converts heterogeneous JSON scalar or string-list metadata values into [PromptContextMetaValue].
class PromptContextMetaValueConverter
    implements JsonConverter<PromptContextMetaValue, Object?> {
  const PromptContextMetaValueConverter();

  @override
  PromptContextMetaValue fromJson(Object? json) {
    if (json == null) {
      return const PromptContextMetaValue();
    }
    if (json is List) {
      final items = <String>[];
      for (final Object? element in json) {
        if (element is! String) {
          throw CheckedFromJsonException(
            <String, Object?>{'value': json},
            'value',
            'PromptContextMetaValue',
            'Expected List<String> metadata value, got element of type ${element.runtimeType}.',
          );
        }
        items.add(element);
      }
      return PromptContextMetaValue(
        stringListValue: List<String>.unmodifiable(items),
      );
    }
    if (json is num) {
      return PromptContextMetaValue(numberValue: json.toDouble());
    }
    if (json is bool) {
      return PromptContextMetaValue(boolValue: json);
    }
    if (json is String) {
      return PromptContextMetaValue(stringValue: json);
    }
    throw CheckedFromJsonException(
      <String, Object?>{'value': json},
      'value',
      'PromptContextMetaValue',
      'Unsupported metadata value type: ${json.runtimeType}.',
    );
  }

  @override
  Object? toJson(PromptContextMetaValue object) {
    if (object.stringListValue != null) {
      return object.stringListValue;
    }
    if (object.numberValue != null) {
      return object.numberValue;
    }
    if (object.boolValue != null) {
      return object.boolValue;
    }
    return object.stringValue;
  }
}

/// Strongly typed metadata value for [PromptContextDto.metadata].
@Freezed(equal: false)
abstract class PromptContextMetaValue with _$PromptContextMetaValue {
  const PromptContextMetaValue._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory PromptContextMetaValue({
    @JsonKey(name: 'string_value') String? stringValue,
    @JsonKey(name: 'number_value') double? numberValue,
    @JsonKey(name: 'bool_value') bool? boolValue,
    @JsonKey(name: 'string_list_value') List<String>? stringListValue,
  }) = _PromptContextMetaValue;

  factory PromptContextMetaValue.fromJson(Map<String, dynamic> json) =>
      _$PromptContextMetaValueFromJson(json);

  Object? get rawValue =>
      stringListValue ?? numberValue ?? boolValue ?? stringValue;
}

@Freezed(equal: false)
abstract class StepSimulationTraceDto with _$StepSimulationTraceDto {
  const StepSimulationTraceDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
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

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory LlmMessageDto({
    required String role,
    required String content,
    @JsonKey(name: 'tool_calls') Object? toolCalls,
    @JsonKey(name: 'tool_call_id') String? toolCallId,
    String? name,
  }) = _LlmMessageDto;

  factory LlmMessageDto.fromJson(Map<String, dynamic> json) =>
      _$LlmMessageDtoFromJson(json);
}

@Freezed(equal: false)
abstract class PromptContextDto with _$PromptContextDto {
  const PromptContextDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory PromptContextDto({
    @Default(<LlmMessageDto>[])
    @JsonKey(name: 'static_messages')
    List<LlmMessageDto> staticMessages,
    @Default(<LlmMessageDto>[])
    @JsonKey(name: 'dynamic_messages')
    List<LlmMessageDto> dynamicMessages,
    @PromptContextMetaValueConverter()
    @Default(<String, PromptContextMetaValue>{})
    Map<String, PromptContextMetaValue> metadata,
  }) = _PromptContextDto;

  factory PromptContextDto.fromJson(Map<String, dynamic> json) =>
      _$PromptContextDtoFromJson(json);
}

@Freezed(equal: false)
abstract class StepSimulationRequest with _$StepSimulationRequest {
  const StepSimulationRequest._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory StepSimulationRequest({
    required NodeStrategy step,
    @Default(<String, String>{})
    @JsonKey(name: 'mock_inputs')
    Map<String, String> mockInputs,
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

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory StepSimulationResponse({
    @Default(true) bool valid,
    @Default(<String>[]) List<String> errors,
    @Default('') @JsonKey(name: 'rendered_prompt') String renderedPrompt,
    @Default(StepSimulationTraceDto()) StepSimulationTraceDto trace,
    @JsonKey(name: 'prompt_context') PromptContextDto? promptContext,
  }) = _StepSimulationResponse;

  factory StepSimulationResponse.fromJson(Map<String, dynamic> json) =>
      _$StepSimulationResponseFromJson(json);
}
