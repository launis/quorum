//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'knowledge_ingest_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class KnowledgeIngestResponse {
  /// Returns a new [KnowledgeIngestResponse] instance.
  KnowledgeIngestResponse({

    required  this.jobId,
  });

  @JsonKey(
    
    name: r'job_id',
    required: true,
    
  )


  final String jobId;





    @override
    bool operator ==(Object other) => identical(this, other) || other is KnowledgeIngestResponse &&
      other.jobId == jobId;

    @override
    int get hashCode =>
        jobId.hashCode;

  factory KnowledgeIngestResponse.fromJson(Map<String, dynamic> json) => _$KnowledgeIngestResponseFromJson(json);

  Map<String, dynamic> toJson() => _$KnowledgeIngestResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

