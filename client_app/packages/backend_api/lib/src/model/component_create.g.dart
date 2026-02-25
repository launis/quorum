// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'component_create.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ComponentCreateCWProxy {
  ComponentCreate id(Object? id);

  ComponentCreate name(Object? name);

  ComponentCreate type(Object? type);

  ComponentCreate content(Object? content);

  ComponentCreate description(Object? description);

  ComponentCreate citation(Object? citation);

  ComponentCreate citationFull(Object? citationFull);

  ComponentCreate module(Object? module);

  ComponentCreate componentClass(Object? componentClass);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ComponentCreate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ComponentCreate(...).copyWith(id: 12, name: "My name")
  /// ````
  ComponentCreate call({
    Object? id,
    Object? name,
    Object? type,
    Object? content,
    Object? description,
    Object? citation,
    Object? citationFull,
    Object? module,
    Object? componentClass,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfComponentCreate.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfComponentCreate.copyWith.fieldName(...)`
class _$ComponentCreateCWProxyImpl implements _$ComponentCreateCWProxy {
  const _$ComponentCreateCWProxyImpl(this._value);

  final ComponentCreate _value;

  @override
  ComponentCreate id(Object? id) => this(id: id);

  @override
  ComponentCreate name(Object? name) => this(name: name);

  @override
  ComponentCreate type(Object? type) => this(type: type);

  @override
  ComponentCreate content(Object? content) => this(content: content);

  @override
  ComponentCreate description(Object? description) =>
      this(description: description);

  @override
  ComponentCreate citation(Object? citation) => this(citation: citation);

  @override
  ComponentCreate citationFull(Object? citationFull) =>
      this(citationFull: citationFull);

  @override
  ComponentCreate module(Object? module) => this(module: module);

  @override
  ComponentCreate componentClass(Object? componentClass) =>
      this(componentClass: componentClass);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ComponentCreate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ComponentCreate(...).copyWith(id: 12, name: "My name")
  /// ````
  ComponentCreate call({
    Object? id = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? type = const $CopyWithPlaceholder(),
    Object? content = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? citation = const $CopyWithPlaceholder(),
    Object? citationFull = const $CopyWithPlaceholder(),
    Object? module = const $CopyWithPlaceholder(),
    Object? componentClass = const $CopyWithPlaceholder(),
  }) {
    return ComponentCreate(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as Object?,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as Object?,
      type: type == const $CopyWithPlaceholder()
          ? _value.type
          // ignore: cast_nullable_to_non_nullable
          : type as Object?,
      content: content == const $CopyWithPlaceholder()
          ? _value.content
          // ignore: cast_nullable_to_non_nullable
          : content as Object?,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as Object?,
      citation: citation == const $CopyWithPlaceholder()
          ? _value.citation
          // ignore: cast_nullable_to_non_nullable
          : citation as Object?,
      citationFull: citationFull == const $CopyWithPlaceholder()
          ? _value.citationFull
          // ignore: cast_nullable_to_non_nullable
          : citationFull as Object?,
      module: module == const $CopyWithPlaceholder()
          ? _value.module
          // ignore: cast_nullable_to_non_nullable
          : module as Object?,
      componentClass: componentClass == const $CopyWithPlaceholder()
          ? _value.componentClass
          // ignore: cast_nullable_to_non_nullable
          : componentClass as Object?,
    );
  }
}

extension $ComponentCreateCopyWith on ComponentCreate {
  /// Returns a callable class that can be used as follows: `instanceOfComponentCreate.copyWith(...)` or like so:`instanceOfComponentCreate.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ComponentCreateCWProxy get copyWith => _$ComponentCreateCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ComponentCreate _$ComponentCreateFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'ComponentCreate',
      json,
      ($checkedConvert) {
        $checkKeys(json, requiredKeys: const ['name', 'type', 'content']);
        final val = ComponentCreate(
          id: $checkedConvert('id', (v) => v),
          name: $checkedConvert('name', (v) => v),
          type: $checkedConvert('type', (v) => v),
          content: $checkedConvert('content', (v) => v),
          description: $checkedConvert('description', (v) => v),
          citation: $checkedConvert('citation', (v) => v),
          citationFull: $checkedConvert('citation_full', (v) => v),
          module: $checkedConvert('module', (v) => v),
          componentClass: $checkedConvert('component_class', (v) => v),
        );
        return val;
      },
      fieldKeyMap: const {
        'citationFull': 'citation_full',
        'componentClass': 'component_class',
      },
    );

Map<String, dynamic> _$ComponentCreateToJson(ComponentCreate instance) =>
    <String, dynamic>{
      'id': ?instance.id,
      'name': instance.name,
      'type': instance.type,
      'content': instance.content,
      'description': ?instance.description,
      'citation': ?instance.citation,
      'citation_full': ?instance.citationFull,
      'module': ?instance.module,
      'component_class': ?instance.componentClass,
    };
