// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'model_registry_update.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ModelRegistryUpdateCWProxy {
  ModelRegistryUpdate registry(Map<String, Map<String, String>> registry);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ModelRegistryUpdate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ModelRegistryUpdate(...).copyWith(id: 12, name: "My name")
  /// ````
  ModelRegistryUpdate call({Map<String, Map<String, String>> registry});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfModelRegistryUpdate.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfModelRegistryUpdate.copyWith.fieldName(...)`
class _$ModelRegistryUpdateCWProxyImpl implements _$ModelRegistryUpdateCWProxy {
  const _$ModelRegistryUpdateCWProxyImpl(this._value);

  final ModelRegistryUpdate _value;

  @override
  ModelRegistryUpdate registry(Map<String, Map<String, String>> registry) =>
      this(registry: registry);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ModelRegistryUpdate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ModelRegistryUpdate(...).copyWith(id: 12, name: "My name")
  /// ````
  ModelRegistryUpdate call({Object? registry = const $CopyWithPlaceholder()}) {
    return ModelRegistryUpdate(
      registry: registry == const $CopyWithPlaceholder()
          ? _value.registry
          // ignore: cast_nullable_to_non_nullable
          : registry as Map<String, Map<String, String>>,
    );
  }
}

extension $ModelRegistryUpdateCopyWith on ModelRegistryUpdate {
  /// Returns a callable class that can be used as follows: `instanceOfModelRegistryUpdate.copyWith(...)` or like so:`instanceOfModelRegistryUpdate.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ModelRegistryUpdateCWProxy get copyWith =>
      _$ModelRegistryUpdateCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ModelRegistryUpdate _$ModelRegistryUpdateFromJson(Map<String, dynamic> json) =>
    $checkedCreate('ModelRegistryUpdate', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['registry']);
      final val = ModelRegistryUpdate(
        registry: $checkedConvert(
          'registry',
          (v) => (v as Map<String, dynamic>).map(
            (k, e) => MapEntry(k, Map<String, String>.from(e as Map)),
          ),
        ),
      );
      return val;
    });

Map<String, dynamic> _$ModelRegistryUpdateToJson(
  ModelRegistryUpdate instance,
) => <String, dynamic>{'registry': instance.registry};
