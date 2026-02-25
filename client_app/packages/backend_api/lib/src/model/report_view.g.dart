// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_view.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ReportViewCWProxy {
  ReportView viewId(String viewId);

  ReportView title(String? title);

  ReportView statusTheme(String? statusTheme);

  ReportView sections(List<UiSection>? sections);

  ReportView metrics(Map<String, Object>? metrics);

  ReportView systemNotification(SystemNotification? systemNotification);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ReportView(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ReportView(...).copyWith(id: 12, name: "My name")
  /// ````
  ReportView call({
    String viewId,
    String? title,
    String? statusTheme,
    List<UiSection>? sections,
    Map<String, Object>? metrics,
    SystemNotification? systemNotification,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfReportView.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfReportView.copyWith.fieldName(...)`
class _$ReportViewCWProxyImpl implements _$ReportViewCWProxy {
  const _$ReportViewCWProxyImpl(this._value);

  final ReportView _value;

  @override
  ReportView viewId(String viewId) => this(viewId: viewId);

  @override
  ReportView title(String? title) => this(title: title);

  @override
  ReportView statusTheme(String? statusTheme) => this(statusTheme: statusTheme);

  @override
  ReportView sections(List<UiSection>? sections) => this(sections: sections);

  @override
  ReportView metrics(Map<String, Object>? metrics) => this(metrics: metrics);

  @override
  ReportView systemNotification(SystemNotification? systemNotification) =>
      this(systemNotification: systemNotification);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ReportView(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ReportView(...).copyWith(id: 12, name: "My name")
  /// ````
  ReportView call({
    Object? viewId = const $CopyWithPlaceholder(),
    Object? title = const $CopyWithPlaceholder(),
    Object? statusTheme = const $CopyWithPlaceholder(),
    Object? sections = const $CopyWithPlaceholder(),
    Object? metrics = const $CopyWithPlaceholder(),
    Object? systemNotification = const $CopyWithPlaceholder(),
  }) {
    return ReportView(
      viewId: viewId == const $CopyWithPlaceholder()
          ? _value.viewId
          // ignore: cast_nullable_to_non_nullable
          : viewId as String,
      title: title == const $CopyWithPlaceholder()
          ? _value.title
          // ignore: cast_nullable_to_non_nullable
          : title as String?,
      statusTheme: statusTheme == const $CopyWithPlaceholder()
          ? _value.statusTheme
          // ignore: cast_nullable_to_non_nullable
          : statusTheme as String?,
      sections: sections == const $CopyWithPlaceholder()
          ? _value.sections
          // ignore: cast_nullable_to_non_nullable
          : sections as List<UiSection>?,
      metrics: metrics == const $CopyWithPlaceholder()
          ? _value.metrics
          // ignore: cast_nullable_to_non_nullable
          : metrics as Map<String, Object>?,
      systemNotification: systemNotification == const $CopyWithPlaceholder()
          ? _value.systemNotification
          // ignore: cast_nullable_to_non_nullable
          : systemNotification as SystemNotification?,
    );
  }
}

extension $ReportViewCopyWith on ReportView {
  /// Returns a callable class that can be used as follows: `instanceOfReportView.copyWith(...)` or like so:`instanceOfReportView.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ReportViewCWProxy get copyWith => _$ReportViewCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ReportView _$ReportViewFromJson(Map<String, dynamic> json) => $checkedCreate(
  'ReportView',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['view_id']);
    final val = ReportView(
      viewId: $checkedConvert('view_id', (v) => v as String),
      title: $checkedConvert(
        'title',
        (v) => v as String? ?? 'Auditintiraportti',
      ),
      statusTheme: $checkedConvert(
        'status_theme',
        (v) => v as String? ?? 'success',
      ),
      sections: $checkedConvert(
        'sections',
        (v) => (v as List<dynamic>?)
            ?.map((e) => UiSection.fromJson(e as Map<String, dynamic>))
            .toList(),
      ),
      metrics: $checkedConvert(
        'metrics',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
      systemNotification: $checkedConvert(
        'system_notification',
        (v) => v == null
            ? null
            : SystemNotification.fromJson(v as Map<String, dynamic>),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'viewId': 'view_id',
    'statusTheme': 'status_theme',
    'systemNotification': 'system_notification',
  },
);

Map<String, dynamic> _$ReportViewToJson(ReportView instance) =>
    <String, dynamic>{
      'view_id': instance.viewId,
      'title': ?instance.title,
      'status_theme': ?instance.statusTheme,
      'sections': ?instance.sections?.map((e) => e.toJson()).toList(),
      'metrics': ?instance.metrics,
      'system_notification': ?instance.systemNotification?.toJson(),
    };
