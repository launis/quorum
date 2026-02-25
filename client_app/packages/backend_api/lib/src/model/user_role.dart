//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:json_annotation/json_annotation.dart';

/// Enumeration of user permission roles within the system.  Attributes:     ROOT: System Owner / Platform Admin with unrestricted access.     ADMIN: Organization Admin responsible for user management.     MANAGER: Workflow/Process Lead managing execution flows.     MEMBER: Standard User (Audit Runner).     VIEWER: Read-Only Stakeholder.
enum UserRole {
          /// Enumeration of user permission roles within the system.  Attributes:     ROOT: System Owner / Platform Admin with unrestricted access.     ADMIN: Organization Admin responsible for user management.     MANAGER: Workflow/Process Lead managing execution flows.     MEMBER: Standard User (Audit Runner).     VIEWER: Read-Only Stakeholder.
      @JsonValue(r'ROOT')
      ROOT(r'ROOT'),
          /// Enumeration of user permission roles within the system.  Attributes:     ROOT: System Owner / Platform Admin with unrestricted access.     ADMIN: Organization Admin responsible for user management.     MANAGER: Workflow/Process Lead managing execution flows.     MEMBER: Standard User (Audit Runner).     VIEWER: Read-Only Stakeholder.
      @JsonValue(r'ADMIN')
      ADMIN(r'ADMIN'),
          /// Enumeration of user permission roles within the system.  Attributes:     ROOT: System Owner / Platform Admin with unrestricted access.     ADMIN: Organization Admin responsible for user management.     MANAGER: Workflow/Process Lead managing execution flows.     MEMBER: Standard User (Audit Runner).     VIEWER: Read-Only Stakeholder.
      @JsonValue(r'MANAGER')
      MANAGER(r'MANAGER'),
          /// Enumeration of user permission roles within the system.  Attributes:     ROOT: System Owner / Platform Admin with unrestricted access.     ADMIN: Organization Admin responsible for user management.     MANAGER: Workflow/Process Lead managing execution flows.     MEMBER: Standard User (Audit Runner).     VIEWER: Read-Only Stakeholder.
      @JsonValue(r'MEMBER')
      MEMBER(r'MEMBER'),
          /// Enumeration of user permission roles within the system.  Attributes:     ROOT: System Owner / Platform Admin with unrestricted access.     ADMIN: Organization Admin responsible for user management.     MANAGER: Workflow/Process Lead managing execution flows.     MEMBER: Standard User (Audit Runner).     VIEWER: Read-Only Stakeholder.
      @JsonValue(r'VIEWER')
      VIEWER(r'VIEWER');

  const UserRole(this.value);

  final String value;

  @override
  String toString() => value;
}
