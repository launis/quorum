// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'copy_workflow_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$CopyWorkflowRequestCWProxy {
  CopyWorkflowRequest newName(String newName);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CopyWorkflowRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CopyWorkflowRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  CopyWorkflowRequest call({String newName});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfCopyWorkflowRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfCopyWorkflowRequest.copyWith.fieldName(...)`
class _$CopyWorkflowRequestCWProxyImpl implements _$CopyWorkflowRequestCWProxy {
  const _$CopyWorkflowRequestCWProxyImpl(this._value);

  final CopyWorkflowRequest _value;

  @override
  CopyWorkflowRequest newName(String newName) => this(newName: newName);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CopyWorkflowRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CopyWorkflowRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  CopyWorkflowRequest call({Object? newName = const $CopyWithPlaceholder()}) {
    return CopyWorkflowRequest(
      newName: newName == const $CopyWithPlaceholder()
          ? _value.newName
          // ignore: cast_nullable_to_non_nullable
          : newName as String,
    );
  }
}

extension $CopyWorkflowRequestCopyWith on CopyWorkflowRequest {
  /// Returns a callable class that can be used as follows: `instanceOfCopyWorkflowRequest.copyWith(...)` or like so:`instanceOfCopyWorkflowRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$CopyWorkflowRequestCWProxy get copyWith =>
      _$CopyWorkflowRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CopyWorkflowRequest _$CopyWorkflowRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate('CopyWorkflowRequest', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['new_name']);
      final val = CopyWorkflowRequest(
        newName: $checkedConvert('new_name', (v) => v as String),
      );
      return val;
    }, fieldKeyMap: const {'newName': 'new_name'});

Map<String, dynamic> _$CopyWorkflowRequestToJson(
  CopyWorkflowRequest instance,
) => <String, dynamic>{'new_name': instance.newName};
