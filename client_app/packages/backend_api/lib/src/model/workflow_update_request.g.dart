// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_update_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$WorkflowUpdateRequestCWProxy {
  WorkflowUpdateRequest name(String? name);

  WorkflowUpdateRequest description(String? description);

  WorkflowUpdateRequest steps(List<String>? steps);

  WorkflowUpdateRequest uiSchema(Map<String, Object>? uiSchema);

  WorkflowUpdateRequest defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  );

  WorkflowUpdateRequest isPublic(bool? isPublic);

  WorkflowUpdateRequest status(String? status);

  WorkflowUpdateRequest version(int? version);

  WorkflowUpdateRequest scoringLogic(List<Map<String, Object>>? scoringLogic);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowUpdateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowUpdateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowUpdateRequest call({
    String? name,
    String? description,
    List<String>? steps,
    Map<String, Object>? uiSchema,
    Map<String, String>? defaultModelMapping,
    bool? isPublic,
    String? status,
    int? version,
    List<Map<String, Object>>? scoringLogic,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfWorkflowUpdateRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfWorkflowUpdateRequest.copyWith.fieldName(...)`
class _$WorkflowUpdateRequestCWProxyImpl
    implements _$WorkflowUpdateRequestCWProxy {
  const _$WorkflowUpdateRequestCWProxyImpl(this._value);

  final WorkflowUpdateRequest _value;

  @override
  WorkflowUpdateRequest name(String? name) => this(name: name);

  @override
  WorkflowUpdateRequest description(String? description) =>
      this(description: description);

  @override
  WorkflowUpdateRequest steps(List<String>? steps) => this(steps: steps);

  @override
  WorkflowUpdateRequest uiSchema(Map<String, Object>? uiSchema) =>
      this(uiSchema: uiSchema);

  @override
  WorkflowUpdateRequest defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  ) => this(defaultModelMapping: defaultModelMapping);

  @override
  WorkflowUpdateRequest isPublic(bool? isPublic) => this(isPublic: isPublic);

  @override
  WorkflowUpdateRequest status(String? status) => this(status: status);

  @override
  WorkflowUpdateRequest version(int? version) => this(version: version);

  @override
  WorkflowUpdateRequest scoringLogic(List<Map<String, Object>>? scoringLogic) =>
      this(scoringLogic: scoringLogic);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowUpdateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowUpdateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowUpdateRequest call({
    Object? name = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? steps = const $CopyWithPlaceholder(),
    Object? uiSchema = const $CopyWithPlaceholder(),
    Object? defaultModelMapping = const $CopyWithPlaceholder(),
    Object? isPublic = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
    Object? version = const $CopyWithPlaceholder(),
    Object? scoringLogic = const $CopyWithPlaceholder(),
  }) {
    return WorkflowUpdateRequest(
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String?,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as String?,
      steps: steps == const $CopyWithPlaceholder()
          ? _value.steps
          // ignore: cast_nullable_to_non_nullable
          : steps as List<String>?,
      uiSchema: uiSchema == const $CopyWithPlaceholder()
          ? _value.uiSchema
          // ignore: cast_nullable_to_non_nullable
          : uiSchema as Map<String, Object>?,
      defaultModelMapping: defaultModelMapping == const $CopyWithPlaceholder()
          ? _value.defaultModelMapping
          // ignore: cast_nullable_to_non_nullable
          : defaultModelMapping as Map<String, String>?,
      isPublic: isPublic == const $CopyWithPlaceholder()
          ? _value.isPublic
          // ignore: cast_nullable_to_non_nullable
          : isPublic as bool?,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String?,
      version: version == const $CopyWithPlaceholder()
          ? _value.version
          // ignore: cast_nullable_to_non_nullable
          : version as int?,
      scoringLogic: scoringLogic == const $CopyWithPlaceholder()
          ? _value.scoringLogic
          // ignore: cast_nullable_to_non_nullable
          : scoringLogic as List<Map<String, Object>>?,
    );
  }
}

extension $WorkflowUpdateRequestCopyWith on WorkflowUpdateRequest {
  /// Returns a callable class that can be used as follows: `instanceOfWorkflowUpdateRequest.copyWith(...)` or like so:`instanceOfWorkflowUpdateRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$WorkflowUpdateRequestCWProxy get copyWith =>
      _$WorkflowUpdateRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WorkflowUpdateRequest _$WorkflowUpdateRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'WorkflowUpdateRequest',
  json,
  ($checkedConvert) {
    final val = WorkflowUpdateRequest(
      name: $checkedConvert('name', (v) => v as String?),
      description: $checkedConvert('description', (v) => v as String? ?? ''),
      steps: $checkedConvert(
        'steps',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
      ),
      uiSchema: $checkedConvert(
        'ui_schema',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
      defaultModelMapping: $checkedConvert(
        'default_model_mapping',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as String),
        ),
      ),
      isPublic: $checkedConvert('is_public', (v) => v as bool?),
      status: $checkedConvert('status', (v) => v as String?),
      version: $checkedConvert('version', (v) => (v as num?)?.toInt()),
      scoringLogic: $checkedConvert(
        'scoring_logic',
        (v) => (v as List<dynamic>?)
            ?.map(
              (e) => (e as Map<String, dynamic>).map(
                (k, e) => MapEntry(k, e as Object),
              ),
            )
            .toList(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'uiSchema': 'ui_schema',
    'defaultModelMapping': 'default_model_mapping',
    'isPublic': 'is_public',
    'scoringLogic': 'scoring_logic',
  },
);

Map<String, dynamic> _$WorkflowUpdateRequestToJson(
  WorkflowUpdateRequest instance,
) => <String, dynamic>{
  'name': ?instance.name,
  'description': ?instance.description,
  'steps': ?instance.steps,
  'ui_schema': ?instance.uiSchema,
  'default_model_mapping': ?instance.defaultModelMapping,
  'is_public': ?instance.isPublic,
  'status': ?instance.status,
  'version': ?instance.version,
  'scoring_logic': ?instance.scoringLogic,
};
