//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'ad_hoc_test_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class AdHocTestResponse {
  /// Returns a new [AdHocTestResponse] instance.
  AdHocTestResponse({

    required  this.content,

    required  this.latencyMs,

    required  this.status,
  });

      /// Generated content.
  @JsonKey(
    
    name: r'content',
    required: true,
    
  )


  final String content;



      /// Execution latency in milliseconds.
  @JsonKey(
    
    name: r'latency_ms',
    required: true,
    
  )


  final num latencyMs;



      /// Status string (e.g. 'success', 'error').
  @JsonKey(
    
    name: r'status',
    required: true,
    
  )


  final String status;





    @override
    bool operator ==(Object other) => identical(this, other) || other is AdHocTestResponse &&
      other.content == content &&
      other.latencyMs == latencyMs &&
      other.status == status;

    @override
    int get hashCode =>
        content.hashCode +
        latencyMs.hashCode +
        status.hashCode;

  factory AdHocTestResponse.fromJson(Map<String, dynamic> json) => _$AdHocTestResponseFromJson(json);

  Map<String, dynamic> toJson() => _$AdHocTestResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

