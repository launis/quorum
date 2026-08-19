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

/// Exhaustive registry mapping each TargetBlockType to its dedicated builder widget.
class BlockCardRegistry {
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
        title: 'Executive Summary',
        subtitle: 'Global multi-step synthesis and management summary',
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
        title: 'Penalties & Deductions',
        subtitle: 'Automated scoring deductions and compliance penalties',
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
        title: 'Variance Validation',
        subtitle: 'Inter-rater variance and statistical confidence bounds',
        icon: Icons.rule_outlined,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.authenticityEvaluationBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.authenticityEvaluationBlock,
        title: 'Authenticity Evaluation',
        subtitle:
            'Source document authenticity and cognitive manipulation checks',
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
        title: 'Global Score',
        subtitle: 'Aggregated final scoring card and benchmark metrics',
        icon: Icons.speed_outlined,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.auditTrailBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.auditTrailBlock,
        title: 'Audit Trail',
        subtitle: 'Forensic event logs and chronological execution trace',
        icon: Icons.history_outlined,
        payload: payload,
        updatePayload: updatePayload,
        dragHandle: dragHandle,
      ),
      TargetBlockType.jargonRatioBlock => SimpleToggleBlockCard(
        key: key,
        blockType: TargetBlockType.jargonRatioBlock,
        title: 'Jargon & Clarity Ratio',
        subtitle: 'Linguistic clarity metrics and domain jargon density',
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
