//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'body_citation_lookup_tools_citation_lookup_post.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class BodyCitationLookupToolsCitationLookupPost {
  /// Returns a new [BodyCitationLookupToolsCitationLookupPost] instance.
  BodyCitationLookupToolsCitationLookupPost({required this.queries});

  @JsonKey(name: r'queries', required: true)
  final List<String> queries;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is BodyCitationLookupToolsCitationLookupPost &&
          other.queries == queries;

  @override
  int get hashCode => queries.hashCode;

  factory BodyCitationLookupToolsCitationLookupPost.fromJson(
    Map<String, dynamic> json,
  ) => _$BodyCitationLookupToolsCitationLookupPostFromJson(json);

  Map<String, dynamic> toJson() =>
      _$BodyCitationLookupToolsCitationLookupPostToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
