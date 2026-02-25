// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'matrix_content_dto.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$MatrixContentDTOCWProxy {
  MatrixContentDTO scale(Map<String, int>? scale);

  MatrixContentDTO criteria(List<Map<String, Object>>? criteria);

  MatrixContentDTO roleDescription(String? roleDescription);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `MatrixContentDTO(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// MatrixContentDTO(...).copyWith(id: 12, name: "My name")
  /// ````
  MatrixContentDTO call({
    Map<String, int>? scale,
    List<Map<String, Object>>? criteria,
    String? roleDescription,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfMatrixContentDTO.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfMatrixContentDTO.copyWith.fieldName(...)`
class _$MatrixContentDTOCWProxyImpl implements _$MatrixContentDTOCWProxy {
  const _$MatrixContentDTOCWProxyImpl(this._value);

  final MatrixContentDTO _value;

  @override
  MatrixContentDTO scale(Map<String, int>? scale) => this(scale: scale);

  @override
  MatrixContentDTO criteria(List<Map<String, Object>>? criteria) =>
      this(criteria: criteria);

  @override
  MatrixContentDTO roleDescription(String? roleDescription) =>
      this(roleDescription: roleDescription);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `MatrixContentDTO(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// MatrixContentDTO(...).copyWith(id: 12, name: "My name")
  /// ````
  MatrixContentDTO call({
    Object? scale = const $CopyWithPlaceholder(),
    Object? criteria = const $CopyWithPlaceholder(),
    Object? roleDescription = const $CopyWithPlaceholder(),
  }) {
    return MatrixContentDTO(
      scale: scale == const $CopyWithPlaceholder()
          ? _value.scale
          // ignore: cast_nullable_to_non_nullable
          : scale as Map<String, int>?,
      criteria: criteria == const $CopyWithPlaceholder()
          ? _value.criteria
          // ignore: cast_nullable_to_non_nullable
          : criteria as List<Map<String, Object>>?,
      roleDescription: roleDescription == const $CopyWithPlaceholder()
          ? _value.roleDescription
          // ignore: cast_nullable_to_non_nullable
          : roleDescription as String?,
    );
  }
}

extension $MatrixContentDTOCopyWith on MatrixContentDTO {
  /// Returns a callable class that can be used as follows: `instanceOfMatrixContentDTO.copyWith(...)` or like so:`instanceOfMatrixContentDTO.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$MatrixContentDTOCWProxy get copyWith => _$MatrixContentDTOCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

MatrixContentDTO _$MatrixContentDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'MatrixContentDTO',
      json,
      ($checkedConvert) {
        final val = MatrixContentDTO(
          scale: $checkedConvert(
            'scale',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, (e as num).toInt()),
            ),
          ),
          criteria: $checkedConvert(
            'criteria',
            (v) => (v as List<dynamic>?)
                ?.map(
                  (e) => (e as Map<String, dynamic>).map(
                    (k, e) => MapEntry(k, e as Object),
                  ),
                )
                .toList(),
          ),
          roleDescription: $checkedConvert(
            'role_description',
            (v) => v as String?,
          ),
        );
        return val;
      },
      fieldKeyMap: const {'roleDescription': 'role_description'},
    );

Map<String, dynamic> _$MatrixContentDTOToJson(MatrixContentDTO instance) =>
    <String, dynamic>{
      'scale': ?instance.scale,
      'criteria': ?instance.criteria,
      'role_description': ?instance.roleDescription,
    };
