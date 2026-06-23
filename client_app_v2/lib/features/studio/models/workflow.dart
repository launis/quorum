// ignore_for_file: invalid_annotation_target
import 'dart:convert';
import 'dart:isolate';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'workflow.freezed.dart';
part 'workflow.g.dart';

@Freezed(equal: false)
abstract class QuestionnaireItem with _$QuestionnaireItem {
  const QuestionnaireItem._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory QuestionnaireItem({
    required String questionId,
    required I18nText question,
    required String type,
  }) = _QuestionnaireItem;

  factory QuestionnaireItem.fromJson(Map<String, dynamic> json) =>
      _$QuestionnaireItemFromJson(json);
}

@Freezed(equal: false)
abstract class ExpectedInput with _$ExpectedInput {
  const ExpectedInput._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ExpectedInput({
    required String inputKey,
    required I18nText label,
    required bool required,
    @Default(false) bool isChatHistory,
    @Default([]) List<String> inputModes,
    required I18nText description,
    String? aiDescription,
    @Default([]) List<QuestionnaireItem> questionnaireDefinition,
  }) = _ExpectedInput;

  factory ExpectedInput.fromJson(Map<String, dynamic> json) =>
      _$ExpectedInputFromJson(json);
}

@Freezed(equal: false)
abstract class StepRule with _$StepRule {
  const StepRule._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory StepRule({
    @StrictOpaqueIdConverter() required String id,
    @StrictOpaqueIdConverter() required String taskBlueprint,
    @Default([]) List<String> dependsOn,
    @Default({}) Map<String, String> inputMappings,
    @Default(0.0) double uiPosX,
    @Default(0.0) double uiPosY,
  }) = _StepRule;

  factory StepRule.fromJson(Map<String, dynamic> json) =>
      _$StepRuleFromJson(json);
}

/// Sealed Classes Mandate: Dart 3 Native Pattern Matching
/// Polymorfisille luokille ei sallita Unknown/Fallback -tyyppejä.
@Freezed(unionKey: 'type')
sealed class NodeStrategy with _$NodeStrategy {
  const NodeStrategy._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('llm')
  const factory NodeStrategy.llm({
    @StrictOpaqueIdConverter() required String id,
    required String slug,
    required I18nText name,
    I18nText? description,
    String? hook,
    @StrictOpaqueIdConverter() String? roleBlockId,
    @StrictOpaqueIdConverter() String? extractionProtocolBlockId,
    @StrictOpaqueIdConverter() String? executionPersonaBlockId,
    @Default([]) List<String> criteriaBlockIds,
    @Default([]) List<String> preHooks,
    @Default([]) List<String> postHooks,
    @Default('safe') String safety,
    @Default([]) List<String> allowedMcpTools,
    @Default([]) List<String> expectedInputs,
    Map<String, dynamic>? outputSchema,
    String? modelStrategy,
    String? organizationId,
  }) = NodeStrategyLlm;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('logic')
  const factory NodeStrategy.logic({
    @StrictOpaqueIdConverter() required String id,
    required String slug,
    required I18nText name,
    I18nText? description,
    required String hook,
    @StrictOpaqueIdConverter() String? roleBlockId,
    @StrictOpaqueIdConverter() String? extractionProtocolBlockId,
    @StrictOpaqueIdConverter() String? executionPersonaBlockId,
    @Default([]) List<String> criteriaBlockIds,
    @Default([]) List<String> preHooks,
    @Default([]) List<String> postHooks,
    @Default('safe') String safety,
    @Default([]) List<String> allowedMcpTools,
    @Default([]) List<String> expectedInputs,
    Map<String, dynamic>? outputSchema,
    String? modelStrategy,
    String? organizationId,
  }) = NodeStrategyLogic;

  factory NodeStrategy.fromJson(Map<String, dynamic> json) =>
      _$NodeStrategyFromJson(json);
}

@Freezed(equal: false)
abstract class Workflow with _$Workflow {
  const Workflow._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory Workflow({
    @StrictOpaqueIdConverter() required String id,
    required String slug,
    required I18nText name,
    required I18nText description,
    @Default("draft") String status,
    @Default(1) int version,
    @Default(false) bool isPublic,
    String? organizationId,
    @Default({}) Map<String, dynamic> uiSchema,
    @Default({}) Map<String, EmbeddedOutputProfile> outputProfiles,
    @Default("default") String defaultProfileId,
    @JsonKey(name: 'default_strictness_level')
    @Default(50)
    int defaultStrictnessLevel,
    @JsonKey(name: 'default_scoring_strategy')
    @Default(ScoringStrategy.average)
    ScoringStrategy defaultScoringStrategy,
    @JsonKey(name: 'enable_contextual_overrides')
    @Default(false)
    bool enableContextualOverrides,
    @JsonKey(name: 'enable_semantic_smoothing')
    @Default(false)
    bool enableSemanticSmoothing,
    @JsonKey(name: 'enable_eager_anonymization')
    @Default(false)
    bool enableEagerAnonymization,
    @JsonKey(name: 'system_audit_trail') @Default(false) bool systemAuditTrail,
    @Default([]) List<ExpectedInput> expectedInputs,
    @Default([]) List<StepRule> steps,
  }) = _Workflow;

  factory Workflow.fromJson(Map<String, dynamic> json) =>
      _$WorkflowFromJson(json);

  /// Isolate Mandate: Zero-Latency Illusion requires background parsing
  static Future<Workflow> parseInBackground(String rawJson) async {
    return Isolate.run(() {
      final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
      return Workflow.fromJson(decoded);
    });
  }

  static Future<List<Workflow>> parseListInBackground(
    List<dynamic> rawList,
  ) async {
    return Isolate.run(() {
      return rawList
          .map((e) => Workflow.fromJson(e as Map<String, dynamic>))
          .toList();
    });
  }
}
