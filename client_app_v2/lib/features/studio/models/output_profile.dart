// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:client_app/core/models/enums.dart';
import '../../../shared/models/sdui_block_dto.dart';

part 'output_profile.freezed.dart';
part 'output_profile.g.dart';

@Freezed(equal: false)
abstract class MatrixSynthesisGroup with _$MatrixSynthesisGroup {
  const MatrixSynthesisGroup._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory MatrixSynthesisGroup({
    required String id,
    required I18nText title,
    @JsonKey(name: 'target_blocks') required List<String> targetBlocks,
    @Default(PresetView.metrics1d)
    @JsonKey(name: 'view_type')
    PresetView viewType,
  }) = _MatrixSynthesisGroup;

  factory MatrixSynthesisGroup.fromJson(Map<String, dynamic> json) =>
      _$MatrixSynthesisGroupFromJson(json);
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
    @Default(['date', 'organization', 'user', 'scoring_engine', 'strictness'])
    List<String> visibleMetadata,
    @Default([
      'label',
      'distribution',
      'row_explanation',
      'quotes',
      'normalized_score',
      'score',
    ])
    @JsonKey(name: 'matrix_visible_columns')
    List<String> matrixVisibleColumns,
    @Default([]) List<XaiExtensionType> visibleBlockExtensions,
    @Default([]) List<XaiExtensionType> visibleWorkflowExtensions,
    @Default(3) @JsonKey(name: 'max_extension_items') int maxExtensionItems,
    @Default(DisplayScale.original)
    @JsonKey(name: 'display_scale')
    DisplayScale displayScale,
    @JsonKey(name: 'custom_scale_min') double? customScaleMin,
    @JsonKey(name: 'custom_scale_max') double? customScaleMax,
    @JsonKey(name: 'strictness_level') int? strictnessLevel,
    @JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,
    @JsonKey(name: 'synthesis_length_constraint')
    int? synthesisLengthConstraint,
    @JsonKey(name: 'max_quotes_per_matrix') int? maxQuotesPerMatrix,
    @JsonKey(name: 'max_unmet_criteria') int? maxUnmetCriteria,
    @JsonKey(name: 'tone_instruction') I18nText? toneInstruction,
    @JsonKey(name: 'executive_summary_directive')
    I18nText? executiveSummaryDirective,
    @JsonKey(name: 'matrix_1d_synthesis_directive')
    I18nText? matrix1dSynthesisDirective,
    @JsonKey(name: 'matrix_2d_synthesis_directive')
    I18nText? matrix2dSynthesisDirective,
    @JsonKey(name: 'matrix_3d_synthesis_directive')
    I18nText? matrix3dSynthesisDirective,
    @JsonKey(name: 'matrix_text_synthesis_directive')
    I18nText? matrixTextSynthesisDirective,
    @JsonKey(name: 'row_explanation_directive')
    I18nText? rowExplanationDirective,
    @JsonKey(name: 'xai_synthesis_directive') I18nText? xaiSynthesisDirective,
    @JsonKey(name: 'variance_synthesis_directive')
    I18nText? varianceSynthesisDirective,
    SystemLocale? language,
    @JsonKey(name: 'matrix_synthesis_groups')
    @Default([])
    List<MatrixSynthesisGroup> matrixSynthesisGroups,
    @JsonKey(name: 'content_blocks')
    @Default([])
    List<SduiBlockDTO> contentBlocks,
    @JsonKey(name: 'target_block_order')
    @Default([
      TargetBlockType.metadataBlock,
      TargetBlockType.executiveSummaryBlock,
      TargetBlockType.synthesisTextBlock,
      TargetBlockType.matrixGraphsBlock,
      TargetBlockType.groupedExtensionsBlock,
      TargetBlockType.penaltiesBlock,
      TargetBlockType.matrixSummaryTableBlock,
      TargetBlockType.varianceValidationBlock,
      TargetBlockType.authenticityEvaluationBlock,
      TargetBlockType.printableSourcesBlock,
      TargetBlockType.globalScoreBlock,
      TargetBlockType.auditTrailBlock,
    ])
    List<TargetBlockType> targetBlockOrder,
    @Default(true)
    @JsonKey(name: 'show_sources_summary_box')
    bool showSourcesSummaryBox,
    @Default(SourcesDisplayMode.verifiedEvidence)
    @JsonKey(name: 'sources_display_mode')
    SourcesDisplayMode sourcesDisplayMode,
    @JsonKey(name: 'performativity_detector_step_id')
    String? performativityDetectorStepId,
  }) = _OutputProfile;

  factory OutputProfile.fromJson(Map<String, dynamic> json) =>
      _$OutputProfileFromJson(json);
}
