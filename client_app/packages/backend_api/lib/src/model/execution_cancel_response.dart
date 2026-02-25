//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'execution_cancel_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ExecutionCancelResponse {
  /// Returns a new [ExecutionCancelResponse] instance.
  ExecutionCancelResponse({

    required  this.id,

    required  this.status,

    required  this.message,
  });

  @JsonKey(
    
    name: r'id',
    required: true,
    
  )


  final String id;



  @JsonKey(
    
    name: r'status',
    required: true,
    
  )


  final String status;



  @JsonKey(
    
    name: r'message',
    required: true,
    
  )


  final String message;





    @override
    bool operator ==(Object other) => identical(this, other) || other is ExecutionCancelResponse &&
      other.id == id &&
      other.status == status &&
      other.message == message;

    @override
    int get hashCode =>
        id.hashCode +
        status.hashCode +
        message.hashCode;

  factory ExecutionCancelResponse.fromJson(Map<String, dynamic> json) => _$ExecutionCancelResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ExecutionCancelResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

