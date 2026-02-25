// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'model_registry_update_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ModelRegistryUpdateResponseCWProxy {
  ModelRegistryUpdateResponse status(String status);

  ModelRegistryUpdateResponse registry(
    Map<String, Map<String, String>> registry,
  );

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ModelRegistryUpdateResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ModelRegistryUpdateResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ModelRegistryUpdateResponse call({
    String status,
    Map<String, Map<String, String>> registry,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfModelRegistryUpdateResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfModelRegistryUpdateResponse.copyWith.fieldName(...)`
class _$ModelRegistryUpdateResponseCWProxyImpl
    implements _$ModelRegistryUpdateResponseCWProxy {
  const _$ModelRegistryUpdateResponseCWProxyImpl(this._value);

  final ModelRegistryUpdateResponse _value;

  @override
  ModelRegistryUpdateResponse status(String status) => this(status: status);

  @override
  ModelRegistryUpdateResponse registry(
    Map<String, Map<String, String>> registry,
  ) => this(registry: registry);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ModelRegistryUpdateResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ModelRegistryUpdateResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ModelRegistryUpdateResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? registry = const $CopyWithPlaceholder(),
  }) {
    return ModelRegistryUpdateResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      registry: registry == const $CopyWithPlaceholder()
          ? _value.registry
          // ignore: cast_nullable_to_non_nullable
          : registry as Map<String, Map<String, String>>,
    );
  }
}

extension $ModelRegistryUpdateResponseCopyWith on ModelRegistryUpdateResponse {
  /// Returns a callable class that can be used as follows: `instanceOfModelRegistryUpdateResponse.copyWith(...)` or like so:`instanceOfModelRegistryUpdateResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ModelRegistryUpdateResponseCWProxy get copyWith =>
      _$ModelRegistryUpdateResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ModelRegistryUpdateResponse _$ModelRegistryUpdateResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('ModelRegistryUpdateResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['status', 'registry']);
  final val = ModelRegistryUpdateResponse(
    status: $checkedConvert('status', (v) => v as String),
    registry: $checkedConvert(
      'registry',
      (v) => (v as Map<String, dynamic>).map(
        (k, e) => MapEntry(k, Map<String, String>.from(e as Map)),
      ),
    ),
  );
  return val;
});

Map<String, dynamic> _$ModelRegistryUpdateResponseToJson(
  ModelRegistryUpdateResponse instance,
) => <String, dynamic>{
  'status': instance.status,
  'registry': instance.registry,
};
