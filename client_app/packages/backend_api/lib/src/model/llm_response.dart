//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'llm_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class LLMResponse {
  /// Returns a new [LLMResponse] instance.
  LLMResponse({

    required  this.result,

     this.usage,
  });

  @JsonKey(
    
    name: r'result',
    required: true,
    includeIfNull: true,
  )


  final Object? result;



      /// Usage statistics if available.
  @JsonKey(
    
    name: r'usage',
    required: false,
    
  )


  final dynamic? usage;





    @override
    bool operator ==(Object other) => identical(this, other) || other is LLMResponse &&
      other.result == result &&
      other.usage == usage;

    @override
    int get hashCode =>
        (result == null ? 0 : result.hashCode) +
        (usage == null ? 0 : usage.hashCode);

  factory LLMResponse.fromJson(Map<String, dynamic> json) => _$LLMResponseFromJson(json);

  Map<String, dynamic> toJson() => _$LLMResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

