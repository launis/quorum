//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'playground_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PlaygroundResponse {
  /// Returns a new [PlaygroundResponse] instance.
  PlaygroundResponse({

    required  this.content,

     this.usage,
  });

      /// The LLM response content.
  @JsonKey(
    
    name: r'content',
    required: true,
    
  )


  final String content;



  @JsonKey(
    
    name: r'usage',
    required: false,
    
  )


  final Map<String, Object>? usage;





    @override
    bool operator ==(Object other) => identical(this, other) || other is PlaygroundResponse &&
      other.content == content &&
      other.usage == usage;

    @override
    int get hashCode =>
        content.hashCode +
        (usage == null ? 0 : usage.hashCode);

  factory PlaygroundResponse.fromJson(Map<String, dynamic> json) => _$PlaygroundResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PlaygroundResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

