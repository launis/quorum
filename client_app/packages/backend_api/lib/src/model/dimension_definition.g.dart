// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dimension_definition.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$DimensionDefinitionCWProxy {
  DimensionDefinition id(String? id);

  DimensionDefinition slug(String? slug);

  DimensionDefinition label(String label);

  DimensionDefinition description(String? description);

  DimensionDefinition isSystem(bool? isSystem);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `DimensionDefinition(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// DimensionDefinition(...).copyWith(id: 12, name: "My name")
  /// ````
  DimensionDefinition call({
    String? id,
    String? slug,
    String label,
    String? description,
    bool? isSystem,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfDimensionDefinition.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfDimensionDefinition.copyWith.fieldName(...)`
class _$DimensionDefinitionCWProxyImpl implements _$DimensionDefinitionCWProxy {
  const _$DimensionDefinitionCWProxyImpl(this._value);

  final DimensionDefinition _value;

  @override
  DimensionDefinition id(String? id) => this(id: id);

  @override
  DimensionDefinition slug(String? slug) => this(slug: slug);

  @override
  DimensionDefinition label(String label) => this(label: label);

  @override
  DimensionDefinition description(String? description) =>
      this(description: description);

  @override
  DimensionDefinition isSystem(bool? isSystem) => this(isSystem: isSystem);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `DimensionDefinition(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// DimensionDefinition(...).copyWith(id: 12, name: "My name")
  /// ````
  DimensionDefinition call({
    Object? id = const $CopyWithPlaceholder(),
    Object? slug = const $CopyWithPlaceholder(),
    Object? label = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? isSystem = const $CopyWithPlaceholder(),
  }) {
    return DimensionDefinition(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String?,
      slug: slug == const $CopyWithPlaceholder()
          ? _value.slug
          // ignore: cast_nullable_to_non_nullable
          : slug as String?,
      label: label == const $CopyWithPlaceholder()
          ? _value.label
          // ignore: cast_nullable_to_non_nullable
          : label as String,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as String?,
      isSystem: isSystem == const $CopyWithPlaceholder()
          ? _value.isSystem
          // ignore: cast_nullable_to_non_nullable
          : isSystem as bool?,
    );
  }
}

extension $DimensionDefinitionCopyWith on DimensionDefinition {
  /// Returns a callable class that can be used as follows: `instanceOfDimensionDefinition.copyWith(...)` or like so:`instanceOfDimensionDefinition.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$DimensionDefinitionCWProxy get copyWith =>
      _$DimensionDefinitionCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

DimensionDefinition _$DimensionDefinitionFromJson(Map<String, dynamic> json) =>
    $checkedCreate('DimensionDefinition', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['label']);
      final val = DimensionDefinition(
        id: $checkedConvert('id', (v) => v as String?),
        slug: $checkedConvert('slug', (v) => v as String?),
        label: $checkedConvert('label', (v) => v as String),
        description: $checkedConvert('description', (v) => v as String?),
        isSystem: $checkedConvert('is_system', (v) => v as bool? ?? false),
      );
      return val;
    }, fieldKeyMap: const {'isSystem': 'is_system'});

Map<String, dynamic> _$DimensionDefinitionToJson(
  DimensionDefinition instance,
) => <String, dynamic>{
  'id': ?instance.id,
  'slug': ?instance.slug,
  'label': instance.label,
  'description': ?instance.description,
  'is_system': ?instance.isSystem,
};
