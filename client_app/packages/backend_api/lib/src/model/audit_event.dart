//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'audit_event.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class AuditEvent {
  /// Returns a new [AuditEvent] instance.
  AuditEvent({

    required  this.id,

    required  this.timestamp,

    required  this.actorId,

    required  this.action,

     this.organizationId,

     this.targetId,

     this.details,
  });

  @JsonKey(
    
    name: r'id',
    required: true,
    
  )


  final String id;



  @JsonKey(
    
    name: r'timestamp',
    required: true,
    
  )


  final DateTime timestamp;



  @JsonKey(
    
    name: r'actor_id',
    required: true,
    
  )


  final String actorId;



  @JsonKey(
    
    name: r'action',
    required: true,
    
  )


  final String action;



  @JsonKey(
    
    name: r'organization_id',
    required: false,
    
  )


  final String? organizationId;



  @JsonKey(
    
    name: r'target_id',
    required: false,
    
  )


  final String? targetId;



  @JsonKey(
    
    name: r'details',
    required: false,
    
  )


  final Map<String, Object>? details;





    @override
    bool operator ==(Object other) => identical(this, other) || other is AuditEvent &&
      other.id == id &&
      other.timestamp == timestamp &&
      other.actorId == actorId &&
      other.action == action &&
      other.organizationId == organizationId &&
      other.targetId == targetId &&
      other.details == details;

    @override
    int get hashCode =>
        id.hashCode +
        timestamp.hashCode +
        actorId.hashCode +
        action.hashCode +
        (organizationId == null ? 0 : organizationId.hashCode) +
        (targetId == null ? 0 : targetId.hashCode) +
        details.hashCode;

  factory AuditEvent.fromJson(Map<String, dynamic> json) => _$AuditEventFromJson(json);

  Map<String, dynamic> toJson() => _$AuditEventToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

