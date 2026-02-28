//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'concept_extraction_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ConceptExtractionResponse {
  /// Returns a new [ConceptExtractionResponse] instance.
  ConceptExtractionResponse({
    required this.sourceLength,

    required this.concepts,
  });

  /// Length of the source text processed.
  @JsonKey(name: r'source_length', required: true)
  final int sourceLength;

  @JsonKey(name: r'concepts', required: true, includeIfNull: true)
  final Object? concepts;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ConceptExtractionResponse &&
          other.sourceLength == sourceLength &&
          other.concepts == concepts;

  @override
  int get hashCode =>
      sourceLength.hashCode + (concepts == null ? 0 : concepts.hashCode);

  factory ConceptExtractionResponse.fromJson(Map<String, dynamic> json) =>
      _$ConceptExtractionResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ConceptExtractionResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
