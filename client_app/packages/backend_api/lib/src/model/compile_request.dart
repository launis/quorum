//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'compile_request.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class CompileRequest {
  /// Returns a new [CompileRequest] instance.
  CompileRequest({

    required  this.workflowId,

    required  this.steps,
  });

      /// Target workflow ID.
  @JsonKey(
    
    name: r'workflow_id',
    required: true,
    
  )


  final String workflowId;



      /// List of step IDs to fuse.
  @JsonKey(
    
    name: r'steps',
    required: true,
    
  )


  final List<String> steps;





    @override
    bool operator ==(Object other) => identical(this, other) || other is CompileRequest &&
      other.workflowId == workflowId &&
      other.steps == steps;

    @override
    int get hashCode =>
        workflowId.hashCode +
        steps.hashCode;

  factory CompileRequest.fromJson(Map<String, dynamic> json) => _$CompileRequestFromJson(json);

  Map<String, dynamic> toJson() => _$CompileRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

