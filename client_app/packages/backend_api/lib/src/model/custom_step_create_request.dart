//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'custom_step_create_request.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class CustomStepCreateRequest {
  /// Returns a new [CustomStepCreateRequest] instance.
  CustomStepCreateRequest({

    required  this.componentType,

     this.nameHint,
  });

      /// Base component type (e.g. 'Judge', 'Analyst').
  @JsonKey(
    
    name: r'component_type',
    required: true,
    
  )


  final String componentType;



  @JsonKey(
    
    name: r'name_hint',
    required: false,
    
  )


  final String? nameHint;





    @override
    bool operator ==(Object other) => identical(this, other) || other is CustomStepCreateRequest &&
      other.componentType == componentType &&
      other.nameHint == nameHint;

    @override
    int get hashCode =>
        componentType.hashCode +
        (nameHint == null ? 0 : nameHint.hashCode);

  factory CustomStepCreateRequest.fromJson(Map<String, dynamic> json) => _$CustomStepCreateRequestFromJson(json);

  Map<String, dynamic> toJson() => _$CustomStepCreateRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

