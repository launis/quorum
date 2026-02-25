//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'body_clone_step_builder_steps_clone_post.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class BodyCloneStepBuilderStepsClonePost {
  /// Returns a new [BodyCloneStepBuilderStepsClonePost] instance.
  BodyCloneStepBuilderStepsClonePost({

    required  this.sourceStepId,
  });

  @JsonKey(
    
    name: r'source_step_id',
    required: true,
    
  )


  final String sourceStepId;





    @override
    bool operator ==(Object other) => identical(this, other) || other is BodyCloneStepBuilderStepsClonePost &&
      other.sourceStepId == sourceStepId;

    @override
    int get hashCode =>
        sourceStepId.hashCode;

  factory BodyCloneStepBuilderStepsClonePost.fromJson(Map<String, dynamic> json) => _$BodyCloneStepBuilderStepsClonePostFromJson(json);

  Map<String, dynamic> toJson() => _$BodyCloneStepBuilderStepsClonePostToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

