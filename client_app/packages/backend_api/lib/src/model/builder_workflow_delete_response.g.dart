// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'builder_workflow_delete_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$BuilderWorkflowDeleteResponseCWProxy {
  BuilderWorkflowDeleteResponse status(String status);

  BuilderWorkflowDeleteResponse deletedSteps(List<String> deletedSteps);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BuilderWorkflowDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BuilderWorkflowDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  BuilderWorkflowDeleteResponse call({
    String status,
    List<String> deletedSteps,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfBuilderWorkflowDeleteResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfBuilderWorkflowDeleteResponse.copyWith.fieldName(...)`
class _$BuilderWorkflowDeleteResponseCWProxyImpl
    implements _$BuilderWorkflowDeleteResponseCWProxy {
  const _$BuilderWorkflowDeleteResponseCWProxyImpl(this._value);

  final BuilderWorkflowDeleteResponse _value;

  @override
  BuilderWorkflowDeleteResponse status(String status) => this(status: status);

  @override
  BuilderWorkflowDeleteResponse deletedSteps(List<String> deletedSteps) =>
      this(deletedSteps: deletedSteps);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BuilderWorkflowDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BuilderWorkflowDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  BuilderWorkflowDeleteResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? deletedSteps = const $CopyWithPlaceholder(),
  }) {
    return BuilderWorkflowDeleteResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      deletedSteps: deletedSteps == const $CopyWithPlaceholder()
          ? _value.deletedSteps
          // ignore: cast_nullable_to_non_nullable
          : deletedSteps as List<String>,
    );
  }
}

extension $BuilderWorkflowDeleteResponseCopyWith
    on BuilderWorkflowDeleteResponse {
  /// Returns a callable class that can be used as follows: `instanceOfBuilderWorkflowDeleteResponse.copyWith(...)` or like so:`instanceOfBuilderWorkflowDeleteResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$BuilderWorkflowDeleteResponseCWProxy get copyWith =>
      _$BuilderWorkflowDeleteResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BuilderWorkflowDeleteResponse _$BuilderWorkflowDeleteResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'BuilderWorkflowDeleteResponse',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['status', 'deleted_steps']);
    final val = BuilderWorkflowDeleteResponse(
      status: $checkedConvert('status', (v) => v as String),
      deletedSteps: $checkedConvert(
        'deleted_steps',
        (v) => (v as List<dynamic>).map((e) => e as String).toList(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {'deletedSteps': 'deleted_steps'},
);

Map<String, dynamic> _$BuilderWorkflowDeleteResponseToJson(
  BuilderWorkflowDeleteResponse instance,
) => <String, dynamic>{
  'status': instance.status,
  'deleted_steps': instance.deletedSteps,
};
