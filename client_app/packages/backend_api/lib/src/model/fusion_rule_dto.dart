//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'fusion_rule_dto.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class FusionRuleDTO {
  /// Returns a new [FusionRuleDTO] instance.
  FusionRuleDTO({

    required  this.compositeStepId,

    required  this.name,

    required  this.replacesComponents,

    required  this.minSteps,
  });

  @JsonKey(
    
    name: r'composite_step_id',
    required: true,
    
  )


  final String compositeStepId;



  @JsonKey(
    
    name: r'name',
    required: true,
    
  )


  final String name;



  @JsonKey(
    
    name: r'replaces_components',
    required: true,
    
  )


  final List<String> replacesComponents;



  @JsonKey(
    
    name: r'min_steps',
    required: true,
    
  )


  final int minSteps;





    @override
    bool operator ==(Object other) => identical(this, other) || other is FusionRuleDTO &&
      other.compositeStepId == compositeStepId &&
      other.name == name &&
      other.replacesComponents == replacesComponents &&
      other.minSteps == minSteps;

    @override
    int get hashCode =>
        compositeStepId.hashCode +
        name.hashCode +
        replacesComponents.hashCode +
        minSteps.hashCode;

  factory FusionRuleDTO.fromJson(Map<String, dynamic> json) => _$FusionRuleDTOFromJson(json);

  Map<String, dynamic> toJson() => _$FusionRuleDTOToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

