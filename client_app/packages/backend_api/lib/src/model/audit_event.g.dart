// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'audit_event.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AuditEventCWProxy {
  AuditEvent id(String id);

  AuditEvent timestamp(DateTime timestamp);

  AuditEvent actorId(String actorId);

  AuditEvent action(String action);

  AuditEvent organizationId(String? organizationId);

  AuditEvent targetId(String? targetId);

  AuditEvent details(Map<String, Object>? details);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AuditEvent(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AuditEvent(...).copyWith(id: 12, name: "My name")
  /// ````
  AuditEvent call({
    String id,
    DateTime timestamp,
    String actorId,
    String action,
    String? organizationId,
    String? targetId,
    Map<String, Object>? details,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAuditEvent.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAuditEvent.copyWith.fieldName(...)`
class _$AuditEventCWProxyImpl implements _$AuditEventCWProxy {
  const _$AuditEventCWProxyImpl(this._value);

  final AuditEvent _value;

  @override
  AuditEvent id(String id) => this(id: id);

  @override
  AuditEvent timestamp(DateTime timestamp) => this(timestamp: timestamp);

  @override
  AuditEvent actorId(String actorId) => this(actorId: actorId);

  @override
  AuditEvent action(String action) => this(action: action);

  @override
  AuditEvent organizationId(String? organizationId) =>
      this(organizationId: organizationId);

  @override
  AuditEvent targetId(String? targetId) => this(targetId: targetId);

  @override
  AuditEvent details(Map<String, Object>? details) => this(details: details);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AuditEvent(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AuditEvent(...).copyWith(id: 12, name: "My name")
  /// ````
  AuditEvent call({
    Object? id = const $CopyWithPlaceholder(),
    Object? timestamp = const $CopyWithPlaceholder(),
    Object? actorId = const $CopyWithPlaceholder(),
    Object? action = const $CopyWithPlaceholder(),
    Object? organizationId = const $CopyWithPlaceholder(),
    Object? targetId = const $CopyWithPlaceholder(),
    Object? details = const $CopyWithPlaceholder(),
  }) {
    return AuditEvent(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
      timestamp: timestamp == const $CopyWithPlaceholder()
          ? _value.timestamp
          // ignore: cast_nullable_to_non_nullable
          : timestamp as DateTime,
      actorId: actorId == const $CopyWithPlaceholder()
          ? _value.actorId
          // ignore: cast_nullable_to_non_nullable
          : actorId as String,
      action: action == const $CopyWithPlaceholder()
          ? _value.action
          // ignore: cast_nullable_to_non_nullable
          : action as String,
      organizationId: organizationId == const $CopyWithPlaceholder()
          ? _value.organizationId
          // ignore: cast_nullable_to_non_nullable
          : organizationId as String?,
      targetId: targetId == const $CopyWithPlaceholder()
          ? _value.targetId
          // ignore: cast_nullable_to_non_nullable
          : targetId as String?,
      details: details == const $CopyWithPlaceholder()
          ? _value.details
          // ignore: cast_nullable_to_non_nullable
          : details as Map<String, Object>?,
    );
  }
}

extension $AuditEventCopyWith on AuditEvent {
  /// Returns a callable class that can be used as follows: `instanceOfAuditEvent.copyWith(...)` or like so:`instanceOfAuditEvent.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AuditEventCWProxy get copyWith => _$AuditEventCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AuditEvent _$AuditEventFromJson(Map<String, dynamic> json) => $checkedCreate(
  'AuditEvent',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const ['id', 'timestamp', 'actor_id', 'action'],
    );
    final val = AuditEvent(
      id: $checkedConvert('id', (v) => v as String),
      timestamp: $checkedConvert(
        'timestamp',
        (v) => DateTime.parse(v as String),
      ),
      actorId: $checkedConvert('actor_id', (v) => v as String),
      action: $checkedConvert('action', (v) => v as String),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      targetId: $checkedConvert('target_id', (v) => v as String?),
      details: $checkedConvert(
        'details',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'actorId': 'actor_id',
    'organizationId': 'organization_id',
    'targetId': 'target_id',
  },
);

Map<String, dynamic> _$AuditEventToJson(AuditEvent instance) =>
    <String, dynamic>{
      'id': instance.id,
      'timestamp': instance.timestamp.toIso8601String(),
      'actor_id': instance.actorId,
      'action': instance.action,
      'organization_id': ?instance.organizationId,
      'target_id': ?instance.targetId,
      'details': ?instance.details,
    };
