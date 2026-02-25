// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$WorkflowResponseCWProxy {
  WorkflowResponse id(String id);

  WorkflowResponse name(String name);

  WorkflowResponse description(String? description);

  WorkflowResponse steps(List<WorkflowStep> steps);

  WorkflowResponse defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  );

  WorkflowResponse uiSchema(Map<String, Object>? uiSchema);

  WorkflowResponse isPublic(bool? isPublic);

  WorkflowResponse status(String? status);

  WorkflowResponse version(int? version);

  WorkflowResponse scoringLogic(List<Map<String, Object>>? scoringLogic);

  WorkflowResponse createdAt(dynamic createdAt);

  WorkflowResponse updatedAt(dynamic updatedAt);

  WorkflowResponse organizationId(String organizationId);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowResponse call({
    String id,
    String name,
    String? description,
    List<WorkflowStep> steps,
    Map<String, String>? defaultModelMapping,
    Map<String, Object>? uiSchema,
    bool? isPublic,
    String? status,
    int? version,
    List<Map<String, Object>>? scoringLogic,
    dynamic createdAt,
    dynamic updatedAt,
    String organizationId,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfWorkflowResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfWorkflowResponse.copyWith.fieldName(...)`
class _$WorkflowResponseCWProxyImpl implements _$WorkflowResponseCWProxy {
  const _$WorkflowResponseCWProxyImpl(this._value);

  final WorkflowResponse _value;

  @override
  WorkflowResponse id(String id) => this(id: id);

  @override
  WorkflowResponse name(String name) => this(name: name);

  @override
  WorkflowResponse description(String? description) =>
      this(description: description);

  @override
  WorkflowResponse steps(List<WorkflowStep> steps) => this(steps: steps);

  @override
  WorkflowResponse defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  ) => this(defaultModelMapping: defaultModelMapping);

  @override
  WorkflowResponse uiSchema(Map<String, Object>? uiSchema) =>
      this(uiSchema: uiSchema);

  @override
  WorkflowResponse isPublic(bool? isPublic) => this(isPublic: isPublic);

  @override
  WorkflowResponse status(String? status) => this(status: status);

  @override
  WorkflowResponse version(int? version) => this(version: version);

  @override
  WorkflowResponse scoringLogic(List<Map<String, Object>>? scoringLogic) =>
      this(scoringLogic: scoringLogic);

  @override
  WorkflowResponse createdAt(dynamic createdAt) => this(createdAt: createdAt);

  @override
  WorkflowResponse updatedAt(dynamic updatedAt) => this(updatedAt: updatedAt);

  @override
  WorkflowResponse organizationId(String organizationId) =>
      this(organizationId: organizationId);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WorkflowResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WorkflowResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  WorkflowResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? steps = const $CopyWithPlaceholder(),
    Object? defaultModelMapping = const $CopyWithPlaceholder(),
    Object? uiSchema = const $CopyWithPlaceholder(),
    Object? isPublic = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
    Object? version = const $CopyWithPlaceholder(),
    Object? scoringLogic = const $CopyWithPlaceholder(),
    Object? createdAt = const $CopyWithPlaceholder(),
    Object? updatedAt = const $CopyWithPlaceholder(),
    Object? organizationId = const $CopyWithPlaceholder(),
  }) {
    return WorkflowResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      description: description == const $CopyWithPlaceholder()
          ? _value.description
          // ignore: cast_nullable_to_non_nullable
          : description as String?,
      steps: steps == const $CopyWithPlaceholder()
          ? _value.steps
          // ignore: cast_nullable_to_non_nullable
          : steps as List<WorkflowStep>,
      defaultModelMapping: defaultModelMapping == const $CopyWithPlaceholder()
          ? _value.defaultModelMapping
          // ignore: cast_nullable_to_non_nullable
          : defaultModelMapping as Map<String, String>?,
      uiSchema: uiSchema == const $CopyWithPlaceholder()
          ? _value.uiSchema
          // ignore: cast_nullable_to_non_nullable
          : uiSchema as Map<String, Object>?,
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
      createdAt: createdAt == const $CopyWithPlaceholder()
          ? _value.createdAt
          // ignore: cast_nullable_to_non_nullable
          : createdAt as dynamic,
      updatedAt: updatedAt == const $CopyWithPlaceholder()
          ? _value.updatedAt
          // ignore: cast_nullable_to_non_nullable
          : updatedAt as dynamic,
      organizationId: organizationId == const $CopyWithPlaceholder()
          ? _value.organizationId
          // ignore: cast_nullable_to_non_nullable
          : organizationId as String,
    );
  }
}

extension $WorkflowResponseCopyWith on WorkflowResponse {
  /// Returns a callable class that can be used as follows: `instanceOfWorkflowResponse.copyWith(...)` or like so:`instanceOfWorkflowResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$WorkflowResponseCWProxy get copyWith => _$WorkflowResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WorkflowResponse _$WorkflowResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'WorkflowResponse',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const ['id', 'name', 'steps', 'organization_id'],
    );
    final val = WorkflowResponse(
      id: $checkedConvert('id', (v) => v as String),
      name: $checkedConvert('name', (v) => v as String),
      description: $checkedConvert('description', (v) => v as String? ?? ''),
      steps: $checkedConvert(
        'steps',
        (v) => (v as List<dynamic>)
            .map((e) => WorkflowStep.fromJson(e as Map<String, dynamic>))
            .toList(),
      ),
      defaultModelMapping: $checkedConvert(
        'default_model_mapping',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as String),
            ) ??
            {},
      ),
      uiSchema: $checkedConvert(
        'ui_schema',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ) ??
            {},
      ),
      isPublic: $checkedConvert('is_public', (v) => v as bool? ?? false),
      status: $checkedConvert('status', (v) => v as String? ?? 'draft'),
      version: $checkedConvert('version', (v) => (v as num?)?.toInt() ?? 1),
      scoringLogic: $checkedConvert(
        'scoring_logic',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) => (e as Map<String, dynamic>).map(
                    (k, e) => MapEntry(k, e as Object),
                  ),
                )
                .toList() ??
            [],
      ),
      createdAt: $checkedConvert('created_at', (v) => v),
      updatedAt: $checkedConvert('updated_at', (v) => v),
      organizationId: $checkedConvert('organization_id', (v) => v as String),
    );
    return val;
  },
  fieldKeyMap: const {
    'defaultModelMapping': 'default_model_mapping',
    'uiSchema': 'ui_schema',
    'isPublic': 'is_public',
    'scoringLogic': 'scoring_logic',
    'createdAt': 'created_at',
    'updatedAt': 'updated_at',
    'organizationId': 'organization_id',
  },
);

Map<String, dynamic> _$WorkflowResponseToJson(WorkflowResponse instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': ?instance.description,
      'steps': instance.steps.map((e) => e.toJson()).toList(),
      'default_model_mapping': ?instance.defaultModelMapping,
      'ui_schema': ?instance.uiSchema,
      'is_public': ?instance.isPublic,
      'status': ?instance.status,
      'version': ?instance.version,
      'scoring_logic': ?instance.scoringLogic,
      'created_at': ?instance.createdAt,
      'updated_at': ?instance.updatedAt,
      'organization_id': instance.organizationId,
    };
