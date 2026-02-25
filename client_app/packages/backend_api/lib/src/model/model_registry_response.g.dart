// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'model_registry_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ModelRegistryResponseCWProxy {
  ModelRegistryResponse models(Map<String, Map<String, Object>>? models);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ModelRegistryResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ModelRegistryResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ModelRegistryResponse call({Map<String, Map<String, Object>>? models});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfModelRegistryResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfModelRegistryResponse.copyWith.fieldName(...)`
class _$ModelRegistryResponseCWProxyImpl
    implements _$ModelRegistryResponseCWProxy {
  const _$ModelRegistryResponseCWProxyImpl(this._value);

  final ModelRegistryResponse _value;

  @override
  ModelRegistryResponse models(Map<String, Map<String, Object>>? models) =>
      this(models: models);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ModelRegistryResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ModelRegistryResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ModelRegistryResponse call({Object? models = const $CopyWithPlaceholder()}) {
    return ModelRegistryResponse(
      models: models == const $CopyWithPlaceholder()
          ? _value.models
          // ignore: cast_nullable_to_non_nullable
          : models as Map<String, Map<String, Object>>?,
    );
  }
}

extension $ModelRegistryResponseCopyWith on ModelRegistryResponse {
  /// Returns a callable class that can be used as follows: `instanceOfModelRegistryResponse.copyWith(...)` or like so:`instanceOfModelRegistryResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ModelRegistryResponseCWProxy get copyWith =>
      _$ModelRegistryResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ModelRegistryResponse _$ModelRegistryResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('ModelRegistryResponse', json, ($checkedConvert) {
  final val = ModelRegistryResponse(
    models: $checkedConvert(
      'models',
      (v) => (v as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(
          k,
          (e as Map<String, dynamic>).map((k, e) => MapEntry(k, e as Object)),
        ),
      ),
    ),
  );
  return val;
});

Map<String, dynamic> _$ModelRegistryResponseToJson(
  ModelRegistryResponse instance,
) => <String, dynamic>{'models': ?instance.models};
