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
        'allowed_mcp_tools',
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
      allowedMcpTools: $checkedConvert(
        'allowed_mcp_tools',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
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
    'allowedMcpTools': 'allowed_mcp_tools',
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
  'allowed_mcp_tools': instance.allowedMcpTools,
  'ui_pos_x': instance.uiPosX,
  'ui_pos_y': instance.uiPosY,
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
        'task_key',
        'prompt_blocks',
        'pre_hooks',
        'post_hooks',
        'safety',
        'allowed_mcp_tools',
        'model_strategy',
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
      taskKey: $checkedConvert('task_key', (v) => v as String?),
      promptBlocks: $checkedConvert(
        'prompt_blocks',
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
      modelStrategy: $checkedConvert('model_strategy', (v) => v as String?),
      $type: $checkedConvert('type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'taskKey': 'task_key',
    'promptBlocks': 'prompt_blocks',
    'preHooks': 'pre_hooks',
    'postHooks': 'post_hooks',
    'allowedMcpTools': 'allowed_mcp_tools',
    'modelStrategy': 'model_strategy',
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
      'task_key': instance.taskKey,
      'prompt_blocks': instance.promptBlocks,
      'pre_hooks': instance.preHooks,
      'post_hooks': instance.postHooks,
      'safety': instance.safety,
      'allowed_mcp_tools': instance.allowedMcpTools,
      'model_strategy': instance.modelStrategy,
      'type': instance.$type,
    };

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
        'task_key',
        'prompt_blocks',
        'pre_hooks',
        'post_hooks',
        'safety',
        'allowed_mcp_tools',
        'model_strategy',
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
      taskKey: $checkedConvert('task_key', (v) => v as String?),
      promptBlocks: $checkedConvert(
        'prompt_blocks',
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
      modelStrategy: $checkedConvert('model_strategy', (v) => v as String?),
      $type: $checkedConvert('type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'taskKey': 'task_key',
    'promptBlocks': 'prompt_blocks',
    'preHooks': 'pre_hooks',
    'postHooks': 'post_hooks',
    'allowedMcpTools': 'allowed_mcp_tools',
    'modelStrategy': 'model_strategy',
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
      'task_key': instance.taskKey,
      'prompt_blocks': instance.promptBlocks,
      'pre_hooks': instance.preHooks,
      'post_hooks': instance.postHooks,
      'safety': instance.safety,
      'allowed_mcp_tools': instance.allowedMcpTools,
      'model_strategy': instance.modelStrategy,
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
  'expected_inputs': instance.expectedInputs.map((e) => e.toJson()).toList(),
  'steps': instance.steps.map((e) => e.toJson()).toList(),
};
