//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/user_role.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'user_admin_view.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class UserAdminView {
  /// Returns a new [UserAdminView] instance.
  UserAdminView({

    required  this.email,

     this.displayName,

     this.role = UserRole.MEMBER,

     this.organizationId,

     this.isActive = true,

     this.language = UserAdminViewLanguageEnum.fi,

     this.themeMode = UserAdminViewThemeModeEnum.system,

    required  this.id,

     this.slug,

    required  this.createdAt,

     this.createdBy,

     this.lastLoginAt,

     this.executionCount = 0,
  });

      /// User email address
  @JsonKey(
    
    name: r'email',
    required: true,
    
  )


  final String email;



  @JsonKey(
    
    name: r'display_name',
    required: false,
    
  )


  final String? displayName;



      /// Assigned permission role
  @JsonKey(
    defaultValue: UserRole.MEMBER,
    name: r'role',
    required: false,
    
  )


  final UserRole? role;



  @JsonKey(
    
    name: r'organization_id',
    required: false,
    
  )


  final String? organizationId;



      /// Is the account active?
  @JsonKey(
    defaultValue: true,
    name: r'is_active',
    required: false,
    
  )


  final bool? isActive;



      /// Preferred UI language
  @JsonKey(
    defaultValue: 'fi',
    name: r'language',
    required: false,
    
  )


  final UserAdminViewLanguageEnum? language;



      /// Preferred Theme Mode
  @JsonKey(
    defaultValue: 'system',
    name: r'theme_mode',
    required: false,
    
  )


  final UserAdminViewThemeModeEnum? themeMode;



  @JsonKey(
    
    name: r'id',
    required: true,
    
  )


  final String id;



  @JsonKey(
    
    name: r'slug',
    required: false,
    
  )


  final String? slug;



  @JsonKey(
    
    name: r'created_at',
    required: true,
    
  )


  final DateTime createdAt;



  @JsonKey(
    
    name: r'created_by',
    required: false,
    
  )


  final String? createdBy;



  @JsonKey(
    
    name: r'last_login_at',
    required: false,
    
  )


  final DateTime? lastLoginAt;



  @JsonKey(
    defaultValue: 0,
    name: r'execution_count',
    required: false,
    
  )


  final int? executionCount;





    @override
    bool operator ==(Object other) => identical(this, other) || other is UserAdminView &&
      other.email == email &&
      other.displayName == displayName &&
      other.role == role &&
      other.organizationId == organizationId &&
      other.isActive == isActive &&
      other.language == language &&
      other.themeMode == themeMode &&
      other.id == id &&
      other.slug == slug &&
      other.createdAt == createdAt &&
      other.createdBy == createdBy &&
      other.lastLoginAt == lastLoginAt &&
      other.executionCount == executionCount;

    @override
    int get hashCode =>
        email.hashCode +
        (displayName == null ? 0 : displayName.hashCode) +
        role.hashCode +
        (organizationId == null ? 0 : organizationId.hashCode) +
        isActive.hashCode +
        language.hashCode +
        themeMode.hashCode +
        id.hashCode +
        (slug == null ? 0 : slug.hashCode) +
        createdAt.hashCode +
        (createdBy == null ? 0 : createdBy.hashCode) +
        (lastLoginAt == null ? 0 : lastLoginAt.hashCode) +
        executionCount.hashCode;

  factory UserAdminView.fromJson(Map<String, dynamic> json) => _$UserAdminViewFromJson(json);

  Map<String, dynamic> toJson() => _$UserAdminViewToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

/// Preferred UI language
enum UserAdminViewLanguageEnum {
    /// Preferred UI language
@JsonValue(r'fi')
fi(r'fi'),
    /// Preferred UI language
@JsonValue(r'en')
en(r'en'),
    /// Preferred UI language
@JsonValue(r'sv')
sv(r'sv');

const UserAdminViewLanguageEnum(this.value);

final String value;

@override
String toString() => value;
}


/// Preferred Theme Mode
enum UserAdminViewThemeModeEnum {
    /// Preferred Theme Mode
@JsonValue(r'system')
system(r'system'),
    /// Preferred Theme Mode
@JsonValue(r'light')
light(r'light'),
    /// Preferred Theme Mode
@JsonValue(r'dark')
dark(r'dark');

const UserAdminViewThemeModeEnum(this.value);

final String value;

@override
String toString() => value;
}


