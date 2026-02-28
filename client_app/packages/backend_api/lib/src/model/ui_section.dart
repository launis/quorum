//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/section_type.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'ui_section.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class UiSection {
  /// Returns a new [UiSection] instance.
  UiSection({
    required this.id,

    required this.type,

    required this.title,

    this.data,
  });

  /// Unique identifier for the section (e.g. 'verdict-card')
  @JsonKey(name: r'id', required: true)
  final String id;

  /// Determines which UI component to render
  @JsonKey(name: r'type', required: true)
  final SectionType type;

  /// User-facing title of the section
  @JsonKey(name: r'title', required: true)
  final String title;

  @JsonKey(name: r'data', required: false)
  final Object? data;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is UiSection &&
          other.id == id &&
          other.type == type &&
          other.title == title &&
          other.data == data;

  @override
  int get hashCode =>
      id.hashCode +
      type.hashCode +
      title.hashCode +
      (data == null ? 0 : data.hashCode);

  factory UiSection.fromJson(Map<String, dynamic> json) =>
      _$UiSectionFromJson(json);

  Map<String, dynamic> toJson() => _$UiSectionToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
