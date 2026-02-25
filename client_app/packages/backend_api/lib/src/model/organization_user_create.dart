//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/user_role.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'organization_user_create.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class OrganizationUserCreate {
  /// Returns a new [OrganizationUserCreate] instance.
  OrganizationUserCreate({

    required  this.email,

    required  this.displayName,

    required  this.role,

     this.password,
  });

  @JsonKey(
    
    name: r'email',
    required: true,
    
  )


  final String email;



  @JsonKey(
    
    name: r'display_name',
    required: true,
    
  )


  final String displayName;



  @JsonKey(
    
    name: r'role',
    required: true,
    
  )


  final UserRole role;



  @JsonKey(
    
    name: r'password',
    required: false,
    
  )


  final String? password;





    @override
    bool operator ==(Object other) => identical(this, other) || other is OrganizationUserCreate &&
      other.email == email &&
      other.displayName == displayName &&
      other.role == role &&
      other.password == password;

    @override
    int get hashCode =>
        email.hashCode +
        displayName.hashCode +
        role.hashCode +
        (password == null ? 0 : password.hashCode);

  factory OrganizationUserCreate.fromJson(Map<String, dynamic> json) => _$OrganizationUserCreateFromJson(json);

  Map<String, dynamic> toJson() => _$OrganizationUserCreateToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

