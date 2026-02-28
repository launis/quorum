//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'citation_lookup_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class CitationLookupResponse {
  /// Returns a new [CitationLookupResponse] instance.
  CitationLookupResponse({required this.results});

  /// Map of query to resolved context items.
  @JsonKey(name: r'results', required: true)
  final Map<String, List<Map<String, Object>>> results;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CitationLookupResponse && other.results == results;

  @override
  int get hashCode => results.hashCode;

  factory CitationLookupResponse.fromJson(Map<String, dynamic> json) =>
      _$CitationLookupResponseFromJson(json);

  Map<String, dynamic> toJson() => _$CitationLookupResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
