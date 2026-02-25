//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'async_job_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class AsyncJobResponse {
  /// Returns a new [AsyncJobResponse] instance.
  AsyncJobResponse({

    required  this.jobId,

    required  this.status,

     this.message,
  });

      /// Unique Identifier for the background job.
  @JsonKey(
    
    name: r'job_id',
    required: true,
    
  )


  final String jobId;



      /// Initial status (e.g. 'queued', 'starting').
  @JsonKey(
    
    name: r'status',
    required: true,
    
  )


  final String status;



  @JsonKey(
    
    name: r'message',
    required: false,
    
  )


  final String? message;





    @override
    bool operator ==(Object other) => identical(this, other) || other is AsyncJobResponse &&
      other.jobId == jobId &&
      other.status == status &&
      other.message == message;

    @override
    int get hashCode =>
        jobId.hashCode +
        status.hashCode +
        (message == null ? 0 : message.hashCode);

  factory AsyncJobResponse.fromJson(Map<String, dynamic> json) => _$AsyncJobResponseFromJson(json);

  Map<String, dynamic> toJson() => _$AsyncJobResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

