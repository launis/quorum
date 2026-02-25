// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'text_component_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$TextComponentResponseCWProxy {
  TextComponentResponse id(String? id);

  TextComponentResponse slug(String? slug);

  TextComponentResponse name(String? name);

  TextComponentResponse description(String? description);

  TextComponentResponse citation(String? citation);

  TextComponentResponse citationFull(String? citationFull);

  TextComponentResponse module(String? module);

  TextComponentResponse componentClass(String? componentClass);

  TextComponentResponse className(String? className);

  TextComponentResponse registeredAt(String? registeredAt);

  TextComponentResponse type(String type);

  TextComponentResponse content(String content);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TextComponentResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TextComponentResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  TextComponentResponse call({
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
    String type,
    String content,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfTextComponentResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfTextComponentResponse.copyWith.fieldName(...)`
class _$TextComponentResponseCWProxyImpl
    implements _$TextComponentResponseCWProxy {
  const _$TextComponentResponseCWProxyImpl(this._value);

  final TextComponentResponse _value;

  @override
  TextComponentResponse id(String? id) => this(id: id);

  @override
  TextComponentResponse slug(String? slug) => this(slug: slug);

  @override
  TextComponentResponse name(String? name) => this(name: name);

  @override
  TextComponentResponse description(String? description) =>
      this(description: description);

  @override
  TextComponentResponse citation(String? citation) => this(citation: citation);

  @override
  TextComponentResponse citationFull(String? citationFull) =>
      this(citationFull: citationFull);

  @override
  TextComponentResponse module(String? module) => this(module: module);

  @override
  TextComponentResponse componentClass(String? componentClass) =>
      this(componentClass: componentClass);

  @override
  TextComponentResponse className(String? className) =>
      this(className: className);

  @override
  TextComponentResponse registeredAt(String? registeredAt) =>
      this(registeredAt: registeredAt);

  @override
  TextComponentResponse type(String type) => this(type: type);

  @override
  TextComponentResponse content(String content) => this(content: content);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TextComponentResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TextComponentResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  TextComponentResponse call({
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
    return TextComponentResponse(
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
          : type as String,
      content: content == const $CopyWithPlaceholder()
          ? _value.content
          // ignore: cast_nullable_to_non_nullable
          : content as String,
    );
  }
}

extension $TextComponentResponseCopyWith on TextComponentResponse {
  /// Returns a callable class that can be used as follows: `instanceOfTextComponentResponse.copyWith(...)` or like so:`instanceOfTextComponentResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$TextComponentResponseCWProxy get copyWith =>
      _$TextComponentResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TextComponentResponse _$TextComponentResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'TextComponentResponse',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['type', 'content']);
    final val = TextComponentResponse(
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
      type: $checkedConvert('type', (v) => v as String),
      content: $checkedConvert('content', (v) => v as String),
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

Map<String, dynamic> _$TextComponentResponseToJson(
  TextComponentResponse instance,
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
  'type': instance.type,
  'content': instance.content,
};
