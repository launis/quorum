// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'config_workflow_delete_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ConfigWorkflowDeleteResponseCWProxy {
  ConfigWorkflowDeleteResponse status(String status);

  ConfigWorkflowDeleteResponse id(String id);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ConfigWorkflowDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ConfigWorkflowDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ConfigWorkflowDeleteResponse call({String status, String id});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfConfigWorkflowDeleteResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfConfigWorkflowDeleteResponse.copyWith.fieldName(...)`
class _$ConfigWorkflowDeleteResponseCWProxyImpl
    implements _$ConfigWorkflowDeleteResponseCWProxy {
  const _$ConfigWorkflowDeleteResponseCWProxyImpl(this._value);

  final ConfigWorkflowDeleteResponse _value;

  @override
  ConfigWorkflowDeleteResponse status(String status) => this(status: status);

  @override
  ConfigWorkflowDeleteResponse id(String id) => this(id: id);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ConfigWorkflowDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ConfigWorkflowDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ConfigWorkflowDeleteResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? id = const $CopyWithPlaceholder(),
  }) {
    return ConfigWorkflowDeleteResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
    );
  }
}

extension $ConfigWorkflowDeleteResponseCopyWith
    on ConfigWorkflowDeleteResponse {
  /// Returns a callable class that can be used as follows: `instanceOfConfigWorkflowDeleteResponse.copyWith(...)` or like so:`instanceOfConfigWorkflowDeleteResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ConfigWorkflowDeleteResponseCWProxy get copyWith =>
      _$ConfigWorkflowDeleteResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ConfigWorkflowDeleteResponse _$ConfigWorkflowDeleteResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('ConfigWorkflowDeleteResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['status', 'id']);
  final val = ConfigWorkflowDeleteResponse(
    status: $checkedConvert('status', (v) => v as String),
    id: $checkedConvert('id', (v) => v as String),
  );
  return val;
});

Map<String, dynamic> _$ConfigWorkflowDeleteResponseToJson(
  ConfigWorkflowDeleteResponse instance,
) => <String, dynamic>{'status': instance.status, 'id': instance.id};
