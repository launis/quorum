//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/system_notification.dart';
import 'package:backend_api/src/model/ui_section.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'report_view.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ReportView {
  /// Returns a new [ReportView] instance.
  ReportView({
    required this.viewId,

    this.title = 'Auditintiraportti',

    this.statusTheme = 'success',

    this.sections,

    this.metrics,

    this.systemNotification,
  });

  /// The Execution ID
  @JsonKey(name: r'view_id', required: true)
  final String viewId;

  /// Page title
  @JsonKey(defaultValue: 'Auditintiraportti', name: r'title', required: false)
  final String? title;

  /// Visual theme: 'success' | 'warning' | 'danger'
  @JsonKey(defaultValue: 'success', name: r'status_theme', required: false)
  final String? statusTheme;

  /// Ordered list of UI sections
  @JsonKey(name: r'sections', required: false)
  final List<UiSection>? sections;

  @JsonKey(name: r'metrics', required: false)
  final Map<String, Object>? metrics;

  @JsonKey(name: r'system_notification', required: false)
  final SystemNotification? systemNotification;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ReportView &&
          other.viewId == viewId &&
          other.title == title &&
          other.statusTheme == statusTheme &&
          other.sections == sections &&
          other.metrics == metrics &&
          other.systemNotification == systemNotification;

  @override
  int get hashCode =>
      viewId.hashCode +
      title.hashCode +
      statusTheme.hashCode +
      sections.hashCode +
      (metrics == null ? 0 : metrics.hashCode) +
      (systemNotification == null ? 0 : systemNotification.hashCode);

  factory ReportView.fromJson(Map<String, dynamic> json) =>
      _$ReportViewFromJson(json);

  Map<String, dynamic> toJson() => _$ReportViewToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
