// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'compile_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$CompileRequestCWProxy {
  CompileRequest workflowId(String workflowId);

  CompileRequest steps(List<String> steps);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CompileRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CompileRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  CompileRequest call({String workflowId, List<String> steps});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfCompileRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfCompileRequest.copyWith.fieldName(...)`
class _$CompileRequestCWProxyImpl implements _$CompileRequestCWProxy {
  const _$CompileRequestCWProxyImpl(this._value);

  final CompileRequest _value;

  @override
  CompileRequest workflowId(String workflowId) => this(workflowId: workflowId);

  @override
  CompileRequest steps(List<String> steps) => this(steps: steps);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CompileRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CompileRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  CompileRequest call({
    Object? workflowId = const $CopyWithPlaceholder(),
    Object? steps = const $CopyWithPlaceholder(),
  }) {
    return CompileRequest(
      workflowId: workflowId == const $CopyWithPlaceholder()
          ? _value.workflowId
          // ignore: cast_nullable_to_non_nullable
          : workflowId as String,
      steps: steps == const $CopyWithPlaceholder()
          ? _value.steps
          // ignore: cast_nullable_to_non_nullable
          : steps as List<String>,
    );
  }
}

extension $CompileRequestCopyWith on CompileRequest {
  /// Returns a callable class that can be used as follows: `instanceOfCompileRequest.copyWith(...)` or like so:`instanceOfCompileRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$CompileRequestCWProxy get copyWith => _$CompileRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CompileRequest _$CompileRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate('CompileRequest', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['workflow_id', 'steps']);
      final val = CompileRequest(
        workflowId: $checkedConvert('workflow_id', (v) => v as String),
        steps: $checkedConvert(
          'steps',
          (v) => (v as List<dynamic>).map((e) => e as String).toList(),
        ),
      );
      return val;
    }, fieldKeyMap: const {'workflowId': 'workflow_id'});

Map<String, dynamic> _$CompileRequestToJson(CompileRequest instance) =>
    <String, dynamic>{
      'workflow_id': instance.workflowId,
      'steps': instance.steps,
    };
