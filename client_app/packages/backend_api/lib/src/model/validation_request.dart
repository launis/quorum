//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'validation_request.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ValidationRequest {
  /// Returns a new [ValidationRequest] instance.
  ValidationRequest({

    required  this.sourceStep,

    required  this.targetStep,
  });

      /// ID of the source step.
  @JsonKey(
    
    name: r'source_step',
    required: true,
    
  )


  final String sourceStep;



      /// ID of the target step.
  @JsonKey(
    
    name: r'target_step',
    required: true,
    
  )


  final String targetStep;





    @override
    bool operator ==(Object other) => identical(this, other) || other is ValidationRequest &&
      other.sourceStep == sourceStep &&
      other.targetStep == targetStep;

    @override
    int get hashCode =>
        sourceStep.hashCode +
        targetStep.hashCode;

  factory ValidationRequest.fromJson(Map<String, dynamic> json) => _$ValidationRequestFromJson(json);

  Map<String, dynamic> toJson() => _$ValidationRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

