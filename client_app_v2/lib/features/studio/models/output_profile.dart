// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:client_app/core/models/enums.dart';
import '../../../shared/models/sdui_block_dto.dart';

part 'output_profile.freezed.dart';
part 'output_profile.g.dart';

@Freezed(equal: false)
abstract class OutputLayoutBlock with _$OutputLayoutBlock {
  const OutputLayoutBlock._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory OutputLayoutBlock({
    @Default(PresetView.defaultView)
    @JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)
    PresetView presetView,
    I18nText? title,
    I18nText? description,
    @Default([]) List<String> steps,
    @Default([]) List<String> targetBlocks,
    @Default(TextDeliveryMode.full)
    @JsonKey(
      name: 'text_delivery_mode',
      unknownEnumValue: TextDeliveryMode.full,
    )
    TextDeliveryMode textDeliveryMode,
    @JsonKey(name: 'is_synthesis_enabled')
    @Default(true)
    bool isSynthesisEnabled,
    SynthesisConfigDTO? synthesis,
    @JsonKey(name: 'synthesis_blocks')
    @Default([])
    List<SduiBlockDTO> synthesisBlocks,
    @JsonKey(name: 'strictness_level') int? strictnessLevel,
    @JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,
    @JsonKey(name: 'matrix_column_labels')
    @Default({})
    Map<String, I18nText> matrixColumnLabels,
    @JsonKey(name: 'matrix_visible_columns')
    @Default([])
    List<String> matrixVisibleColumns,
  }) = _OutputLayoutBlock;

  factory OutputLayoutBlock.fromJson(Map<String, dynamic> json) =>
      _$OutputLayoutBlockFromJson(json);
}

@Freezed(equal: false)
abstract class SynthesisConfigDTO with _$SynthesisConfigDTO {
  const SynthesisConfigDTO._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory SynthesisConfigDTO({
    String? systemPrompt,
    int? lengthConstraint,
    I18nText? preambleText,
    @Default(HistoricalContextMode.disabled)
    @JsonKey(
      name: 'historical_context_mode',
      unknownEnumValue: HistoricalContextMode.disabled,
    )
    HistoricalContextMode historicalContextMode,
    @Default(false) bool enablePiiMasking,
    @Default(['pdf', 'raw_json']) List<String> allowedExports,
    @Default(true) bool omitEmptySections,
    @Default([]) List<String> allowedMcpTools,
    @JsonKey(name: 'model_strategy') String? modelStrategy,
    @JsonKey(name: 'tone_instruction') I18nText? toneInstruction,
    @JsonKey(name: 'synthesis_block_id') String? synthesisBlockId,
    @JsonKey(name: 'row_explanations_block_id') String? rowExplanationsBlockId,
  }) = _SynthesisConfigDTO;

  factory SynthesisConfigDTO.fromJson(Map<String, dynamic> json) =>
      _$SynthesisConfigDTOFromJson(json);
}

@Freezed(equal: false)
abstract class OutputProfile with _$OutputProfile {
  const OutputProfile._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory OutputProfile({
    @StrictOpaqueIdConverter() required String id,
    @Default('') String slug,
    @StrictOpaqueIdConverter() required String workflowId,
    String? organizationId,
    required I18nText name,
    I18nText? description,
    @JsonKey(name: 'user_role_label') I18nText? userRoleLabel,
    @JsonKey(name: 'custom_preface') I18nText? customPreface,
    @Default(['date', 'organization']) List<String> visibleMetadata,
    @Default([]) List<XaiExtensionType> visibleBlockExtensions,
    @Default([]) List<XaiExtensionType> visibleWorkflowExtensions,
    @JsonKey(name: 'max_extension_items') int? maxExtensionItems,
    @Default('original') String displayScale,
    @Default(false)
    @JsonKey(name: 'include_diagnostic_scorecard')
    bool includeDiagnosticScorecard,
    @JsonKey(name: 'strictness_level') int? strictnessLevel,
    @JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,
    @JsonKey(name: 'tone_instruction') I18nText? toneInstruction,
    String? language,
    @JsonKey(name: 'user_role_mappings')
    @Default({})
    Map<String, I18nText> userRoleMappings,
    @JsonKey(name: 'extension_labels')
    @Default({})
    Map<String, I18nText> extensionLabels,
    @Default([]) List<OutputLayoutBlock> layouts,
    @JsonKey(name: 'content_blocks')
    @Default([])
    List<SduiBlockDTO> contentBlocks,
    SynthesisConfigDTO? synthesis,
    @JsonKey(name: 'performativity_detector_step_id')
    String? performativityDetectorStepId,
  }) = _OutputProfile;

  factory OutputProfile.fromJson(Map<String, dynamic> json) =>
      _$OutputProfileFromJson(json);
}
