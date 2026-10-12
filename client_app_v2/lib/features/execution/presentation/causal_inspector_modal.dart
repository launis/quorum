import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/execution/models/causal_discovery_dto.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Modal dialog providing desktop-class pro-tool interactive inspection of causal discovery graphs.
///
/// Features pan/zoom navigation via [InteractiveViewer], node selection, citation exploration,
/// and prescriptive remediation simulation with 100% Theme Sovereignty compliance.
class CausalInspectorModal extends StatefulWidget {
  final SduiCausalGraphBlock block;

  const CausalInspectorModal({super.key, required this.block});

  @override
  State<CausalInspectorModal> createState() => _CausalInspectorModalState();
}

class _CausalInspectorModalState extends State<CausalInspectorModal> {
  String? _selectedNodeId;

  @override
  void initState() {
    super.initState();
    if (widget.block.criticalPathNodes.isNotEmpty) {
      final failingNode = widget.block.criticalPathNodes.firstWhere(
        (n) => n.status != ExecutionStatus.passed,
        orElse: () => widget.block.criticalPathNodes.first,
      );
      _selectedNodeId = failingNode.nodeId;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final semanticColors = context.semanticColors;
    final langCode = Localizations.localeOf(context).languageCode;
    final summaryText = widget.block.summary.get(langCode);

    final selectedNode = _findNode(_selectedNodeId);

    return AppErrorBoundary(
      child: Dialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.s12),
        ),
        backgroundColor: colorScheme.surface,
        surfaceTintColor: colorScheme.surfaceTint,
        child: Container(
          constraints: const BoxConstraints(maxWidth: 1100, maxHeight: 750),
          padding: const EdgeInsets.all(AppSpacing.s16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildHeader(
                context,
                summaryText,
                colorScheme,
                textTheme,
                semanticColors,
              ),
              AppSpacing.h12,
              Expanded(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Expanded(
                      flex: 6,
                      child: _buildGraphCanvas(
                        context,
                        colorScheme,
                        textTheme,
                        semanticColors,
                      ),
                    ),
                    AppSpacing.w16,
                    Expanded(
                      flex: 4,
                      child: _buildDetailPanel(
                        context,
                        selectedNode,
                        colorScheme,
                        textTheme,
                        semanticColors,
                      ),
                    ),
                  ],
                ),
              ),
              AppSpacing.h12,
              _buildFooter(context, colorScheme, textTheme, semanticColors),
            ],
          ),
        ),
      ),
    );
  }

  CausalNodeDto? _findNode(String? nodeId) {
    if (nodeId == null) return null;
    for (final node in widget.block.criticalPathNodes) {
      if (node.nodeId == nodeId) return node;
    }
    return null;
  }

  Widget _buildHeader(
    BuildContext context,
    String summaryText,
    ColorScheme colorScheme,
    TextTheme textTheme,
    AppSemanticColors semanticColors,
  ) {
    return Row(
      children: [
        Icon(Icons.hub_outlined, color: colorScheme.primary, size: 24),
        AppSpacing.w8,
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                AppLocalizations.of(context)!.causalInspectorTitle,
                style: textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: colorScheme.onSurface,
                ),
              ),
              if (summaryText.isNotEmpty)
                Text(
                  summaryText,
                  style: textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
            ],
          ),
        ),
        AppSpacing.w8,
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.s8,
            vertical: AppSpacing.s4,
          ),
          decoration: BoxDecoration(
            color: colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(AppSpacing.s12),
            border: Border.all(
              color: colorScheme.primary.withValues(alpha: 0.3),
            ),
          ),
          child: Text(
            '${widget.block.intactClaimsCount} / ${widget.block.totalClaimsCount} Intact',
            style: textTheme.labelSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: colorScheme.onPrimaryContainer,
            ),
          ),
        ),
        AppSpacing.w8,
        IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.of(context).pop(),
          tooltip: 'Close',
        ),
      ],
    );
  }

  Widget _buildGraphCanvas(
    BuildContext context,
    ColorScheme colorScheme,
    TextTheme textTheme,
    AppSemanticColors semanticColors,
  ) {
    return Container(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        border: Border.all(color: colorScheme.outlineVariant),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        child: InteractiveViewer(
          boundaryMargin: const EdgeInsets.all(AppSpacing.s24),
          minScale: 0.5,
          maxScale: 2.5,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.s16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'CRITICAL CAUSAL PATH & DEPENDENCIES',
                  style: textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    letterSpacing: 0.8,
                    color: colorScheme.primary,
                  ),
                ),
                AppSpacing.h12,
                if (widget.block.criticalPathNodes.isEmpty)
                  Padding(
                    padding: const EdgeInsets.all(AppSpacing.s16),
                    child: Text(
                      'No critical path nodes discovered in this execution.',
                      style: textTheme.bodySmall?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                  )
                else
                  ...widget.block.criticalPathNodes.asMap().entries.map((
                    entry,
                  ) {
                    final index = entry.key;
                    final node = entry.value;
                    final isSelected = node.nodeId == _selectedNodeId;
                    final isPassed = node.status == ExecutionStatus.passed;
                    final isLast =
                        index == widget.block.criticalPathNodes.length - 1;

                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        MouseRegion(
                          cursor: SystemMouseCursors.click,
                          child: GestureDetector(
                            onTap: () {
                              setState(() {
                                _selectedNodeId = node.nodeId;
                              });
                            },
                            child: Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(AppSpacing.s12),
                              decoration: BoxDecoration(
                                color: isSelected
                                    ? colorScheme.secondaryContainer.withValues(
                                        alpha: 0.4,
                                      )
                                    : colorScheme.surfaceContainerLow,
                                borderRadius: BorderRadius.circular(
                                  AppSpacing.s8,
                                ),
                                border: Border.all(
                                  color: isSelected
                                      ? colorScheme.primary
                                      : isPassed
                                      ? colorScheme.outlineVariant
                                      : colorScheme.error.withValues(
                                          alpha: 0.5,
                                        ),
                                  width: isSelected ? 2.0 : 1.0,
                                ),
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: AppSpacing.s6,
                                      vertical: AppSpacing.s2,
                                    ),
                                    decoration: BoxDecoration(
                                      color: isPassed
                                          ? colorScheme.primaryContainer
                                          : colorScheme.errorContainer,
                                      borderRadius: BorderRadius.circular(
                                        AppSpacing.s4,
                                      ),
                                    ),
                                    child: Text(
                                      node.nodeId,
                                      style: textTheme.labelSmall?.copyWith(
                                        fontWeight: FontWeight.bold,
                                        color: isPassed
                                            ? colorScheme.onPrimaryContainer
                                            : colorScheme.onErrorContainer,
                                      ),
                                    ),
                                  ),
                                  AppSpacing.w8,
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          node.claim,
                                          style: textTheme.bodySmall?.copyWith(
                                            fontWeight: FontWeight.w600,
                                            color: colorScheme.onSurface,
                                          ),
                                        ),
                                        if (node.paragraphRef != null &&
                                            node.paragraphRef!.isNotEmpty) ...[
                                          AppSpacing.h4,
                                          Text(
                                            'Ref: ${node.paragraphRef}',
                                            style: textTheme.labelSmall
                                                ?.copyWith(
                                                  color: colorScheme
                                                      .onSurfaceVariant,
                                                ),
                                          ),
                                        ],
                                      ],
                                    ),
                                  ),
                                  AppSpacing.w8,
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: AppSpacing.s6,
                                      vertical: AppSpacing.s2,
                                    ),
                                    decoration: BoxDecoration(
                                      color: isPassed
                                          ? colorScheme.primaryContainer
                                                .withValues(alpha: 0.5)
                                          : colorScheme.errorContainer
                                                .withValues(alpha: 0.5),
                                      borderRadius: BorderRadius.circular(
                                        AppSpacing.s4,
                                      ),
                                    ),
                                    child: Text(
                                      isPassed ? 'PASSED' : 'FAULT',
                                      style: textTheme.labelSmall?.copyWith(
                                        fontWeight: FontWeight.bold,
                                        color: isPassed
                                            ? colorScheme.primary
                                            : colorScheme.error,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                        if (!isLast) ...[
                          Padding(
                            padding: const EdgeInsets.only(
                              left: AppSpacing.s24,
                              top: AppSpacing.s4,
                              bottom: AppSpacing.s4,
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  Icons.arrow_downward,
                                  size: 16,
                                  color: colorScheme.outline,
                                ),
                                AppSpacing.w8,
                                Text(
                                  'causal fault propagation',
                                  style: textTheme.labelSmall?.copyWith(
                                    color: colorScheme.outline,
                                    fontStyle: FontStyle.italic,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ],
                    );
                  }),
                if (widget.block.criticalEdges.isNotEmpty) ...[
                  AppSpacing.h16,
                  Text(
                    'CRITICAL CAUSAL EDGES',
                    style: textTheme.labelSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.8,
                      color: colorScheme.secondary,
                    ),
                  ),
                  AppSpacing.h8,
                  ...widget.block.criticalEdges.map(
                    (edge) => Container(
                      margin: const EdgeInsets.only(bottom: AppSpacing.s6),
                      padding: const EdgeInsets.all(AppSpacing.s8),
                      decoration: BoxDecoration(
                        color: colorScheme.surfaceContainerLow,
                        borderRadius: BorderRadius.circular(AppSpacing.s4),
                        border: Border.all(color: colorScheme.outlineVariant),
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${edge.sourceId} → ${edge.targetId}',
                            style: textTheme.labelSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: colorScheme.primary,
                            ),
                          ),
                          AppSpacing.w8,
                          Expanded(
                            child: Text(
                              edge.reasoning,
                              style: textTheme.bodySmall?.copyWith(
                                color: colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildDetailPanel(
    BuildContext context,
    CausalNodeDto? node,
    ColorScheme colorScheme,
    TextTheme textTheme,
    AppSemanticColors semanticColors,
  ) {
    return Container(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        border: Border.all(color: colorScheme.outlineVariant),
      ),
      padding: const EdgeInsets.all(AppSpacing.s12),
      child: node == null
          ? Center(
              child: Text(
                'Select a node to inspect citations and remediations.',
                style: textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
            )
          : SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: AppSpacing.s6,
                          vertical: AppSpacing.s2,
                        ),
                        decoration: BoxDecoration(
                          color: colorScheme.primaryContainer,
                          borderRadius: BorderRadius.circular(AppSpacing.s4),
                        ),
                        child: Text(
                          node.nodeId,
                          style: textTheme.labelSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: colorScheme.onPrimaryContainer,
                          ),
                        ),
                      ),
                      AppSpacing.w8,
                      Expanded(
                        child: Text(
                          'Node Details',
                          style: textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: colorScheme.onSurface,
                          ),
                        ),
                      ),
                    ],
                  ),
                  AppSpacing.h8,
                  Text(
                    node.claim,
                    style: textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurface,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  if (node.sourceQuote != null &&
                      node.sourceQuote!.isNotEmpty) ...[
                    AppSpacing.h12,
                    Text(
                      'CITATION EVIDENCE',
                      style: textTheme.labelSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        letterSpacing: 0.6,
                        color: colorScheme.secondary,
                      ),
                    ),
                    AppSpacing.h4,
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(AppSpacing.s8),
                      decoration: BoxDecoration(
                        color: colorScheme.surfaceContainerHighest.withValues(
                          alpha: 0.4,
                        ),
                        borderRadius: BorderRadius.circular(AppSpacing.s4),
                        border: Border(
                          left: BorderSide(
                            color: colorScheme.secondary,
                            width: AppSpacing.s2,
                          ),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '"${node.sourceQuote}"',
                            style: textTheme.bodySmall?.copyWith(
                              fontStyle: FontStyle.italic,
                              color: colorScheme.onSurface,
                            ),
                          ),
                          if (node.paragraphRef != null &&
                              node.paragraphRef!.isNotEmpty) ...[
                            AppSpacing.h4,
                            Text(
                              'Location: ${node.paragraphRef}',
                              style: textTheme.labelSmall?.copyWith(
                                color: colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                  ..._buildMatchingDiagnoses(
                    node.nodeId,
                    colorScheme,
                    textTheme,
                  ),
                  ..._buildMatchingRemediations(
                    node.nodeId,
                    colorScheme,
                    textTheme,
                  ),
                ],
              ),
            ),
    );
  }

  List<Widget> _buildMatchingDiagnoses(
    String nodeId,
    ColorScheme colorScheme,
    TextTheme textTheme,
  ) {
    final matches = widget.block.rootCauseDiagnoses
        .where(
          (d) => d.failingNodeId == nodeId || d.rootCauseParentId == nodeId,
        )
        .toList();

    if (matches.isEmpty) return const [];

    return [
      AppSpacing.h12,
      Text(
        'ROOT CAUSE DIAGNOSIS',
        style: textTheme.labelSmall?.copyWith(
          fontWeight: FontWeight.bold,
          letterSpacing: 0.6,
          color: colorScheme.error,
        ),
      ),
      AppSpacing.h4,
      ...matches.map(
        (diag) => Container(
          margin: const EdgeInsets.only(bottom: AppSpacing.s6),
          padding: const EdgeInsets.all(AppSpacing.s8),
          decoration: BoxDecoration(
            color: colorScheme.errorContainer.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(AppSpacing.s4),
            border: Border(
              left: BorderSide(color: colorScheme.error, width: AppSpacing.s2),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Fault Chain: ${diag.rootCauseParentId} → ${diag.failingNodeId}',
                style: textTheme.labelSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: colorScheme.error,
                ),
              ),
              AppSpacing.h2,
              Text(
                diag.explanation,
                style: textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurface,
                ),
              ),
              if (diag.penaltyPoints > 0) ...[
                AppSpacing.h4,
                Text(
                  'Penalty Attribution: -${diag.penaltyPoints.toStringAsFixed(1)} pts',
                  style: textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: colorScheme.error,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    ];
  }

  List<Widget> _buildMatchingRemediations(
    String nodeId,
    ColorScheme colorScheme,
    TextTheme textTheme,
  ) {
    final matches = widget.block.prescriptiveRemediations
        .where((r) => r.targetNodeId == nodeId)
        .toList();

    if (matches.isEmpty) return const [];

    return [
      AppSpacing.h12,
      Text(
        'REMEDIATION SIMULATION',
        style: textTheme.labelSmall?.copyWith(
          fontWeight: FontWeight.bold,
          letterSpacing: 0.6,
          color: colorScheme.primary,
        ),
      ),
      AppSpacing.h4,
      ...matches.map(
        (rem) => Container(
          margin: const EdgeInsets.only(bottom: AppSpacing.s6),
          padding: const EdgeInsets.all(AppSpacing.s8),
          decoration: BoxDecoration(
            color: colorScheme.primaryContainer.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(AppSpacing.s4),
            border: Border(
              left: BorderSide(
                color: colorScheme.primary,
                width: AppSpacing.s2,
              ),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                rem.requiredAction,
                style: textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: colorScheme.onSurface,
                ),
              ),
              if (rem.unlocksNodeIds.isNotEmpty) ...[
                AppSpacing.h4,
                Text(
                  'Unlocks downstream: ${rem.unlocksNodeIds.join(", ")}',
                  style: textTheme.labelSmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
              if (rem.potentialScoreImpact > 0) ...[
                AppSpacing.h4,
                Text(
                  'Potential Recovery: +${rem.potentialScoreImpact.toStringAsFixed(1)} pts',
                  style: textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: colorScheme.primary,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    ];
  }

  Widget _buildFooter(
    BuildContext context,
    ColorScheme colorScheme,
    TextTheme textTheme,
    AppSemanticColors semanticColors,
  ) {
    final fairScoring = widget.block.fairScoring;
    final antiFluff = widget.block.antiFluffAudit;

    return Container(
      padding: const EdgeInsets.all(AppSpacing.s8),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppSpacing.s6),
        border: Border.all(color: colorScheme.outlineVariant),
      ),
      child: Row(
        children: [
          Icon(Icons.balance, size: 16, color: colorScheme.primary),
          AppSpacing.w8,
          Expanded(
            child: fairScoring != null
                ? Text(
                    'Fair Scoring: ${fairScoring.independentErrorCount} independent, ${fairScoring.cascadingFaultCount} cascading | Deduplicated: -${fairScoring.deduplicatedPenaltyPoints.toStringAsFixed(1)} pts (saved ${fairScoring.dampenedSavingsPoints.toStringAsFixed(1)} pts)',
                    style: textTheme.labelSmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                    overflow: TextOverflow.ellipsis,
                  )
                : Text(
                    'Cohesion Score: ${(antiFluff.logicalCohesionScore * 100).toStringAsFixed(0)}% | Unsupported Claims: ${antiFluff.unsupportedClaimsCount}',
                    style: textTheme.labelSmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
          ),
          AppSpacing.w8,
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(AppLocalizations.of(context)!.close),
          ),
        ],
      ),
    );
  }
}
