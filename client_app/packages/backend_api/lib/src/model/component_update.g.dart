// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'component_update.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ComponentUpdateCWProxy {
  ComponentUpdate content(Object? content);

  ComponentUpdate description(Object? description);

  ComponentUpdate citation(Object? citation);

  ComponentUpdate citationFull(Object? citationFull);

  ComponentUpdate type(Object? type);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ComponentUpdate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ComponentUpdate(...).copyWith(id: 12, name: "My name")
  /// ````
  ComponentUpdate call({
    Object? content,
    Object? description,
    Object? citation,
    Object? citationFull,
    Object? type,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfComponentUpdate.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfComponentUpdate.copyWith.fieldName(...)`
class _$ComponentUpdateCWProxyImpl implements _$ComponentUpdateCWProxy {
  const _$ComponentUpdateCWProxyImpl(this._value);

  final ComponentUpdate _value;

  @override
  ComponentUpdate content(Object? content) => this(content: content);

  @override
  ComponentUpdate description(Object? description) =>
      this(description: description);

  @override
  ComponentUpdate citation(Object? citation) => this(citation: citation);

  @override
  ComponentUpdate citationFull(Object? citationFull) =>
      this(citationFull: citationFull);

  @override
  ComponentUpdate type(Object? type) => this(type: type);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ComponentUpdate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ComponentUpdate(...).copyWith(id: 12, name: "My name")
  /// ````
  ComponentUpdate call({
    Object? content = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? citation = const $CopyWithPlaceholder(),
    Object? citationFull = const $CopyWithPlaceholder(),
    Object? type = const $CopyWithPlaceholder(),
  }) {
    return ComponentUpdate(
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
      type: type == const $CopyWithPlaceholder()
          ? _value.type
          // ignore: cast_nullable_to_non_nullable
          : type as Object?,
    );
  }
}

extension $ComponentUpdateCopyWith on ComponentUpdate {
  /// Returns a callable class that can be used as follows: `instanceOfComponentUpdate.copyWith(...)` or like so:`instanceOfComponentUpdate.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ComponentUpdateCWProxy get copyWith => _$ComponentUpdateCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ComponentUpdate _$ComponentUpdateFromJson(Map<String, dynamic> json) =>
    $checkedCreate('ComponentUpdate', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['content']);
      final val = ComponentUpdate(
        content: $checkedConvert('content', (v) => v),
        description: $checkedConvert('description', (v) => v),
        citation: $checkedConvert('citation', (v) => v),
        citationFull: $checkedConvert('citation_full', (v) => v),
        type: $checkedConvert('type', (v) => v),
      );
      return val;
    }, fieldKeyMap: const {'citationFull': 'citation_full'});

Map<String, dynamic> _$ComponentUpdateToJson(ComponentUpdate instance) =>
    <String, dynamic>{
      'content': instance.content,
      'description': ?instance.description,
      'citation': ?instance.citation,
      'citation_full': ?instance.citationFull,
      'type': ?instance.type,
    };
