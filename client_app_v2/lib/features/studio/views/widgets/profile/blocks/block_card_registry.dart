import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/metadata_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/synthesis_text_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart';

import 'package:client_app/l10n/gen/app_localizations.dart';

/// Exhaustive registry mapping each TargetBlockType to its dedicated builder widget.
class BlockCardRegistry {
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
      TargetBlockType.executiveSummaryBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.executiveSummaryBlock,
        title: getBlockTitle(TargetBlockType.executiveSummaryBlock, l10n),
        subtitle: getBlockSubtitle(TargetBlockType.executiveSummaryBlock, l10n),
        icon: Icons.summarize_outlined,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.synthesisTextBlock => SynthesisTextBlockCard(
        key: key,
        payload: payload,
        updatePayload: updatePayload,
        promptBlocksState: promptBlocksState,
        dragHandle: dragHandle,
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
        icon: Icons.gavel_outlined,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.matrixSummaryTableBlock => MatrixSummaryTableCard(
        key: key,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.varianceValidationBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.varianceValidationBlock,
        title: getBlockTitle(TargetBlockType.varianceValidationBlock, l10n),
        subtitle: getBlockSubtitle(
          TargetBlockType.varianceValidationBlock,
          l10n,
        ),
        icon: Icons.rule_outlined,
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
        icon: Icons.verified_user_outlined,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
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
        icon: Icons.speed_outlined,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.auditTrailBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.auditTrailBlock,
        title: getBlockTitle(TargetBlockType.auditTrailBlock, l10n),
        subtitle: getBlockSubtitle(TargetBlockType.auditTrailBlock, l10n),
        icon: Icons.history_outlined,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.jargonRatioBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.jargonRatioBlock,
        title: getBlockTitle(TargetBlockType.jargonRatioBlock, l10n),
        subtitle: getBlockSubtitle(TargetBlockType.jargonRatioBlock, l10n),
        icon: Icons.spellcheck_outlined,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
    };
  }

  /// Exposes the registered target block types for test verification.
  static Set<TargetBlockType> get registeredTypes =>
      TargetBlockType.values.toSet();
}
