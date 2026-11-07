import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/utils/safe_isolate.dart';
import 'dart:convert';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'workflow.freezed.dart';
part 'workflow.g.dart';

/// Phase 5, Step 5.1: Strongly typed MCP tool parameter override value replacing `Map<String, Object?>`.
@freezed
abstract class McpToolParamValue with _$McpToolParamValue {
  const McpToolParamValue._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory McpToolParamValue({
    @JsonKey(name: 'string_value') String? stringValue,
    @JsonKey(name: 'int_value') int? intValue,
    @JsonKey(name: 'double_value') double? doubleValue,
    @JsonKey(name: 'bool_value') bool? boolValue,
    @JsonKey(name: 'string_list_value') List<String>? stringListValue,
  }) = _McpToolParamValue;

  factory McpToolParamValue.fromPrimitive(Object? value) {
    if (value is McpToolParamValue) {
      return value;
    }
    if (value is List) {
      return McpToolParamValue(
        stringListValue: value
            .map((Object? e) => e.toString())
            .toList(growable: false),
      );
    }
    if (value is bool) {
      return McpToolParamValue(boolValue: value);
    }
    if (value is int) {
      return McpToolParamValue(intValue: value);
    }
    if (value is double) {
      return McpToolParamValue(doubleValue: value);
    }
    if (value is num) {
      return McpToolParamValue(doubleValue: value.toDouble());
    }
    if (value is String) {
      return McpToolParamValue(stringValue: value);
    }
    return const McpToolParamValue();
  }

  factory McpToolParamValue.fromJson(Map<String, dynamic> json) =>
      _$McpToolParamValueFromJson(json);

  Object? get rawValue =>
      stringListValue ?? boolValue ?? intValue ?? doubleValue ?? stringValue;
}

/// Converter serializing [McpToolParamValue] directly as JSON primitives/arrays on the wire.
class McpToolParamValueConverter
    implements JsonConverter<McpToolParamValue, Object?> {
  const McpToolParamValueConverter();

  @override
  McpToolParamValue fromJson(Object? json) =>
      McpToolParamValue.fromPrimitive(json);

  @override
  Object? toJson(McpToolParamValue object) => object.rawValue;
}

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
    @Default(false)
    @JsonKey(name: 'is_endorsed_deliverable')
    bool isEndorsedDeliverable,
    @Default([]) List<String> inputModes,
    required I18nText description,
    @Default(false) bool scanForPerformativePatterns,
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
    @JsonKey(name: 'expected_sdui_type') SduiBlockType? expectedSduiType,
    @Default(0.0) double uiPosX,
    @Default(0.0) double uiPosY,
    @Default(true) @JsonKey(name: 'is_synthesis_source') bool isSynthesisSource,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'causal_source_step_id')
    String? causalSourceStepId,
  }) = _StepRule;

  factory StepRule.fromJson(Map<String, dynamic> json) =>
      _$StepRuleFromJson(json);
}

/// Sealed Classes Mandate: Unknown/Fallback union types are strictly forbidden.
@Freezed(unionKey: 'type', equal: false)
sealed class NodeStrategy with _$NodeStrategy {
  const NodeStrategy._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
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
    @JsonKey(name: 'mcp_tool_params')
    @McpToolParamValueConverter()
    @Default(<String, Map<String, McpToolParamValue>>{})
    Map<String, Map<String, McpToolParamValue>> mcpToolParams,
    @Default([]) List<String> expectedInputs,
    @JsonKey(name: 'cognitive_tier')
    @Default(CognitiveTier.fast)
    CognitiveTier cognitiveTier,
    String? organizationId,
    @Default(false) @JsonKey(name: 'is_system_core') bool isSystemCore,
    @JsonKey(name: 'engine_type')
    @Default(EngineType.prompt)
    EngineType engineType,
    @JsonKey(name: 'zone') @Default(StepZone.zoneB) StepZone zone,
  }) = NodeStrategyLlm;

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
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
    @JsonKey(name: 'mcp_tool_params')
    @McpToolParamValueConverter()
    @Default(<String, Map<String, McpToolParamValue>>{})
    Map<String, Map<String, McpToolParamValue>> mcpToolParams,
    @Default([]) List<String> expectedInputs,
    @JsonKey(name: 'cognitive_tier')
    @Default(CognitiveTier.fast)
    CognitiveTier cognitiveTier,
    String? organizationId,
    @Default(false) @JsonKey(name: 'is_system_core') bool isSystemCore,
    @JsonKey(name: 'engine_type')
    @Default(EngineType.prompt)
    EngineType engineType,
    @JsonKey(name: 'zone') @Default(StepZone.zoneB) StepZone zone,
  }) = NodeStrategyLogic;

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  @FreezedUnionValue('causal_discovery')
  const factory NodeStrategy.causalDiscovery({
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
    @JsonKey(name: 'mcp_tool_params')
    @McpToolParamValueConverter()
    @Default(<String, Map<String, McpToolParamValue>>{})
    Map<String, Map<String, McpToolParamValue>> mcpToolParams,
    @Default([]) List<String> expectedInputs,
    @JsonKey(name: 'cognitive_tier')
    @Default(CognitiveTier.fast)
    CognitiveTier cognitiveTier,
    String? organizationId,
    @Default(false) @JsonKey(name: 'is_system_core') bool isSystemCore,
    @JsonKey(name: 'engine_type')
    @Default(EngineType.causalDiscovery)
    EngineType engineType,
    @JsonKey(name: 'zone') @Default(StepZone.zoneB) StepZone zone,
  }) = NodeStrategyCausalDiscovery;

  factory NodeStrategy.fromJson(Map<String, dynamic> json) =>
      _$NodeStrategyFromJson(json);
}

@Freezed(equal: false)
abstract class Workflow with _$Workflow {
  const Workflow._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory Workflow({
    @StrictOpaqueIdConverter() required String id,
    required String slug,
    required I18nText name,
    required I18nText description,
    @Default("draft") String status,
    @Default(1) int version,
    @Default(false) bool isPublic,
    String? organizationId,
    @Default({}) Map<String, OutputProfile> outputProfiles,
    @Default("default") String defaultProfileId,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'mcp_gateway_id')
    String? mcpGatewayId,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'model_registry_id')
    required String modelRegistryId,
    @JsonKey(name: 'default_strictness_level')
    @Default(50)
    int defaultStrictnessLevel,
    @JsonKey(name: 'default_lexical_strictness_level')
    @Default(50)
    int defaultLexicalStrictnessLevel,
    @JsonKey(name: 'security_penalty') @Default(0.0) double securityPenalty,
    @JsonKey(name: 'post_hoc_penalty') @Default(0.0) double postHocPenalty,
    @JsonKey(name: 'passivity_penalty') @Default(0.0) double passivityPenalty,
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
    @JsonKey(name: 'historical_context_mode')
    @Default(HistoricalContextMode.disabled)
    HistoricalContextMode historicalContextMode,
    @Default([]) List<ExpectedInput> expectedInputs,
    @Default([]) List<StepRule> steps,
  }) = _Workflow;

  factory Workflow.fromJson(Map<String, dynamic> json) =>
      _$WorkflowFromJson(json);

  /// Isolate Mandate: Zero-Latency Illusion requires background parsing
  static Future<Workflow> parseInBackground(String rawJson) async {
    return safeIsolateRun(() {
      // Phase 5, Step 5.1: Eliminate Map<String, Object?> cast in background isolate
      final Object? decoded = jsonDecode(rawJson);
      if (decoded is! Map) {
        throw AppException.validation(
          'Malformed Workflow JSON payload: expected JSON object.',
        );
      }
      return Workflow.fromJson(Map.from(decoded));
    });
  }

  static Future<List<Workflow>> parseListInBackground(
    List<Object?> rawList,
  ) async {
    return safeIsolateRun(() {
      return rawList
          .map((Object? item) {
            if (item is! Map) {
              throw AppException.validation(
                'Malformed Workflow list item: expected JSON object.',
              );
            }
            return Workflow.fromJson(Map.from(item));
          })
          .toList(growable: false);
    });
  }
}
