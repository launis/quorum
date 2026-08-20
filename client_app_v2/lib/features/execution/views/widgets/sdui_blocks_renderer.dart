import 'package:flutter/material.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:client_app/features/execution/views/widgets/sdui_alert_box_widget.dart';
import 'package:client_app/features/execution/views/widgets/sdui_grid_widget.dart';
import 'package:client_app/shared/widgets/logic_radar_chart.dart';
import 'package:client_app/shared/widgets/logic_matrix_chart.dart';
import 'package:client_app/features/execution/views/widgets/matrix_row_item_widget.dart';
import 'package:client_app/features/execution/views/widgets/sdui_matrix_table_widget.dart';
import 'package:client_app/features/execution/views/widgets/xai_evidence_box.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';

class SduiBlocksRenderer extends StatelessWidget {
  final List<SduiBlockDTO> blocks;
  final List<McpAuditTraceDto>? mcpToolAudit;

  const SduiBlocksRenderer({
    super.key,
    required this.blocks,
    this.mcpToolAudit,
  });

  @override
  Widget build(BuildContext context) {
    if (blocks.isEmpty) return const SizedBox();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: blocks.map((block) {
        return switch (block) {
          SduiAccordionBlock() => _buildAccordion(context, block),
          SduiMetadataBlock() => _buildMetadata(context, block),
          SduiScoreCardBlock() => _buildScoreCard(context, block),
          SduiAuditTrailBlock() => _buildAuditTrail(context, block),
          SduiAlertBoxBlock() => SduiAlertBoxWidget(block: block),
          SduiGridBlock() => SduiGridWidget(block: block),
          SduiMarkdownBlock() =>
            block.text.isNotEmpty
                ? Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.s8),
                    child: OutputRenderer(markdownContent: block.text),
                  )
                : const SizedBox.shrink(),
          SduiParagraphBlock() =>
            block.text.isNotEmpty
                ? Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.s8),
                    child: OutputRenderer(markdownContent: block.text),
                  )
                : const SizedBox.shrink(),
          SduiRadarChartBlock() => _buildChartWithTitle(
            context,
            block.title,
            LogicRadarChart(axes: block.axes),
          ),
          SduiScatterPlotBlock() => _buildChartWithTitle(
            context,
            block.title,
            LogicMatrixChart(
              xAxis: block.axes[0],
              yAxis: block.axes[1],
              zAxis: block.axes.length > 2 ? block.axes[2] : null,
            ),
          ),
          SduiMetrics1DBlock() => _buildChartWithTitle(
            context,
            block.title,
            Column(
              children: block.axes
                  .map((axis) => MatrixRowItemWidget(matrix: axis))
                  .toList(),
            ),
          ),
          SduiMatrixTableBlock() => SduiMatrixTableWidget(block: block),
          SduiBulletListBlock() => _buildBulletList(context, block),
          SduiHeroInsightBlock() => _buildHeroInsight(context, block),
          SduiQuoteCardBlock() => _buildQuoteCard(context, block),
          SduiWarningCardBlock() => _buildWarningCard(context, block),
          SduiNACardBlock() => _buildNACard(context, block),
        };
      }).toList(),
    );
  }

  Widget _buildHeroInsight(BuildContext context, SduiHeroInsightBlock block) {
    if (block.text.isEmpty) return const SizedBox.shrink();
    final theme = Theme.of(context);
    return Container(
      margin: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
      padding: const EdgeInsets.all(AppSpacing.s16),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        border: Border(
          left: BorderSide(
            color: theme.colorScheme.primary,
            width: AppSpacing.s4,
          ),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.lightbulb_outline,
            color: theme.colorScheme.primary,
            size: 24,
          ),
          AppSpacing.w8,
          Expanded(child: OutputRenderer(markdownContent: block.text)),
        ],
      ),
    );
  }

  Widget _buildBulletList(BuildContext context, SduiBulletListBlock block) {
    if (block.items.isEmpty) return const SizedBox.shrink();
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: block.items.map((item) {
          if (item.text.isEmpty) return const SizedBox.shrink();
          return Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.s6),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(
                    top: AppSpacing.s8,
                    left: AppSpacing.s4,
                    right: AppSpacing.s8,
                  ),
                  child: Icon(
                    Icons.circle,
                    size: AppSpacing.s6,
                    color: theme.colorScheme.primary,
                  ),
                ),
                Expanded(child: OutputRenderer(markdownContent: item.text)),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildQuoteCard(BuildContext context, SduiQuoteCardBlock block) {
    if (block.quote.isEmpty) return const SizedBox.shrink();
    final theme = Theme.of(context);
    return Card(
      elevation: 1,
      margin: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        side: BorderSide(
          color: theme.colorScheme.outlineVariant,
          width: AppSpacing.s2 / 2,
        ),
      ),
      color: theme.colorScheme.surfaceContainerLow,
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.s16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.format_quote,
                  color: theme.colorScheme.primary,
                  size: 24,
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    block.quote,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
              ],
            ),
            if (block.sourceAliases.isNotEmpty ||
                block.citations.isNotEmpty) ...[
              AppSpacing.h12,
              Wrap(
                spacing: AppSpacing.s8,
                runSpacing: AppSpacing.s4,
                children: [
                  ...block.sourceAliases.map(
                    (alias) => Chip(
                      label: Text(
                        alias,
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.onSecondaryContainer,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      backgroundColor: theme.colorScheme.secondaryContainer,
                      visualDensity: VisualDensity.compact,
                      padding: EdgeInsets.zero,
                    ),
                  ),
                  if (block.citations.isNotEmpty)
                    Chip(
                      avatar: Icon(
                        Icons.bookmark_outline,
                        size: 14,
                        color: theme.colorScheme.primary,
                      ),
                      label: Text(
                        block.citations.map((c) => '[$c]').join(' '),
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      backgroundColor: theme.colorScheme.primaryContainer,
                      visualDensity: VisualDensity.compact,
                      padding: EdgeInsets.zero,
                    ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildWarningCard(BuildContext context, SduiWarningCardBlock block) {
    if (block.message.isEmpty) return const SizedBox.shrink();
    final theme = Theme.of(context);
    return Container(
      margin: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
      padding: const EdgeInsets.all(AppSpacing.s16),
      decoration: BoxDecoration(
        color: AppColors.intentWarning.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        border: Border(
          left: BorderSide(
            color: AppColors.intentWarning,
            width: AppSpacing.s4,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(
                Icons.warning_amber_rounded,
                color: AppColors.intentWarning,
                size: 24,
              ),
              AppSpacing.w8,
              Expanded(child: OutputRenderer(markdownContent: block.message)),
            ],
          ),
          if (block.quoteText != null && block.quoteText!.isNotEmpty) ...[
            AppSpacing.h12,
            Container(
              padding: const EdgeInsets.all(AppSpacing.s12),
              decoration: BoxDecoration(
                color: theme.colorScheme.surface,
                borderRadius: BorderRadius.circular(AppSpacing.s4),
                border: Border.all(
                  color: AppColors.intentWarning.withValues(alpha: 0.3),
                ),
              ),
              child: Text(
                block.quoteText!,
                style: theme.textTheme.bodySmall?.copyWith(
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildNACard(BuildContext context, SduiNACardBlock block) {
    final theme = Theme.of(context);
    return Container(
      margin: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
      padding: const EdgeInsets.all(AppSpacing.s16),
      decoration: BoxDecoration(
        color: AppColors.intentNeutral.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        border: Border(
          left: BorderSide(
            color: AppColors.intentNeutral,
            width: AppSpacing.s4,
          ),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(
            Icons.info_outline,
            color: AppColors.intentNeutral,
            size: 24,
          ),
          AppSpacing.w8,
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                OutputRenderer(markdownContent: block.message),
                if (block.shortCircuitReasonTdaIds.isNotEmpty) ...[
                  AppSpacing.h8,
                  Wrap(
                    spacing: AppSpacing.s4,
                    runSpacing: AppSpacing.s4,
                    children: block.shortCircuitReasonTdaIds
                        .map(
                          (tdaId) => Chip(
                            label: Text(
                              tdaId,
                              style: theme.textTheme.labelSmall?.copyWith(
                                fontFamily: 'monospace',
                              ),
                            ),
                            visualDensity: VisualDensity.compact,
                            padding: EdgeInsets.zero,
                          ),
                        )
                        .toList(),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAccordion(BuildContext context, SduiAccordionBlock block) {
    final theme = Theme.of(context);
    Color headerColor;
    Color bgColor;
    IconData? icon;

    switch (block.severity) {
      case 'success':
        headerColor = AppColors.intentSuccess;
        bgColor = AppColors.intentSuccess.withValues(alpha: 0.1);
        icon = Icons.build;
        break;
      case 'warning':
        headerColor = AppColors.intentWarning;
        bgColor = AppColors.intentWarning.withValues(alpha: 0.1);
        icon = Icons.warning;
        break;
      case 'error':
        headerColor = theme.colorScheme.error;
        bgColor = theme.colorScheme.errorContainer;
        icon = Icons.error;
        break;
      case 'info':
      default:
        headerColor = AppColors.intentInfo;
        bgColor = AppColors.intentInfo.withValues(alpha: 0.1);
        icon = Icons.info;
        break;
    }

    if (block.iconName == 'lightbulb') icon = Icons.lightbulb;
    if (block.iconName == 'balance') icon = Icons.balance;

    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s8),
      ),
      color: bgColor,
      child: ExpansionTile(
        initiallyExpanded: true,
        leading: Icon(icon, color: headerColor),
        title: Text(
          block.title,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: headerColor,
          ),
        ),
        children: [
          Container(
            color: theme.colorScheme.surface,
            padding: const EdgeInsets.all(AppSpacing.s12),
            child: SduiBlocksRenderer(blocks: block.children),
          ),
        ],
      ),
    );
  }

  Widget _buildMetadata(BuildContext context, SduiMetadataBlock block) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: AppSpacing.s16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
        side: BorderSide(color: AppColors.intentSuccess, width: AppSpacing.s2),
      ),
      color: theme.colorScheme.surfaceContainerLowest,
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.s16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              block.title,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            AppSpacing.h12,
            if (block.badges.isNotEmpty)
              Wrap(
                alignment: WrapAlignment.center,
                spacing: AppSpacing.s8,
                runSpacing: AppSpacing.s8,
                children: block.badges
                    .map(
                      (b) => Chip(
                        label: Text(
                          b,
                          style: theme.textTheme.labelSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: theme.colorScheme.primary,
                          ),
                        ),
                        backgroundColor: theme.colorScheme.primaryContainer,
                        side: BorderSide(
                          color: theme.colorScheme.primary.withValues(
                            alpha: 0.5,
                          ),
                        ),
                      ),
                    )
                    .toList(),
              ),
            AppSpacing.h16,
            if (block.metadataLines.isNotEmpty)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: block.metadataLines
                    .map(
                      (line) => Padding(
                        padding: const EdgeInsets.only(bottom: AppSpacing.s4),
                        child: OutputRenderer(markdownContent: line),
                      ),
                    )
                    .toList(),
              ),
            if (block.costs != null || block.tokens != null) ...[
              const Divider(height: AppSpacing.s24),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (block.costs != null)
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n.sduiMetadataCosts,
                            style: theme.textTheme.labelSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(block.costs!, style: theme.textTheme.labelSmall),
                        ],
                      ),
                    ),
                  if (block.tokens != null)
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n.sduiMetadataTokens,
                            style: theme.textTheme.labelSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          ...block.tokens!.entries.map(
                            (e) => Text(
                              '${e.key}: ${e.value}',
                              style: theme.textTheme.labelSmall,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ],
            if (block.customPrefaceMd != null &&
                block.customPrefaceMd!.isNotEmpty) ...[
              AppSpacing.h24,
              Container(
                padding: const EdgeInsets.all(AppSpacing.s16),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surface,
                  border: Border.all(
                    color: AppColors.intentInfo,
                    width: AppSpacing.s2,
                  ),
                  borderRadius: BorderRadius.circular(AppSpacing.s8),
                ),
                child: OutputRenderer(markdownContent: block.customPrefaceMd!),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildScoreCard(BuildContext context, SduiScoreCardBlock block) {
    if (block.globalScore == null) return const SizedBox.shrink();
    final l10n = AppLocalizations.of(context)!;
    return Container(
      margin: const EdgeInsets.symmetric(vertical: AppSpacing.s16),
      padding: const EdgeInsets.all(AppSpacing.s16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(AppSpacing.s8),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            l10n.scorecard_global_average,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: Theme.of(context).colorScheme.onPrimaryContainer,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            '${block.globalScore!.toStringAsFixed(2)}/100',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              color: Theme.of(context).colorScheme.onPrimaryContainer,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAuditTrail(BuildContext context, SduiAuditTrailBlock block) {
    if (mcpToolAudit == null || mcpToolAudit!.isEmpty)
      return const SizedBox.shrink();
    final l10n = AppLocalizations.of(context)!;
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: AppSpacing.s16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
        side: BorderSide(color: AppColors.intentInfo, width: AppSpacing.s2),
      ),
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.s16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              l10n.systemAuditTrailLabel,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppColors.intentInfo,
              ),
            ),
            AppSpacing.h12,
            XAIEvidenceBox(traces: mcpToolAudit!),
          ],
        ),
      ),
    );
  }

  Widget _buildChartWithTitle(
    BuildContext context,
    I18nText? title,
    Widget chart,
  ) {
    if (title == null) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: AppSpacing.s16),
        child: chart,
      );
    }

    final locale = Localizations.localeOf(context).languageCode;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.s16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            title.get(locale),
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          AppSpacing.h16,
          chart,
        ],
      ),
    );
  }
}
