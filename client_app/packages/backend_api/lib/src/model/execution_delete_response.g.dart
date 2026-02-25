// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_delete_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ExecutionDeleteResponseCWProxy {
  ExecutionDeleteResponse status(String status);

  ExecutionDeleteResponse id(String id);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ExecutionDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ExecutionDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ExecutionDeleteResponse call({String status, String id});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfExecutionDeleteResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfExecutionDeleteResponse.copyWith.fieldName(...)`
class _$ExecutionDeleteResponseCWProxyImpl
    implements _$ExecutionDeleteResponseCWProxy {
  const _$ExecutionDeleteResponseCWProxyImpl(this._value);

  final ExecutionDeleteResponse _value;

  @override
  ExecutionDeleteResponse status(String status) => this(status: status);

  @override
  ExecutionDeleteResponse id(String id) => this(id: id);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ExecutionDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ExecutionDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ExecutionDeleteResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? id = const $CopyWithPlaceholder(),
  }) {
    return ExecutionDeleteResponse(
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

extension $ExecutionDeleteResponseCopyWith on ExecutionDeleteResponse {
  /// Returns a callable class that can be used as follows: `instanceOfExecutionDeleteResponse.copyWith(...)` or like so:`instanceOfExecutionDeleteResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ExecutionDeleteResponseCWProxy get copyWith =>
      _$ExecutionDeleteResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ExecutionDeleteResponse _$ExecutionDeleteResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('ExecutionDeleteResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['status', 'id']);
  final val = ExecutionDeleteResponse(
    status: $checkedConvert('status', (v) => v as String),
    id: $checkedConvert('id', (v) => v as String),
  );
  return val;
});

Map<String, dynamic> _$ExecutionDeleteResponseToJson(
  ExecutionDeleteResponse instance,
) => <String, dynamic>{'status': instance.status, 'id': instance.id};
