// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_QuestionnaireItem _$QuestionnaireItemFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_QuestionnaireItem', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['question_id', 'question', 'type']);
      final val = _QuestionnaireItem(
        questionId: $checkedConvert('question_id', (v) => v as String),
        question: $checkedConvert(
          'question',
          (v) => I18nText.fromJson(v as Map<String, dynamic>),
        ),
        type: $checkedConvert('type', (v) => v as String),
      );
      return val;
    }, fieldKeyMap: const {'questionId': 'question_id'});

Map<String, dynamic> _$QuestionnaireItemToJson(_QuestionnaireItem instance) =>
    <String, dynamic>{
      'question_id': instance.questionId,
      'question': instance.question.toJson(),
      'type': instance.type,
    };

_ExpectedInput _$ExpectedInputFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ExpectedInput',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'input_key',
            'label',
            'required',
            'is_chat_history',
            'input_modes',
            'description',
            'scan_for_performative_patterns',
            'ai_description',
            'questionnaire_definition',
          ],
        );
        final val = _ExpectedInput(
          inputKey: $checkedConvert('input_key', (v) => v as String),
          label: $checkedConvert(
            'label',
            (v) => I18nText.fromJson(v as Map<String, dynamic>),
          ),
          required: $checkedConvert('required', (v) => v as bool),
          isChatHistory: $checkedConvert(
            'is_chat_history',
            (v) => v as bool? ?? false,
          ),
          inputModes: $checkedConvert(
            'input_modes',
            (v) =>
                (v as List<dynamic>?)?.map((e) => e as String).toList() ??
                const [],
          ),
          description: $checkedConvert(
            'description',
            (v) => I18nText.fromJson(v as Map<String, dynamic>),
          ),
          scanForPerformativePatterns: $checkedConvert(
            'scan_for_performative_patterns',
            (v) => v as bool? ?? false,
          ),
          aiDescription: $checkedConvert('ai_description', (v) => v as String?),
          questionnaireDefinition: $checkedConvert(
            'questionnaire_definition',
            (v) =>
                (v as List<dynamic>?)
                    ?.map(
                      (e) =>
                          QuestionnaireItem.fromJson(e as Map<String, dynamic>),
                    )
                    .toList() ??
                const [],
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'inputKey': 'input_key',
        'isChatHistory': 'is_chat_history',
        'inputModes': 'input_modes',
        'scanForPerformativePatterns': 'scan_for_performative_patterns',
        'aiDescription': 'ai_description',
        'questionnaireDefinition': 'questionnaire_definition',
      },
    );

Map<String, dynamic> _$ExpectedInputToJson(_ExpectedInput instance) =>
    <String, dynamic>{
      'input_key': instance.inputKey,
      'label': instance.label.toJson(),
      'required': instance.required,
      'is_chat_history': instance.isChatHistory,
      'input_modes': instance.inputModes,
      'description': instance.description.toJson(),
      'scan_for_performative_patterns': instance.scanForPerformativePatterns,
      'ai_description': instance.aiDescription,
      'questionnaire_definition': instance.questionnaireDefinition
          .map((e) => e.toJson())
          .toList(),
    };

_StepRule _$StepRuleFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_StepRule',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'task_blueprint',
        'depends_on',
        'input_mappings',
        'engine_override',
        'ui_pos_x',
        'ui_pos_y',
      ],
    );
    final val = _StepRule(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      taskBlueprint: $checkedConvert(
        'task_blueprint',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      dependsOn: $checkedConvert(
        'depends_on',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      inputMappings: $checkedConvert(
        'input_mappings',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as String),
            ) ??
            const {},
      ),
      engineOverride: $checkedConvert(
        'engine_override',
        (v) => $enumDecodeNullable(_$EngineOverrideStrategyEnumMap, v),
      ),
      uiPosX: $checkedConvert(
        'ui_pos_x',
        (v) => (v as num?)?.toDouble() ?? 0.0,
      ),
      uiPosY: $checkedConvert(
        'ui_pos_y',
        (v) => (v as num?)?.toDouble() ?? 0.0,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'taskBlueprint': 'task_blueprint',
    'dependsOn': 'depends_on',
    'inputMappings': 'input_mappings',
    'engineOverride': 'engine_override',
    'uiPosX': 'ui_pos_x',
    'uiPosY': 'ui_pos_y',
  },
);

Map<String, dynamic> _$StepRuleToJson(_StepRule instance) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'task_blueprint': const StrictOpaqueIdConverter().toJson(
    instance.taskBlueprint,
  ),
  'depends_on': instance.dependsOn,
  'input_mappings': instance.inputMappings,
  'engine_override': _$EngineOverrideStrategyEnumMap[instance.engineOverride],
  'ui_pos_x': instance.uiPosX,
  'ui_pos_y': instance.uiPosY,
};

const _$EngineOverrideStrategyEnumMap = {
  EngineOverrideStrategy.preHydratedSynthesis: 'PRE_HYDRATED_SYNTHESIS',
  EngineOverrideStrategy.dynamicToolAgent: 'DYNAMIC_TOOL_AGENT',
};

NodeStrategyLlm _$NodeStrategyLlmFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'NodeStrategyLlm',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'name',
        'description',
        'hook',
        'role_block_id',
        'extraction_protocol_block_id',
        'execution_persona_block_id',
        'criteria_block_ids',
        'pre_hooks',
        'post_hooks',
        'safety',
        'allowed_mcp_tools',
        'expected_inputs',
        'output_schema',
        'model_strategy',
        'organization_id',
        'type',
      ],
    );
    final val = NodeStrategyLlm(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      name: $checkedConvert(
        'name',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      hook: $checkedConvert('hook', (v) => v as String?),
      roleBlockId: $checkedConvert(
        'role_block_id',
        (v) => _$JsonConverterFromJson<String, String>(
          v,
          const StrictOpaqueIdConverter().fromJson,
        ),
      ),
      extractionProtocolBlockId: $checkedConvert(
        'extraction_protocol_block_id',
        (v) => _$JsonConverterFromJson<String, String>(
          v,
          const StrictOpaqueIdConverter().fromJson,
        ),
      ),
      executionPersonaBlockId: $checkedConvert(
        'execution_persona_block_id',
        (v) => _$JsonConverterFromJson<String, String>(
          v,
          const StrictOpaqueIdConverter().fromJson,
        ),
      ),
      criteriaBlockIds: $checkedConvert(
        'criteria_block_ids',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      preHooks: $checkedConvert(
        'pre_hooks',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      postHooks: $checkedConvert(
        'post_hooks',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      safety: $checkedConvert('safety', (v) => v as String? ?? 'safe'),
      allowedMcpTools: $checkedConvert(
        'allowed_mcp_tools',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      expectedInputs: $checkedConvert(
        'expected_inputs',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      outputSchema: $checkedConvert(
        'output_schema',
        (v) => v as Map<String, dynamic>?,
      ),
      modelStrategy: $checkedConvert('model_strategy', (v) => v as String?),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      $type: $checkedConvert('type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'roleBlockId': 'role_block_id',
    'extractionProtocolBlockId': 'extraction_protocol_block_id',
    'executionPersonaBlockId': 'execution_persona_block_id',
    'criteriaBlockIds': 'criteria_block_ids',
    'preHooks': 'pre_hooks',
    'postHooks': 'post_hooks',
    'allowedMcpTools': 'allowed_mcp_tools',
    'expectedInputs': 'expected_inputs',
    'outputSchema': 'output_schema',
    'modelStrategy': 'model_strategy',
    'organizationId': 'organization_id',
    r'$type': 'type',
  },
);

Map<String, dynamic> _$NodeStrategyLlmToJson(NodeStrategyLlm instance) =>
    <String, dynamic>{
      'id': const StrictOpaqueIdConverter().toJson(instance.id),
      'slug': instance.slug,
      'name': instance.name.toJson(),
      'description': instance.description?.toJson(),
      'hook': instance.hook,
      'role_block_id': _$JsonConverterToJson<String, String>(
        instance.roleBlockId,
        const StrictOpaqueIdConverter().toJson,
      ),
      'extraction_protocol_block_id': _$JsonConverterToJson<String, String>(
        instance.extractionProtocolBlockId,
        const StrictOpaqueIdConverter().toJson,
      ),
      'execution_persona_block_id': _$JsonConverterToJson<String, String>(
        instance.executionPersonaBlockId,
        const StrictOpaqueIdConverter().toJson,
      ),
      'criteria_block_ids': instance.criteriaBlockIds,
      'pre_hooks': instance.preHooks,
      'post_hooks': instance.postHooks,
      'safety': instance.safety,
      'allowed_mcp_tools': instance.allowedMcpTools,
      'expected_inputs': instance.expectedInputs,
      'output_schema': instance.outputSchema,
      'model_strategy': instance.modelStrategy,
      'organization_id': instance.organizationId,
      'type': instance.$type,
    };

Value? _$JsonConverterFromJson<Json, Value>(
  Object? json,
  Value? Function(Json json) fromJson,
) => json == null ? null : fromJson(json as Json);

Json? _$JsonConverterToJson<Json, Value>(
  Value? value,
  Json? Function(Value value) toJson,
) => value == null ? null : toJson(value);

NodeStrategyLogic _$NodeStrategyLogicFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'NodeStrategyLogic',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'name',
        'description',
        'hook',
        'role_block_id',
        'extraction_protocol_block_id',
        'execution_persona_block_id',
        'criteria_block_ids',
        'pre_hooks',
        'post_hooks',
        'safety',
        'allowed_mcp_tools',
        'expected_inputs',
        'output_schema',
        'model_strategy',
        'organization_id',
        'type',
      ],
    );
    final val = NodeStrategyLogic(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      name: $checkedConvert(
        'name',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      hook: $checkedConvert('hook', (v) => v as String),
      roleBlockId: $checkedConvert(
        'role_block_id',
        (v) => _$JsonConverterFromJson<String, String>(
          v,
          const StrictOpaqueIdConverter().fromJson,
        ),
      ),
      extractionProtocolBlockId: $checkedConvert(
        'extraction_protocol_block_id',
        (v) => _$JsonConverterFromJson<String, String>(
          v,
          const StrictOpaqueIdConverter().fromJson,
        ),
      ),
      executionPersonaBlockId: $checkedConvert(
        'execution_persona_block_id',
        (v) => _$JsonConverterFromJson<String, String>(
          v,
          const StrictOpaqueIdConverter().fromJson,
        ),
      ),
      criteriaBlockIds: $checkedConvert(
        'criteria_block_ids',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      preHooks: $checkedConvert(
        'pre_hooks',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      postHooks: $checkedConvert(
        'post_hooks',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      safety: $checkedConvert('safety', (v) => v as String? ?? 'safe'),
      allowedMcpTools: $checkedConvert(
        'allowed_mcp_tools',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      expectedInputs: $checkedConvert(
        'expected_inputs',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      outputSchema: $checkedConvert(
        'output_schema',
        (v) => v as Map<String, dynamic>?,
      ),
      modelStrategy: $checkedConvert('model_strategy', (v) => v as String?),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      $type: $checkedConvert('type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'roleBlockId': 'role_block_id',
    'extractionProtocolBlockId': 'extraction_protocol_block_id',
    'executionPersonaBlockId': 'execution_persona_block_id',
    'criteriaBlockIds': 'criteria_block_ids',
    'preHooks': 'pre_hooks',
    'postHooks': 'post_hooks',
    'allowedMcpTools': 'allowed_mcp_tools',
    'expectedInputs': 'expected_inputs',
    'outputSchema': 'output_schema',
    'modelStrategy': 'model_strategy',
    'organizationId': 'organization_id',
    r'$type': 'type',
  },
);

Map<String, dynamic> _$NodeStrategyLogicToJson(NodeStrategyLogic instance) =>
    <String, dynamic>{
      'id': const StrictOpaqueIdConverter().toJson(instance.id),
      'slug': instance.slug,
      'name': instance.name.toJson(),
      'description': instance.description?.toJson(),
      'hook': instance.hook,
      'role_block_id': _$JsonConverterToJson<String, String>(
        instance.roleBlockId,
        const StrictOpaqueIdConverter().toJson,
      ),
      'extraction_protocol_block_id': _$JsonConverterToJson<String, String>(
        instance.extractionProtocolBlockId,
        const StrictOpaqueIdConverter().toJson,
      ),
      'execution_persona_block_id': _$JsonConverterToJson<String, String>(
        instance.executionPersonaBlockId,
        const StrictOpaqueIdConverter().toJson,
      ),
      'criteria_block_ids': instance.criteriaBlockIds,
      'pre_hooks': instance.preHooks,
      'post_hooks': instance.postHooks,
      'safety': instance.safety,
      'allowed_mcp_tools': instance.allowedMcpTools,
      'expected_inputs': instance.expectedInputs,
      'output_schema': instance.outputSchema,
      'model_strategy': instance.modelStrategy,
      'organization_id': instance.organizationId,
      'type': instance.$type,
    };

_Workflow _$WorkflowFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_Workflow',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'name',
        'description',
        'status',
        'version',
        'is_public',
        'organization_id',
        'ui_schema',
        'output_profiles',
        'default_profile_id',
        'default_strictness_level',
        'default_scoring_strategy',
        'enable_contextual_overrides',
        'enable_semantic_smoothing',
        'enable_eager_anonymization',
        'system_audit_trail',
        'expected_inputs',
        'steps',
      ],
    );
    final val = _Workflow(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      name: $checkedConvert(
        'name',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      status: $checkedConvert('status', (v) => v as String? ?? "draft"),
      version: $checkedConvert('version', (v) => (v as num?)?.toInt() ?? 1),
      isPublic: $checkedConvert('is_public', (v) => v as bool? ?? false),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      uiSchema: $checkedConvert(
        'ui_schema',
        (v) => v as Map<String, dynamic>? ?? const {},
      ),
      outputProfiles: $checkedConvert(
        'output_profiles',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(
                k,
                EmbeddedOutputProfile.fromJson(e as Map<String, dynamic>),
              ),
            ) ??
            const {},
      ),
      defaultProfileId: $checkedConvert(
        'default_profile_id',
        (v) => v as String? ?? "default",
      ),
      defaultStrictnessLevel: $checkedConvert(
        'default_strictness_level',
        (v) => (v as num?)?.toInt() ?? 50,
      ),
      defaultScoringStrategy: $checkedConvert(
        'default_scoring_strategy',
        (v) =>
            $enumDecodeNullable(_$ScoringStrategyEnumMap, v) ??
            ScoringStrategy.average,
      ),
      enableContextualOverrides: $checkedConvert(
        'enable_contextual_overrides',
        (v) => v as bool? ?? false,
      ),
      enableSemanticSmoothing: $checkedConvert(
        'enable_semantic_smoothing',
        (v) => v as bool? ?? false,
      ),
      enableEagerAnonymization: $checkedConvert(
        'enable_eager_anonymization',
        (v) => v as bool? ?? false,
      ),
      systemAuditTrail: $checkedConvert(
        'system_audit_trail',
        (v) => v as bool? ?? false,
      ),
      expectedInputs: $checkedConvert(
        'expected_inputs',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => ExpectedInput.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
      steps: $checkedConvert(
        'steps',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => StepRule.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'isPublic': 'is_public',
    'organizationId': 'organization_id',
    'uiSchema': 'ui_schema',
    'outputProfiles': 'output_profiles',
    'defaultProfileId': 'default_profile_id',
    'defaultStrictnessLevel': 'default_strictness_level',
    'defaultScoringStrategy': 'default_scoring_strategy',
    'enableContextualOverrides': 'enable_contextual_overrides',
    'enableSemanticSmoothing': 'enable_semantic_smoothing',
    'enableEagerAnonymization': 'enable_eager_anonymization',
    'systemAuditTrail': 'system_audit_trail',
    'expectedInputs': 'expected_inputs',
  },
);

Map<String, dynamic> _$WorkflowToJson(_Workflow instance) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'slug': instance.slug,
  'name': instance.name.toJson(),
  'description': instance.description.toJson(),
  'status': instance.status,
  'version': instance.version,
  'is_public': instance.isPublic,
  'organization_id': instance.organizationId,
  'ui_schema': instance.uiSchema,
  'output_profiles': instance.outputProfiles.map(
    (k, e) => MapEntry(k, e.toJson()),
  ),
  'default_profile_id': instance.defaultProfileId,
  'default_strictness_level': instance.defaultStrictnessLevel,
  'default_scoring_strategy':
      _$ScoringStrategyEnumMap[instance.defaultScoringStrategy]!,
  'enable_contextual_overrides': instance.enableContextualOverrides,
  'enable_semantic_smoothing': instance.enableSemanticSmoothing,
  'enable_eager_anonymization': instance.enableEagerAnonymization,
  'system_audit_trail': instance.systemAuditTrail,
  'expected_inputs': instance.expectedInputs.map((e) => e.toJson()).toList(),
  'steps': instance.steps.map((e) => e.toJson()).toList(),
};

const _$ScoringStrategyEnumMap = {
  ScoringStrategy.waterfall: 'WATERFALL',
  ScoringStrategy.average: 'AVERAGE',
  ScoringStrategy.weightedAverage: 'WEIGHTED_AVERAGE',
  ScoringStrategy.pureMath: 'PURE_MATH',
};
