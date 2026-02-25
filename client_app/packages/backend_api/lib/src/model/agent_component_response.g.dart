// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'agent_component_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AgentComponentResponseCWProxy {
  AgentComponentResponse id(String? id);

  AgentComponentResponse slug(String? slug);

  AgentComponentResponse name(String? name);

  AgentComponentResponse description(String? description);

  AgentComponentResponse citation(String? citation);

  AgentComponentResponse citationFull(String? citationFull);

  AgentComponentResponse module(String? module);

  AgentComponentResponse componentClass(String? componentClass);

  AgentComponentResponse className(String? className);

  AgentComponentResponse registeredAt(String? registeredAt);

  AgentComponentResponse type(AgentComponentResponseTypeEnum type);

  AgentComponentResponse content(dynamic content);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AgentComponentResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AgentComponentResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AgentComponentResponse call({
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
    AgentComponentResponseTypeEnum type,
    dynamic content,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAgentComponentResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAgentComponentResponse.copyWith.fieldName(...)`
class _$AgentComponentResponseCWProxyImpl
    implements _$AgentComponentResponseCWProxy {
  const _$AgentComponentResponseCWProxyImpl(this._value);

  final AgentComponentResponse _value;

  @override
  AgentComponentResponse id(String? id) => this(id: id);

  @override
  AgentComponentResponse slug(String? slug) => this(slug: slug);

  @override
  AgentComponentResponse name(String? name) => this(name: name);

  @override
  AgentComponentResponse description(String? description) =>
      this(description: description);

  @override
  AgentComponentResponse citation(String? citation) => this(citation: citation);

  @override
  AgentComponentResponse citationFull(String? citationFull) =>
      this(citationFull: citationFull);

  @override
  AgentComponentResponse module(String? module) => this(module: module);

  @override
  AgentComponentResponse componentClass(String? componentClass) =>
      this(componentClass: componentClass);

  @override
  AgentComponentResponse className(String? className) =>
      this(className: className);

  @override
  AgentComponentResponse registeredAt(String? registeredAt) =>
      this(registeredAt: registeredAt);

  @override
  AgentComponentResponse type(AgentComponentResponseTypeEnum type) =>
      this(type: type);

  @override
  AgentComponentResponse content(dynamic content) => this(content: content);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AgentComponentResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AgentComponentResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AgentComponentResponse call({
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
  }) {
    return AgentComponentResponse(
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
          : type as AgentComponentResponseTypeEnum,
      content: content == const $CopyWithPlaceholder()
          ? _value.content
          // ignore: cast_nullable_to_non_nullable
          : content as dynamic,
    );
  }
}

extension $AgentComponentResponseCopyWith on AgentComponentResponse {
  /// Returns a callable class that can be used as follows: `instanceOfAgentComponentResponse.copyWith(...)` or like so:`instanceOfAgentComponentResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AgentComponentResponseCWProxy get copyWith =>
      _$AgentComponentResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AgentComponentResponse _$AgentComponentResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'AgentComponentResponse',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['type']);
    final val = AgentComponentResponse(
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
        (v) => $enumDecode(_$AgentComponentResponseTypeEnumEnumMap, v),
      ),
      content: $checkedConvert('content', (v) => v),
    );
    return val;
  },
  fieldKeyMap: const {
    'citationFull': 'citation_full',
    'componentClass': 'component_class',
    'className': 'class_name',
    'registeredAt': 'registered_at',
  },
);

Map<String, dynamic> _$AgentComponentResponseToJson(
  AgentComponentResponse instance,
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
  'type': _$AgentComponentResponseTypeEnumEnumMap[instance.type]!,
  'content': ?instance.content,
};

const _$AgentComponentResponseTypeEnumEnumMap = {
  AgentComponentResponseTypeEnum.agent: 'agent',
  AgentComponentResponseTypeEnum.processor: 'processor',
};
