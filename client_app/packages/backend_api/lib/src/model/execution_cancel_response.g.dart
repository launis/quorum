// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_cancel_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ExecutionCancelResponseCWProxy {
  ExecutionCancelResponse id(String id);

  ExecutionCancelResponse status(String status);

  ExecutionCancelResponse message(String message);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ExecutionCancelResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ExecutionCancelResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ExecutionCancelResponse call({String id, String status, String message});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfExecutionCancelResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfExecutionCancelResponse.copyWith.fieldName(...)`
class _$ExecutionCancelResponseCWProxyImpl
    implements _$ExecutionCancelResponseCWProxy {
  const _$ExecutionCancelResponseCWProxyImpl(this._value);

  final ExecutionCancelResponse _value;

  @override
  ExecutionCancelResponse id(String id) => this(id: id);

  @override
  ExecutionCancelResponse status(String status) => this(status: status);

  @override
  ExecutionCancelResponse message(String message) => this(message: message);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ExecutionCancelResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ExecutionCancelResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ExecutionCancelResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
    Object? message = const $CopyWithPlaceholder(),
  }) {
    return ExecutionCancelResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      message: message == const $CopyWithPlaceholder()
          ? _value.message
          // ignore: cast_nullable_to_non_nullable
          : message as String,
    );
  }
}

extension $ExecutionCancelResponseCopyWith on ExecutionCancelResponse {
  /// Returns a callable class that can be used as follows: `instanceOfExecutionCancelResponse.copyWith(...)` or like so:`instanceOfExecutionCancelResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ExecutionCancelResponseCWProxy get copyWith =>
      _$ExecutionCancelResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ExecutionCancelResponse _$ExecutionCancelResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('ExecutionCancelResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['id', 'status', 'message']);
  final val = ExecutionCancelResponse(
    id: $checkedConvert('id', (v) => v as String),
    status: $checkedConvert('status', (v) => v as String),
    message: $checkedConvert('message', (v) => v as String),
  );
  return val;
});

Map<String, dynamic> _$ExecutionCancelResponseToJson(
  ExecutionCancelResponse instance,
) => <String, dynamic>{
  'id': instance.id,
  'status': instance.status,
  'message': instance.message,
};
