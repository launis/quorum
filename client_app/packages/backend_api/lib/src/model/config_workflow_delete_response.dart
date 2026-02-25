//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'config_workflow_delete_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ConfigWorkflowDeleteResponse {
  /// Returns a new [ConfigWorkflowDeleteResponse] instance.
  ConfigWorkflowDeleteResponse({

    required  this.status,

    required  this.id,
  });

  @JsonKey(
    
    name: r'status',
    required: true,
    
  )


  final String status;



  @JsonKey(
    
    name: r'id',
    required: true,
    
  )


  final String id;





    @override
    bool operator ==(Object other) => identical(this, other) || other is ConfigWorkflowDeleteResponse &&
      other.status == status &&
      other.id == id;

    @override
    int get hashCode =>
        status.hashCode +
        id.hashCode;

  factory ConfigWorkflowDeleteResponse.fromJson(Map<String, dynamic> json) => _$ConfigWorkflowDeleteResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ConfigWorkflowDeleteResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

