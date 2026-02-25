//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'completion_request.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class CompletionRequest {
  /// Returns a new [CompletionRequest] instance.
  CompletionRequest({

    required  this.prompt,

     this.systemInstruction,

     this.modelStrategy = 'fast',

     this.responseSchema,
  });

      /// The primary prompt text.
  @JsonKey(
    
    name: r'prompt',
    required: true,
    
  )


  final String prompt;



  @JsonKey(
    
    name: r'system_instruction',
    required: false,
    
  )


  final String? systemInstruction;



      /// Strategy key (fast, deep, etc) or direct model name.
  @JsonKey(
    defaultValue: 'fast',
    name: r'model_strategy',
    required: false,
    
  )


  final String? modelStrategy;



  @JsonKey(
    
    name: r'response_schema',
    required: false,
    
  )


  final Map<String, Object>? responseSchema;





    @override
    bool operator ==(Object other) => identical(this, other) || other is CompletionRequest &&
      other.prompt == prompt &&
      other.systemInstruction == systemInstruction &&
      other.modelStrategy == modelStrategy &&
      other.responseSchema == responseSchema;

    @override
    int get hashCode =>
        prompt.hashCode +
        (systemInstruction == null ? 0 : systemInstruction.hashCode) +
        modelStrategy.hashCode +
        (responseSchema == null ? 0 : responseSchema.hashCode);

  factory CompletionRequest.fromJson(Map<String, dynamic> json) => _$CompletionRequestFromJson(json);

  Map<String, dynamic> toJson() => _$CompletionRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

