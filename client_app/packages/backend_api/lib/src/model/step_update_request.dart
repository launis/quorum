//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'step_update_request.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class StepUpdateRequest {
  /// Returns a new [StepUpdateRequest] instance.
  StepUpdateRequest({

     this.name,

     this.config,
  });

  @JsonKey(
    
    name: r'name',
    required: false,
    
  )


  final String? name;



  @JsonKey(
    
    name: r'config',
    required: false,
    
  )


  final Map<String, Object>? config;





    @override
    bool operator ==(Object other) => identical(this, other) || other is StepUpdateRequest &&
      other.name == name &&
      other.config == config;

    @override
    int get hashCode =>
        (name == null ? 0 : name.hashCode) +
        (config == null ? 0 : config.hashCode);

  factory StepUpdateRequest.fromJson(Map<String, dynamic> json) => _$StepUpdateRequestFromJson(json);

  Map<String, dynamic> toJson() => _$StepUpdateRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

