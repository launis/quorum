// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';

part 'output_profile.freezed.dart';
part 'output_profile.g.dart';

@Freezed(equal: false)
abstract class OutputLayoutBlock with _$OutputLayoutBlock {
  const OutputLayoutBlock._();

  const factory OutputLayoutBlock({
    @Default(PresetView.defaultView)
    @JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)
    PresetView presetView,
    I18nText? title,
    I18nText? description,
    @Default([]) List<String> steps,
    @Default([]) List<String> targetBlocks,
    @Default('full')
    @JsonKey(name: 'text_delivery_mode')
    String textDeliveryMode,
    SynthesisConfigDTO? synthesis,
    @JsonKey(name: 'synthesis_blocks')
    @Default([])
    List<SduiBlockDTO> synthesisBlocks,
    @JsonKey(name: 'strictness_level') int? strictnessLevel,
    @JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,
  }) = _OutputLayoutBlock;

  factory OutputLayoutBlock.fromJson(Map<String, dynamic> json) =>
      _$OutputLayoutBlockFromJson(json);
}

@Freezed(equal: false)
abstract class SynthesisConfigDTO with _$SynthesisConfigDTO {
  const SynthesisConfigDTO._();

  const factory SynthesisConfigDTO({
    String? systemPrompt,
    int? lengthConstraint,
    I18nText? preambleText,
    @Default('DISABLED')
    @JsonKey(name: 'historical_context_mode')
    String historicalContextMode,
    @Default(false) bool enablePiiMasking,
    @Default(['pdf', 'raw_json']) List<String> allowedExports,
    @Default(true) bool omitEmptySections,
    @Default([]) List<String> allowedMcpTools,
    @Default(['label', 'score', 'distribution', 'row_explanation'])
    @JsonKey(name: 'matrix_visible_columns')
    List<String> matrixVisibleColumns,
    @JsonKey(name: 'model_strategy') String? modelStrategy,
    @JsonKey(name: 'tone_instruction') I18nText? toneInstruction,
  }) = _SynthesisConfigDTO;

  factory SynthesisConfigDTO.fromJson(Map<String, dynamic> json) =>
      _$SynthesisConfigDTOFromJson(json);
}

@Freezed(equal: false)
abstract class OutputProfile with _$OutputProfile {
  const OutputProfile._();

  const factory OutputProfile({
    @StrictOpaqueIdConverter() required String id,
    @Default('') String slug,
    @StrictOpaqueIdConverter() required String workflowId,
    String? organizationId,
    required I18nText name,
    I18nText? description,
    @JsonKey(name: 'custom_preface') I18nText? customPreface,
    @Default(['date', 'organization']) List<String> visibleMetadata,
    @Default([]) List<XaiExtensionType> visibleBlockExtensions,
    @Default([]) List<XaiExtensionType> visibleWorkflowExtensions,
    @JsonKey(name: 'max_extension_items') int? maxExtensionItems,
    @Default('original') String displayScale,
    SynthesisConfigDTO? synthesis,
    @Default(false)
    @JsonKey(name: 'include_diagnostic_scorecard')
    bool includeDiagnosticScorecard,
    @JsonKey(name: 'strictness_level') int? strictnessLevel,
    @JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,
    @JsonKey(name: 'tone_instruction') I18nText? toneInstruction,
    @Default([]) List<OutputLayoutBlock> layouts,
  }) = _OutputProfile;

  factory OutputProfile.fromJson(Map<String, dynamic> json) =>
      _$OutputProfileFromJson(json);
}

@Freezed(equal: false)
abstract class EmbeddedOutputProfile with _$EmbeddedOutputProfile {
  const EmbeddedOutputProfile._();

  const factory EmbeddedOutputProfile({
    required I18nText name,
    I18nText? description,
    @JsonKey(name: 'custom_preface') I18nText? customPreface,
    @Default(['date', 'organization']) List<String> visibleMetadata,
    @Default([]) List<XaiExtensionType> visibleBlockExtensions,
    @Default([]) List<XaiExtensionType> visibleWorkflowExtensions,
    @JsonKey(name: 'max_extension_items') int? maxExtensionItems,
    @Default('original') String displayScale,
    SynthesisConfigDTO? synthesis,
    @Default(false)
    @JsonKey(name: 'include_diagnostic_scorecard')
    bool includeDiagnosticScorecard,
    @JsonKey(name: 'strictness_level') int? strictnessLevel,
    @JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,
    @JsonKey(name: 'tone_instruction') I18nText? toneInstruction,
    @Default([]) List<OutputLayoutBlock> layouts,
  }) = _EmbeddedOutputProfile;

  factory EmbeddedOutputProfile.fromJson(Map<String, dynamic> json) =>
      _$EmbeddedOutputProfileFromJson(json);
}
