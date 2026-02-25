// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'registry_component_item.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$RegistryComponentItemCWProxy {
  RegistryComponentItem id(String? id);

  RegistryComponentItem slug(String? slug);

  RegistryComponentItem name(String name);

  RegistryComponentItem type(String type);

  RegistryComponentItem description(String? description);

  RegistryComponentItem content(Object? content);

  RegistryComponentItem citation(String? citation);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `RegistryComponentItem(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// RegistryComponentItem(...).copyWith(id: 12, name: "My name")
  /// ````
  RegistryComponentItem call({
    String? id,
    String? slug,
    String name,
    String type,
    String? description,
    Object? content,
    String? citation,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfRegistryComponentItem.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfRegistryComponentItem.copyWith.fieldName(...)`
class _$RegistryComponentItemCWProxyImpl
    implements _$RegistryComponentItemCWProxy {
  const _$RegistryComponentItemCWProxyImpl(this._value);

  final RegistryComponentItem _value;

  @override
  RegistryComponentItem id(String? id) => this(id: id);

  @override
  RegistryComponentItem slug(String? slug) => this(slug: slug);

  @override
  RegistryComponentItem name(String name) => this(name: name);

  @override
  RegistryComponentItem type(String type) => this(type: type);

  @override
  RegistryComponentItem description(String? description) =>
      this(description: description);

  @override
  RegistryComponentItem content(Object? content) => this(content: content);

  @override
  RegistryComponentItem citation(String? citation) => this(citation: citation);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `RegistryComponentItem(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// RegistryComponentItem(...).copyWith(id: 12, name: "My name")
  /// ````
  RegistryComponentItem call({
    Object? id = const $CopyWithPlaceholder(),
    Object? slug = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? type = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? content = const $CopyWithPlaceholder(),
    Object? citation = const $CopyWithPlaceholder(),
  }) {
    return RegistryComponentItem(
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
          : name as String,
      type: type == const $CopyWithPlaceholder()
          ? _value.type
          // ignore: cast_nullable_to_non_nullable
          : type as String,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as String?,
      content: content == const $CopyWithPlaceholder()
          ? _value.content
          // ignore: cast_nullable_to_non_nullable
          : content as Object?,
      citation: citation == const $CopyWithPlaceholder()
          ? _value.citation
          // ignore: cast_nullable_to_non_nullable
          : citation as String?,
    );
  }
}

extension $RegistryComponentItemCopyWith on RegistryComponentItem {
  /// Returns a callable class that can be used as follows: `instanceOfRegistryComponentItem.copyWith(...)` or like so:`instanceOfRegistryComponentItem.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$RegistryComponentItemCWProxy get copyWith =>
      _$RegistryComponentItemCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

RegistryComponentItem _$RegistryComponentItemFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('RegistryComponentItem', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['name', 'type']);
  final val = RegistryComponentItem(
    id: $checkedConvert('id', (v) => v as String?),
    slug: $checkedConvert('slug', (v) => v as String?),
    name: $checkedConvert('name', (v) => v as String),
    type: $checkedConvert('type', (v) => v as String),
    description: $checkedConvert('description', (v) => v as String?),
    content: $checkedConvert('content', (v) => v),
    citation: $checkedConvert('citation', (v) => v as String?),
  );
  return val;
});

Map<String, dynamic> _$RegistryComponentItemToJson(
  RegistryComponentItem instance,
) => <String, dynamic>{
  'id': ?instance.id,
  'slug': ?instance.slug,
  'name': instance.name,
  'type': instance.type,
  'description': ?instance.description,
  'content': ?instance.content,
  'citation': ?instance.citation,
};
