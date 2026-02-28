//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'matrix_content_dto.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class MatrixContentDTO {
  /// Returns a new [MatrixContentDTO] instance.
  MatrixContentDTO({this.scale, this.criteria, this.roleDescription});

  @JsonKey(name: r'scale', required: false)
  final Map<String, int>? scale;

  @JsonKey(name: r'criteria', required: false)
  final List<Map<String, Object>>? criteria;

  @JsonKey(name: r'role_description', required: false)
  final String? roleDescription;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is MatrixContentDTO &&
          other.scale == scale &&
          other.criteria == criteria &&
          other.roleDescription == roleDescription;

  @override
  int get hashCode =>
      scale.hashCode +
      criteria.hashCode +
      (roleDescription == null ? 0 : roleDescription.hashCode);

  factory MatrixContentDTO.fromJson(Map<String, dynamic> json) =>
      _$MatrixContentDTOFromJson(json);

  Map<String, dynamic> toJson() => _$MatrixContentDTOToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
