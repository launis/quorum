// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'matrix_component_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$MatrixComponentResponseCWProxy {
  MatrixComponentResponse id(String? id);

  MatrixComponentResponse slug(String? slug);

  MatrixComponentResponse name(String? name);

  MatrixComponentResponse description(String? description);

  MatrixComponentResponse citation(String? citation);

  MatrixComponentResponse citationFull(String? citationFull);

  MatrixComponentResponse module(String? module);

  MatrixComponentResponse componentClass(String? componentClass);

  MatrixComponentResponse className(String? className);

  MatrixComponentResponse registeredAt(String? registeredAt);

  MatrixComponentResponse type(MatrixComponentResponseTypeEnum type);

  MatrixComponentResponse content(MatrixContentDTO content);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `MatrixComponentResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// MatrixComponentResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  MatrixComponentResponse call({
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
    MatrixComponentResponseTypeEnum type,
    MatrixContentDTO content,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfMatrixComponentResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfMatrixComponentResponse.copyWith.fieldName(...)`
class _$MatrixComponentResponseCWProxyImpl
    implements _$MatrixComponentResponseCWProxy {
  const _$MatrixComponentResponseCWProxyImpl(this._value);

  final MatrixComponentResponse _value;

  @override
  MatrixComponentResponse id(String? id) => this(id: id);

  @override
  MatrixComponentResponse slug(String? slug) => this(slug: slug);

  @override
  MatrixComponentResponse name(String? name) => this(name: name);

  @override
  MatrixComponentResponse description(String? description) =>
      this(description: description);

  @override
  MatrixComponentResponse citation(String? citation) =>
      this(citation: citation);

  @override
  MatrixComponentResponse citationFull(String? citationFull) =>
      this(citationFull: citationFull);

  @override
  MatrixComponentResponse module(String? module) => this(module: module);

  @override
  MatrixComponentResponse componentClass(String? componentClass) =>
      this(componentClass: componentClass);

  @override
  MatrixComponentResponse className(String? className) =>
      this(className: className);

  @override
  MatrixComponentResponse registeredAt(String? registeredAt) =>
      this(registeredAt: registeredAt);

  @override
  MatrixComponentResponse type(MatrixComponentResponseTypeEnum type) =>
      this(type: type);

  @override
  MatrixComponentResponse content(MatrixContentDTO content) =>
      this(content: content);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `MatrixComponentResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// MatrixComponentResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  MatrixComponentResponse call({
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
    return MatrixComponentResponse(
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
          : type as MatrixComponentResponseTypeEnum,
      content: content == const $CopyWithPlaceholder()
          ? _value.content
          // ignore: cast_nullable_to_non_nullable
          : content as MatrixContentDTO,
    );
  }
}

extension $MatrixComponentResponseCopyWith on MatrixComponentResponse {
  /// Returns a callable class that can be used as follows: `instanceOfMatrixComponentResponse.copyWith(...)` or like so:`instanceOfMatrixComponentResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$MatrixComponentResponseCWProxy get copyWith =>
      _$MatrixComponentResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

MatrixComponentResponse _$MatrixComponentResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'MatrixComponentResponse',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['type', 'content']);
    final val = MatrixComponentResponse(
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
        (v) => $enumDecode(_$MatrixComponentResponseTypeEnumEnumMap, v),
      ),
      content: $checkedConvert(
        'content',
        (v) => MatrixContentDTO.fromJson(v as Map<String, dynamic>),
      ),
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

Map<String, dynamic> _$MatrixComponentResponseToJson(
  MatrixComponentResponse instance,
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
  'type': _$MatrixComponentResponseTypeEnumEnumMap[instance.type]!,
  'content': instance.content.toJson(),
};

const _$MatrixComponentResponseTypeEnumEnumMap = {
  MatrixComponentResponseTypeEnum.evaluationMatrix: 'evaluation_matrix',
};
