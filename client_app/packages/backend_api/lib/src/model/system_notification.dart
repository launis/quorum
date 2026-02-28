//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'system_notification.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class SystemNotification {
  /// Returns a new [SystemNotification] instance.
  SystemNotification({
    required this.title,

    required this.message,

    this.level = 'info',
  });

  @JsonKey(name: r'title', required: true)
  final String title;

  @JsonKey(name: r'message', required: true)
  final String message;

  @JsonKey(defaultValue: 'info', name: r'level', required: false)
  final String? level;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SystemNotification &&
          other.title == title &&
          other.message == message &&
          other.level == level;

  @override
  int get hashCode => title.hashCode + message.hashCode + level.hashCode;

  factory SystemNotification.fromJson(Map<String, dynamic> json) =>
      _$SystemNotificationFromJson(json);

  Map<String, dynamic> toJson() => _$SystemNotificationToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
