// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'system_notification.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$SystemNotificationCWProxy {
  SystemNotification title(String title);

  SystemNotification message(String message);

  SystemNotification level(String? level);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SystemNotification(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SystemNotification(...).copyWith(id: 12, name: "My name")
  /// ````
  SystemNotification call({String title, String message, String? level});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfSystemNotification.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfSystemNotification.copyWith.fieldName(...)`
class _$SystemNotificationCWProxyImpl implements _$SystemNotificationCWProxy {
  const _$SystemNotificationCWProxyImpl(this._value);

  final SystemNotification _value;

  @override
  SystemNotification title(String title) => this(title: title);

  @override
  SystemNotification message(String message) => this(message: message);

  @override
  SystemNotification level(String? level) => this(level: level);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SystemNotification(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SystemNotification(...).copyWith(id: 12, name: "My name")
  /// ````
  SystemNotification call({
    Object? title = const $CopyWithPlaceholder(),
    Object? message = const $CopyWithPlaceholder(),
    Object? level = const $CopyWithPlaceholder(),
  }) {
    return SystemNotification(
      title: title == const $CopyWithPlaceholder()
          ? _value.title
          // ignore: cast_nullable_to_non_nullable
          : title as String,
      message: message == const $CopyWithPlaceholder()
          ? _value.message
          // ignore: cast_nullable_to_non_nullable
          : message as String,
      level: level == const $CopyWithPlaceholder()
          ? _value.level
          // ignore: cast_nullable_to_non_nullable
          : level as String?,
    );
  }
}

extension $SystemNotificationCopyWith on SystemNotification {
  /// Returns a callable class that can be used as follows: `instanceOfSystemNotification.copyWith(...)` or like so:`instanceOfSystemNotification.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$SystemNotificationCWProxy get copyWith =>
      _$SystemNotificationCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SystemNotification _$SystemNotificationFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SystemNotification', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['title', 'message']);
      final val = SystemNotification(
        title: $checkedConvert('title', (v) => v as String),
        message: $checkedConvert('message', (v) => v as String),
        level: $checkedConvert('level', (v) => v as String? ?? 'info'),
      );
      return val;
    });

Map<String, dynamic> _$SystemNotificationToJson(SystemNotification instance) =>
    <String, dynamic>{
      'title': instance.title,
      'message': instance.message,
      'level': ?instance.level,
    };
