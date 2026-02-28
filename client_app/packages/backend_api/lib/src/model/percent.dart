//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'percent.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class Percent {
  /// Returns a new [Percent] instance.
  Percent({this.dummy});
  final String? dummy;

  @override
  bool operator ==(Object other) => identical(this, other) || other is Percent;

  @override
  int get hashCode => 0;

  factory Percent.fromJson(Map<String, dynamic> json) =>
      _$PercentFromJson(json);

  Map<String, dynamic> toJson() => _$PercentToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
