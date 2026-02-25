//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'batch_llm_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class BatchLLMResponse {
  /// Returns a new [BatchLLMResponse] instance.
  BatchLLMResponse({

    required  this.results,
  });

      /// List of results (success or error) for each request.
  @JsonKey(
    
    name: r'results',
    required: true,
    
  )


  final List<Map<String, Object>> results;





    @override
    bool operator ==(Object other) => identical(this, other) || other is BatchLLMResponse &&
      other.results == results;

    @override
    int get hashCode =>
        results.hashCode;

  factory BatchLLMResponse.fromJson(Map<String, dynamic> json) => _$BatchLLMResponseFromJson(json);

  Map<String, dynamic> toJson() => _$BatchLLMResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

