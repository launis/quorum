//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'step_preview_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class StepPreviewResponse {
  /// Returns a new [StepPreviewResponse] instance.
  StepPreviewResponse({

    required  this.systemInstruction,

    required  this.userPrompt,

    required  this.agentClass,
  });

      /// The full system prompt.
  @JsonKey(
    
    name: r'system_instruction',
    required: true,
    
  )


  final String systemInstruction;



      /// The user prompt template logic.
  @JsonKey(
    
    name: r'user_prompt',
    required: true,
    
  )


  final String userPrompt;



      /// The agent component class.
  @JsonKey(
    
    name: r'agent_class',
    required: true,
    
  )


  final String agentClass;





    @override
    bool operator ==(Object other) => identical(this, other) || other is StepPreviewResponse &&
      other.systemInstruction == systemInstruction &&
      other.userPrompt == userPrompt &&
      other.agentClass == agentClass;

    @override
    int get hashCode =>
        systemInstruction.hashCode +
        userPrompt.hashCode +
        agentClass.hashCode;

  factory StepPreviewResponse.fromJson(Map<String, dynamic> json) => _$StepPreviewResponseFromJson(json);

  Map<String, dynamic> toJson() => _$StepPreviewResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

