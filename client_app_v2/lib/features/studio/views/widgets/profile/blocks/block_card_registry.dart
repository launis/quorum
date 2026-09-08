import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/executive_summary_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/metadata_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/variance_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart';

import 'package:client_app/l10n/gen/app_localizations.dart';

/// Exhaustive registry mapping each TargetBlockType to its dedicated builder widget.
class BlockCardRegistry {
  /// SSOT map of TargetBlockTypes that synchronize corresponding workflow-level XAI extensions.
  static const Map<TargetBlockType, List<XaiExtensionType>>
  syncWorkflowExtensionsMap = {
    TargetBlockType.varianceValidationBlock: [
      XaiExtensionType.varianceValidation,
    ],
    TargetBlockType.authenticityEvaluationBlock: [
      XaiExtensionType.authenticityEvaluation,
    ],
  };

  /// Detailed block types that require dedicated editor cards on Tab 3 (Section Config).
  static const Set<TargetBlockType> detailedBlockTypes = {
    TargetBlockType.executiveSummaryBlock,
    TargetBlockType.matrixGraphsBlock,
    TargetBlockType.metadataBlock,
    TargetBlockType.matrixSummaryTableBlock,
    TargetBlockType.groupedExtensionsBlock,
    TargetBlockType.varianceValidationBlock,
    TargetBlockType.printableSourcesBlock,
  };

  static String getBlockTitle(TargetBlockType type, AppLocalizations l10n) {
    return switch (type) {
      TargetBlockType.metadataBlock => l10n.blockMetadataTitle,
      TargetBlockType.executiveSummaryBlock => l10n.blockExecutiveSummaryTitle,
      TargetBlockType.synthesisTextBlock => l10n.blockSynthesisTextTitle,
      TargetBlockType.matrixGraphsBlock => l10n.blockMatrixGraphsTitle,
      TargetBlockType.groupedExtensionsBlock => l10n.blockAiExtensionsTitle,
      TargetBlockType.penaltiesBlock => l10n.blockPenaltiesTitle,
      TargetBlockType.matrixSummaryTableBlock => l10n.blockMatrixSummaryTitle,
      TargetBlockType.varianceValidationBlock => l10n.blockVarianceTitle,
      TargetBlockType.authenticityEvaluationBlock =>
        l10n.blockAuthenticityTitle,
      TargetBlockType.printableSourcesBlock => l10n.blockBibliographyTitle,
      TargetBlockType.globalScoreBlock => l10n.blockGlobalScoreTitle,
      TargetBlockType.auditTrailBlock => l10n.blockAuditTrailTitle,
      TargetBlockType.jargonRatioBlock => l10n.blockJargonRatioTitle,
    };
  }

  static String getBlockSubtitle(TargetBlockType type, AppLocalizations l10n) {
    return switch (type) {
      TargetBlockType.metadataBlock => l10n.blockMetadataSubtitle,
      TargetBlockType.executiveSummaryBlock =>
        l10n.blockExecutiveSummarySubtitle,
      TargetBlockType.synthesisTextBlock => l10n.blockSynthesisTextSubtitle,
      TargetBlockType.matrixGraphsBlock => l10n.blockMatrixGraphsSubtitle,
      TargetBlockType.groupedExtensionsBlock => l10n.blockAiExtensionsSubtitle,
      TargetBlockType.penaltiesBlock => l10n.blockPenaltiesSubtitle,
      TargetBlockType.matrixSummaryTableBlock =>
        l10n.blockMatrixSummarySubtitle,
      TargetBlockType.varianceValidationBlock => l10n.blockVarianceSubtitle,
      TargetBlockType.authenticityEvaluationBlock =>
        l10n.blockAuthenticitySubtitle,
      TargetBlockType.printableSourcesBlock => l10n.blockBibliographySubtitle,
      TargetBlockType.globalScoreBlock => l10n.blockGlobalScoreSubtitle,
      TargetBlockType.auditTrailBlock => l10n.blockAuditTrailSubtitle,
      TargetBlockType.jargonRatioBlock => l10n.blockJargonRatioSubtitle,
    };
  }

  static IconData getBlockIcon(TargetBlockType type) {
    return switch (type) {
      TargetBlockType.metadataBlock => Icons.info_outline,
      TargetBlockType.executiveSummaryBlock => Icons.summarize_outlined,
      TargetBlockType.synthesisTextBlock => Icons.auto_stories_outlined,
      TargetBlockType.matrixGraphsBlock => Icons.bar_chart_outlined,
      TargetBlockType.groupedExtensionsBlock => Icons.extension_outlined,
      TargetBlockType.penaltiesBlock => Icons.gavel_outlined,
      TargetBlockType.matrixSummaryTableBlock => Icons.table_chart_outlined,
      TargetBlockType.varianceValidationBlock => Icons.rule_outlined,
      TargetBlockType.authenticityEvaluationBlock =>
        Icons.verified_user_outlined,
      TargetBlockType.printableSourcesBlock => Icons.menu_book_outlined,
      TargetBlockType.globalScoreBlock => Icons.speed_outlined,
      TargetBlockType.auditTrailBlock => Icons.history_outlined,
      TargetBlockType.jargonRatioBlock => Icons.spellcheck_outlined,
    };
  }

  /// Returns dedicated full editor cards (used in Tab 3: Section Config).
  static Widget getBlockCard({
    Key? key,
    required TargetBlockType type,
    required BuildContext context,
    required String profileId,
    required OutputProfile payload,
    required void Function(OutputProfile) updatePayload,
    required Set<String> allowedBlockIds,
    required AsyncValue<List<PromptBlock>> promptBlocksState,
    Widget? dragHandle,
  }) {
    final l10n = AppLocalizations.of(context)!;

    return switch (type) {
      TargetBlockType.metadataBlock => MetadataBlockCard(
        key: key,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.executiveSummaryBlock => ExecutiveSummaryBlockCard(
        key: key,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.synthesisTextBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.synthesisTextBlock,
        title: getBlockTitle(TargetBlockType.synthesisTextBlock, l10n),
        subtitle: getBlockSubtitle(TargetBlockType.synthesisTextBlock, l10n),
        icon: getBlockIcon(TargetBlockType.synthesisTextBlock),
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
        syncWorkflowExtensions: syncWorkflowExtensionsMap[type],
      ),
      TargetBlockType.matrixGraphsBlock => MatrixGraphsBlockCard(
        key: key,
        payload: payload,
        updatePayload: updatePayload,
        allowedBlockIds: allowedBlockIds,
        promptBlocksState: promptBlocksState,
        dragHandle: dragHandle,
      ),
      TargetBlockType.groupedExtensionsBlock => XaiExtensionsBlockCard(
        key: key,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.penaltiesBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.penaltiesBlock,
        title: getBlockTitle(TargetBlockType.penaltiesBlock, l10n),
        subtitle: getBlockSubtitle(TargetBlockType.penaltiesBlock, l10n),
        icon: getBlockIcon(TargetBlockType.penaltiesBlock),
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
        syncWorkflowExtensions: syncWorkflowExtensionsMap[type],
      ),
      TargetBlockType.matrixSummaryTableBlock => MatrixSummaryTableCard(
        key: key,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.varianceValidationBlock => VarianceBlockCard(
        key: key,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.authenticityEvaluationBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.authenticityEvaluationBlock,
        title: getBlockTitle(TargetBlockType.authenticityEvaluationBlock, l10n),
        subtitle: getBlockSubtitle(
          TargetBlockType.authenticityEvaluationBlock,
          l10n,
        ),
        icon: getBlockIcon(TargetBlockType.authenticityEvaluationBlock),
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
        syncWorkflowExtensions: syncWorkflowExtensionsMap[type],
      ),
      TargetBlockType.printableSourcesBlock => BibliographyBlockCard(
        key: key,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.globalScoreBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.globalScoreBlock,
        title: getBlockTitle(TargetBlockType.globalScoreBlock, l10n),
        subtitle: getBlockSubtitle(TargetBlockType.globalScoreBlock, l10n),
        icon: getBlockIcon(TargetBlockType.globalScoreBlock),
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
        syncWorkflowExtensions: syncWorkflowExtensionsMap[type],
      ),
      TargetBlockType.auditTrailBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.auditTrailBlock,
        title: getBlockTitle(TargetBlockType.auditTrailBlock, l10n),
        subtitle: getBlockSubtitle(TargetBlockType.auditTrailBlock, l10n),
        icon: getBlockIcon(TargetBlockType.auditTrailBlock),
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
        syncWorkflowExtensions: syncWorkflowExtensionsMap[type],
      ),
      TargetBlockType.jargonRatioBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.jargonRatioBlock,
        title: getBlockTitle(TargetBlockType.jargonRatioBlock, l10n),
        subtitle: getBlockSubtitle(TargetBlockType.jargonRatioBlock, l10n),
        icon: getBlockIcon(TargetBlockType.jargonRatioBlock),
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
        syncWorkflowExtensions: syncWorkflowExtensionsMap[type],
      ),
    };
  }

  /// Returns uniform SimpleToggleBlockCard widgets for Tab 4 (Report Structure).
  static Widget getSimpleToggleCard({
    Key? key,
    required TargetBlockType type,
    required BuildContext context,
    required OutputProfile payload,
    required void Function(OutputProfile) updatePayload,
    Widget? dragHandle,
  }) {
    final l10n = AppLocalizations.of(context)!;
    return SimpleToggleBlockCard(
      key: key,
      blockType: type,
      title: getBlockTitle(type, l10n),
      subtitle: getBlockSubtitle(type, l10n),
      icon: getBlockIcon(type),
      payload: payload,
      updatePayload: updatePayload,
      dragHandle: dragHandle,
      syncWorkflowExtensions: syncWorkflowExtensionsMap[type],
    );
  }

  /// Exposes the registered target block types for test verification.
  static Set<TargetBlockType> get registeredTypes =>
      TargetBlockType.values.toSet();
}
