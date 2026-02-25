//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/user_role.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'update_role_request.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class UpdateRoleRequest {
  /// Returns a new [UpdateRoleRequest] instance.
  UpdateRoleRequest({

    required  this.role,
  });

  @JsonKey(
    
    name: r'role',
    required: true,
    
  )


  final UserRole role;





    @override
    bool operator ==(Object other) => identical(this, other) || other is UpdateRoleRequest &&
      other.role == role;

    @override
    int get hashCode =>
        role.hashCode;

  factory UpdateRoleRequest.fromJson(Map<String, dynamic> json) => _$UpdateRoleRequestFromJson(json);

  Map<String, dynamic> toJson() => _$UpdateRoleRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

