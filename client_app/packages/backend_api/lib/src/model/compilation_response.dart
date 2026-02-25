//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'compilation_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class CompilationResponse {
  /// Returns a new [CompilationResponse] instance.
  CompilationResponse({

    required  this.status,

    required  this.compositeStepId,

    required  this.newSteps,
  });

      /// Compilation status (e.g. 'compiled').
  @JsonKey(
    
    name: r'status',
    required: true,
    
  )


  final String status;



      /// The ID of the resulting composite step.
  @JsonKey(
    
    name: r'composite_step_id',
    required: true,
    
  )


  final String compositeStepId;



      /// The updated list of step IDs in the workflow.
  @JsonKey(
    
    name: r'new_steps',
    required: true,
    
  )


  final List<String> newSteps;





    @override
    bool operator ==(Object other) => identical(this, other) || other is CompilationResponse &&
      other.status == status &&
      other.compositeStepId == compositeStepId &&
      other.newSteps == newSteps;

    @override
    int get hashCode =>
        status.hashCode +
        compositeStepId.hashCode +
        newSteps.hashCode;

  factory CompilationResponse.fromJson(Map<String, dynamic> json) => _$CompilationResponseFromJson(json);

  Map<String, dynamic> toJson() => _$CompilationResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

