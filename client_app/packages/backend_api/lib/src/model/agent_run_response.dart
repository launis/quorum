//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'agent_run_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class AgentRunResponse {
  /// Returns a new [AgentRunResponse] instance.
  AgentRunResponse({

    required  this.agent,

    required  this.result,
  });

  @JsonKey(
    
    name: r'agent',
    required: true,
    
  )


  final String agent;



  @JsonKey(
    
    name: r'result',
    required: true,
    includeIfNull: true,
  )


  final Object? result;





    @override
    bool operator ==(Object other) => identical(this, other) || other is AgentRunResponse &&
      other.agent == agent &&
      other.result == result;

    @override
    int get hashCode =>
        agent.hashCode +
        (result == null ? 0 : result.hashCode);

  factory AgentRunResponse.fromJson(Map<String, dynamic> json) => _$AgentRunResponseFromJson(json);

  Map<String, dynamic> toJson() => _$AgentRunResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

