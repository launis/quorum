//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/step_definition.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'steps.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class Steps {
  /// Returns a new [Steps] instance.
  Steps({this.dummy});
  final String? dummy;



    @override
    bool operator ==(Object other) => identical(this, other) || other is Steps ;

    @override
    int get hashCode => 0;

  factory Steps.fromJson(Map<String, dynamic> json) => _$StepsFromJson(json);

  Map<String, dynamic> toJson() => _$StepsToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

