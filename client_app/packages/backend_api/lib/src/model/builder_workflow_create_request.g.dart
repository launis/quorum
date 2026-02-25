// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'builder_workflow_create_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$BuilderWorkflowCreateRequestCWProxy {
  BuilderWorkflowCreateRequest name(String name);

  BuilderWorkflowCreateRequest description(String? description);

  BuilderWorkflowCreateRequest steps(List<String>? steps);

  BuilderWorkflowCreateRequest defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  );

  BuilderWorkflowCreateRequest uiSchema(Map<String, Object>? uiSchema);

  BuilderWorkflowCreateRequest isPublic(bool? isPublic);

  BuilderWorkflowCreateRequest status(String? status);

  BuilderWorkflowCreateRequest version(int? version);

  BuilderWorkflowCreateRequest scoringLogic(
    List<Map<String, Object>>? scoringLogic,
  );

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BuilderWorkflowCreateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BuilderWorkflowCreateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  BuilderWorkflowCreateRequest call({
    String name,
    String? description,
    List<String>? steps,
    Map<String, String>? defaultModelMapping,
    Map<String, Object>? uiSchema,
    bool? isPublic,
    String? status,
    int? version,
    List<Map<String, Object>>? scoringLogic,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfBuilderWorkflowCreateRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfBuilderWorkflowCreateRequest.copyWith.fieldName(...)`
class _$BuilderWorkflowCreateRequestCWProxyImpl
    implements _$BuilderWorkflowCreateRequestCWProxy {
  const _$BuilderWorkflowCreateRequestCWProxyImpl(this._value);

  final BuilderWorkflowCreateRequest _value;

  @override
  BuilderWorkflowCreateRequest name(String name) => this(name: name);

  @override
  BuilderWorkflowCreateRequest description(String? description) =>
      this(description: description);

  @override
  BuilderWorkflowCreateRequest steps(List<String>? steps) => this(steps: steps);

  @override
  BuilderWorkflowCreateRequest defaultModelMapping(
    Map<String, String>? defaultModelMapping,
  ) => this(defaultModelMapping: defaultModelMapping);

  @override
  BuilderWorkflowCreateRequest uiSchema(Map<String, Object>? uiSchema) =>
      this(uiSchema: uiSchema);

  @override
  BuilderWorkflowCreateRequest isPublic(bool? isPublic) =>
      this(isPublic: isPublic);

  @override
  BuilderWorkflowCreateRequest status(String? status) => this(status: status);

  @override
  BuilderWorkflowCreateRequest version(int? version) => this(version: version);

  @override
  BuilderWorkflowCreateRequest scoringLogic(
    List<Map<String, Object>>? scoringLogic,
  ) => this(scoringLogic: scoringLogic);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BuilderWorkflowCreateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BuilderWorkflowCreateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  BuilderWorkflowCreateRequest call({
    Object? name = const $CopyWithPlaceholder(),
    Object? description = const $CopyWithPlaceholder(),
    Object? steps = const $CopyWithPlaceholder(),
    Object? defaultModelMapping = const $CopyWithPlaceholder(),
    Object? uiSchema = const $CopyWithPlaceholder(),
    Object? isPublic = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
    Object? version = const $CopyWithPlaceholder(),
    Object? scoringLogic = const $CopyWithPlaceholder(),
  }) {
    return BuilderWorkflowCreateRequest(
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
          : steps as List<String>?,
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
    );
  }
}

extension $BuilderWorkflowCreateRequestCopyWith
    on BuilderWorkflowCreateRequest {
  /// Returns a callable class that can be used as follows: `instanceOfBuilderWorkflowCreateRequest.copyWith(...)` or like so:`instanceOfBuilderWorkflowCreateRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$BuilderWorkflowCreateRequestCWProxy get copyWith =>
      _$BuilderWorkflowCreateRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BuilderWorkflowCreateRequest _$BuilderWorkflowCreateRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'BuilderWorkflowCreateRequest',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['name']);
    final val = BuilderWorkflowCreateRequest(
      name: $checkedConvert('name', (v) => v as String),
      description: $checkedConvert('description', (v) => v as String? ?? ''),
      steps: $checkedConvert(
        'steps',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList() ?? [],
      ),
      defaultModelMapping: $checkedConvert(
        'default_model_mapping',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as String),
        ),
      ),
      uiSchema: $checkedConvert(
        'ui_schema',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
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
    );
    return val;
  },
  fieldKeyMap: const {
    'defaultModelMapping': 'default_model_mapping',
    'uiSchema': 'ui_schema',
    'isPublic': 'is_public',
    'scoringLogic': 'scoring_logic',
  },
);

Map<String, dynamic> _$BuilderWorkflowCreateRequestToJson(
  BuilderWorkflowCreateRequest instance,
) => <String, dynamic>{
  'name': instance.name,
  'description': ?instance.description,
  'steps': ?instance.steps,
  'default_model_mapping': ?instance.defaultModelMapping,
  'ui_schema': ?instance.uiSchema,
  'is_public': ?instance.isPublic,
  'status': ?instance.status,
  'version': ?instance.version,
  'scoring_logic': ?instance.scoringLogic,
};
