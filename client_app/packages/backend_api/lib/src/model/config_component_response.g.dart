// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'config_component_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ConfigComponentResponseCWProxy {
  ConfigComponentResponse id(String? id);

  ConfigComponentResponse slug(String? slug);

  ConfigComponentResponse name(String? name);

  ConfigComponentResponse description(String? description);

  ConfigComponentResponse citation(String? citation);

  ConfigComponentResponse citationFull(String? citationFull);

  ConfigComponentResponse module(String? module);

  ConfigComponentResponse componentClass(String? componentClass);

  ConfigComponentResponse className(String? className);

  ConfigComponentResponse registeredAt(String? registeredAt);

  ConfigComponentResponse type(ConfigComponentResponseTypeEnum type);

  ConfigComponentResponse content(List<Object> content);

  ConfigComponentResponse uiHints(Map<String, Object>? uiHints);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ConfigComponentResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ConfigComponentResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ConfigComponentResponse call({
    String? id,
    String? slug,
    String? name,
    String? description,
    String? citation,
    String? citationFull,
    String? module,
    String? componentClass,
    String? className,
    String? registeredAt,
    ConfigComponentResponseTypeEnum type,
    List<Object> content,
    Map<String, Object>? uiHints,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfConfigComponentResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfConfigComponentResponse.copyWith.fieldName(...)`
class _$ConfigComponentResponseCWProxyImpl
    implements _$ConfigComponentResponseCWProxy {
  const _$ConfigComponentResponseCWProxyImpl(this._value);

  final ConfigComponentResponse _value;

  @override
  ConfigComponentResponse id(String? id) => this(id: id);

  @override
  ConfigComponentResponse slug(String? slug) => this(slug: slug);

  @override
  ConfigComponentResponse name(String? name) => this(name: name);

  @override
  ConfigComponentResponse description(String? description) =>
      this(description: description);

  @override
  ConfigComponentResponse citation(String? citation) =>
      this(citation: citation);

  @override
  ConfigComponentResponse citationFull(String? citationFull) =>
      this(citationFull: citationFull);

  @override
  ConfigComponentResponse module(String? module) => this(module: module);

  @override
  ConfigComponentResponse componentClass(String? componentClass) =>
      this(componentClass: componentClass);

  @override
  ConfigComponentResponse className(String? className) =>
      this(className: className);

  @override
  ConfigComponentResponse registeredAt(String? registeredAt) =>
      this(registeredAt: registeredAt);

  @override
  ConfigComponentResponse type(ConfigComponentResponseTypeEnum type) =>
      this(type: type);

  @override
  ConfigComponentResponse content(List<Object> content) =>
      this(content: content);

  @override
  ConfigComponentResponse uiHints(Map<String, Object>? uiHints) =>
      this(uiHints: uiHints);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ConfigComponentResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ConfigComponentResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ConfigComponentResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? slug = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? citation = const $CopyWithPlaceholder(),
    Object? citationFull = const $CopyWithPlaceholder(),
    Object? module = const $CopyWithPlaceholder(),
    Object? componentClass = const $CopyWithPlaceholder(),
    Object? className = const $CopyWithPlaceholder(),
    Object? registeredAt = const $CopyWithPlaceholder(),
    Object? type = const $CopyWithPlaceholder(),
    Object? content = const $CopyWithPlaceholder(),
    Object? uiHints = const $CopyWithPlaceholder(),
  }) {
    return ConfigComponentResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String?,
      slug: slug == const $CopyWithPlaceholder()
          ? _value.slug
          // ignore: cast_nullable_to_non_nullable
          : slug as String?,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String?,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as String?,
      citation: citation == const $CopyWithPlaceholder()
          ? _value.citation
          // ignore: cast_nullable_to_non_nullable
          : citation as String?,
      citationFull: citationFull == const $CopyWithPlaceholder()
          ? _value.citationFull
          // ignore: cast_nullable_to_non_nullable
          : citationFull as String?,
      module: module == const $CopyWithPlaceholder()
          ? _value.module
          // ignore: cast_nullable_to_non_nullable
          : module as String?,
      componentClass: componentClass == const $CopyWithPlaceholder()
          ? _value.componentClass
          // ignore: cast_nullable_to_non_nullable
          : componentClass as String?,
      className: className == const $CopyWithPlaceholder()
          ? _value.className
          // ignore: cast_nullable_to_non_nullable
          : className as String?,
      registeredAt: registeredAt == const $CopyWithPlaceholder()
          ? _value.registeredAt
          // ignore: cast_nullable_to_non_nullable
          : registeredAt as String?,
      type: type == const $CopyWithPlaceholder()
          ? _value.type
          // ignore: cast_nullable_to_non_nullable
          : type as ConfigComponentResponseTypeEnum,
      content: content == const $CopyWithPlaceholder()
          ? _value.content
          // ignore: cast_nullable_to_non_nullable
          : content as List<Object>,
      uiHints: uiHints == const $CopyWithPlaceholder()
          ? _value.uiHints
          // ignore: cast_nullable_to_non_nullable
          : uiHints as Map<String, Object>?,
    );
  }
}

extension $ConfigComponentResponseCopyWith on ConfigComponentResponse {
  /// Returns a callable class that can be used as follows: `instanceOfConfigComponentResponse.copyWith(...)` or like so:`instanceOfConfigComponentResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ConfigComponentResponseCWProxy get copyWith =>
      _$ConfigComponentResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ConfigComponentResponse _$ConfigComponentResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'ConfigComponentResponse',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['type', 'content']);
    final val = ConfigComponentResponse(
      id: $checkedConvert('id', (v) => v as String?),
      slug: $checkedConvert('slug', (v) => v as String?),
      name: $checkedConvert('name', (v) => v as String?),
      description: $checkedConvert('description', (v) => v as String?),
      citation: $checkedConvert('citation', (v) => v as String?),
      citationFull: $checkedConvert('citation_full', (v) => v as String?),
      module: $checkedConvert('module', (v) => v as String?),
      componentClass: $checkedConvert('component_class', (v) => v as String?),
      className: $checkedConvert('class_name', (v) => v as String?),
      registeredAt: $checkedConvert('registered_at', (v) => v as String?),
      type: $checkedConvert(
        'type',
        (v) => $enumDecode(_$ConfigComponentResponseTypeEnumEnumMap, v),
      ),
      content: $checkedConvert(
        'content',
        (v) => (v as List<dynamic>).map((e) => e as Object).toList(),
      ),
      uiHints: $checkedConvert(
        'ui_hints',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'citationFull': 'citation_full',
    'componentClass': 'component_class',
    'className': 'class_name',
    'registeredAt': 'registered_at',
    'uiHints': 'ui_hints',
  },
);

Map<String, dynamic> _$ConfigComponentResponseToJson(
  ConfigComponentResponse instance,
) => <String, dynamic>{
  'id': ?instance.id,
  'slug': ?instance.slug,
  'name': ?instance.name,
  'description': ?instance.description,
  'citation': ?instance.citation,
  'citation_full': ?instance.citationFull,
  'module': ?instance.module,
  'component_class': ?instance.componentClass,
  'class_name': ?instance.className,
  'registered_at': ?instance.registeredAt,
  'type': _$ConfigComponentResponseTypeEnumEnumMap[instance.type]!,
  'content': instance.content,
  'ui_hints': ?instance.uiHints,
};

const _$ConfigComponentResponseTypeEnumEnumMap = {
  ConfigComponentResponseTypeEnum.outputConfig: 'output_config',
  ConfigComponentResponseTypeEnum.knowledgeBase: 'knowledge_base',
};
