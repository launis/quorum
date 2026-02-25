//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/completion_request.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'batch_completion_request.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class BatchCompletionRequest {
  /// Returns a new [BatchCompletionRequest] instance.
  BatchCompletionRequest({

    required  this.requests,
  });

      /// List of requests to process in parallel.
  @JsonKey(
    
    name: r'requests',
    required: true,
    
  )


  final List<CompletionRequest> requests;





    @override
    bool operator ==(Object other) => identical(this, other) || other is BatchCompletionRequest &&
      other.requests == requests;

    @override
    int get hashCode =>
        requests.hashCode;

  factory BatchCompletionRequest.fromJson(Map<String, dynamic> json) => _$BatchCompletionRequestFromJson(json);

  Map<String, dynamic> toJson() => _$BatchCompletionRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

