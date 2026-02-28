//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'knowledge_status_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class KnowledgeStatusResponse {
  /// Returns a new [KnowledgeStatusResponse] instance.
  KnowledgeStatusResponse({
    required this.hasDocuments,

    required this.documentCount,

    required this.precedentCount,
  });

  /// True if the knowledge base contains any documents.
  @JsonKey(name: r'has_documents', required: true)
  final bool hasDocuments;

  /// Total number of documents in the knowledge base.
  @JsonKey(name: r'document_count', required: true)
  final int documentCount;

  /// Total number of historical precedents (completed executions).
  @JsonKey(name: r'precedent_count', required: true)
  final int precedentCount;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is KnowledgeStatusResponse &&
          other.hasDocuments == hasDocuments &&
          other.documentCount == documentCount &&
          other.precedentCount == precedentCount;

  @override
  int get hashCode =>
      hasDocuments.hashCode + documentCount.hashCode + precedentCount.hashCode;

  factory KnowledgeStatusResponse.fromJson(Map<String, dynamic> json) =>
      _$KnowledgeStatusResponseFromJson(json);

  Map<String, dynamic> toJson() => _$KnowledgeStatusResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
