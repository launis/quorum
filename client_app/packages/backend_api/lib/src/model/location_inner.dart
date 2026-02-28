//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'location_inner.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class LocationInner {
  /// Returns a new [LocationInner] instance.
  LocationInner({this.dummy});
  final String? dummy;

  @override
  bool operator ==(Object other) =>
      identical(this, other) || other is LocationInner;

  @override
  int get hashCode => 0;

  factory LocationInner.fromJson(Map<String, dynamic> json) =>
      _$LocationInnerFromJson(json);

  Map<String, dynamic> toJson() => _$LocationInnerToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
