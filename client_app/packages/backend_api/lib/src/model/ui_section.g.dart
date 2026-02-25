// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ui_section.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$UiSectionCWProxy {
  UiSection id(String id);

  UiSection type(SectionType type);

  UiSection title(String title);

  UiSection data(Object? data);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UiSection(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UiSection(...).copyWith(id: 12, name: "My name")
  /// ````
  UiSection call({String id, SectionType type, String title, Object? data});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfUiSection.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfUiSection.copyWith.fieldName(...)`
class _$UiSectionCWProxyImpl implements _$UiSectionCWProxy {
  const _$UiSectionCWProxyImpl(this._value);

  final UiSection _value;

  @override
  UiSection id(String id) => this(id: id);

  @override
  UiSection type(SectionType type) => this(type: type);

  @override
  UiSection title(String title) => this(title: title);

  @override
  UiSection data(Object? data) => this(data: data);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UiSection(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UiSection(...).copyWith(id: 12, name: "My name")
  /// ````
  UiSection call({
    Object? id = const $CopyWithPlaceholder(),
    Object? type = const $CopyWithPlaceholder(),
    Object? title = const $CopyWithPlaceholder(),
    Object? data = const $CopyWithPlaceholder(),
  }) {
    return UiSection(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
      type: type == const $CopyWithPlaceholder()
          ? _value.type
          // ignore: cast_nullable_to_non_nullable
          : type as SectionType,
      title: title == const $CopyWithPlaceholder()
          ? _value.title
          // ignore: cast_nullable_to_non_nullable
          : title as String,
      data: data == const $CopyWithPlaceholder()
          ? _value.data
          // ignore: cast_nullable_to_non_nullable
          : data as Object?,
    );
  }
}

extension $UiSectionCopyWith on UiSection {
  /// Returns a callable class that can be used as follows: `instanceOfUiSection.copyWith(...)` or like so:`instanceOfUiSection.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$UiSectionCWProxy get copyWith => _$UiSectionCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UiSection _$UiSectionFromJson(Map<String, dynamic> json) =>
    $checkedCreate('UiSection', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['id', 'type', 'title']);
      final val = UiSection(
        id: $checkedConvert('id', (v) => v as String),
        type: $checkedConvert(
          'type',
          (v) => $enumDecode(_$SectionTypeEnumMap, v),
        ),
        title: $checkedConvert('title', (v) => v as String),
        data: $checkedConvert('data', (v) => v),
      );
      return val;
    });

Map<String, dynamic> _$UiSectionToJson(UiSection instance) => <String, dynamic>{
  'id': instance.id,
  'type': _$SectionTypeEnumMap[instance.type]!,
  'title': instance.title,
  'data': ?instance.data,
};

const _$SectionTypeEnumMap = {
  SectionType.SCORE_CARD: 'SCORE_CARD',
  SectionType.MARKDOWN_BLOCK: 'MARKDOWN_BLOCK',
  SectionType.TIMELINE_FEED: 'TIMELINE_FEED',
  SectionType.HEADER: 'HEADER',
  SectionType.KEY_METRICS: 'KEY_METRICS',
  SectionType.EVIDENCE_LIST: 'EVIDENCE_LIST',
  SectionType.KEY_VALUE_GRID: 'KEY_VALUE_GRID',
  SectionType.DATA_TABLE: 'DATA_TABLE',
  SectionType.ACCORDION: 'ACCORDION',
  SectionType.USAGE_STATS: 'USAGE_STATS',
  SectionType.LOGIC_ANALYSIS: 'LOGIC_ANALYSIS',
  SectionType.STRESS_TEST: 'STRESS_TEST',
  SectionType.CAUSAL_ANALYSIS: 'CAUSAL_ANALYSIS',
  SectionType.PERFORMATIVITY_CHECK: 'PERFORMATIVITY_CHECK',
  SectionType.FACT_CHECK: 'FACT_CHECK',
  SectionType.PROFILER_ANALYSIS: 'PROFILER_ANALYSIS',
  SectionType.ARCHIVIST_CHECK: 'ARCHIVIST_CHECK',
  SectionType.DRIVER_PROFILE: 'DRIVER_PROFILE',
  SectionType.SECURITY_CHECK: 'SECURITY_CHECK',
};
