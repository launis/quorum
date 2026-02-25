//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'self_test_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class SelfTestResponse {
  /// Returns a new [SelfTestResponse] instance.
  SelfTestResponse({

    required  this.llmStatus,

    required  this.dbStatus,

    required  this.details,
  });

  @JsonKey(
    
    name: r'llm_status',
    required: true,
    
  )


  final String llmStatus;



  @JsonKey(
    
    name: r'db_status',
    required: true,
    
  )


  final String dbStatus;



  @JsonKey(
    
    name: r'details',
    required: true,
    
  )


  final Map<String, Object> details;





    @override
    bool operator ==(Object other) => identical(this, other) || other is SelfTestResponse &&
      other.llmStatus == llmStatus &&
      other.dbStatus == dbStatus &&
      other.details == details;

    @override
    int get hashCode =>
        llmStatus.hashCode +
        dbStatus.hashCode +
        details.hashCode;

  factory SelfTestResponse.fromJson(Map<String, dynamic> json) => _$SelfTestResponseFromJson(json);

  Map<String, dynamic> toJson() => _$SelfTestResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

