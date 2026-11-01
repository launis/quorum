import 'package:flutter/material.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/scale_editor_modal.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// **Desktop-First V2 BARS Matrix Builder**
/// Interactive layout to build evaluation matrices.
/// Complies with Macro-Breakpoint Three-Pane rule and handles deep atomization scales.
class BarsMatrixBuilder extends StatelessWidget {
  final List<MatrixScale> scales;
  final void Function(List<MatrixScale>) onChanged;

  static const double _desktopBreakpoint = 1200.0;
  static const double _tabletBreakpoint = 800.0;
  static const double _minScaleCardWidth = 240.0;
  static const double _maxScaleCardWidth = 320.0;
  static const double _maxAtomChipWidth = 150.0;

  const BarsMatrixBuilder({
    super.key,
    required this.scales,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    // Use pure native flex constraints!
    return LayoutBuilder(
      builder: (context, constraints) {
        // Sort the scales ascending by score
        final sortedScales = List<MatrixScale>.from(scales)
          ..sort((a, b) => a.score.compareTo(b.score));

        Widget content;
        if (constraints.maxWidth >= _desktopBreakpoint) {
          if (sortedScales.length <= 5) {
            content = Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: sortedScales
                  .map(
                    (s) => Expanded(child: _buildScaleCard(context, l10n, s)),
                  )
                  .toList(),
            );
          } else {
            content = SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: sortedScales
                    .map(
                      (s) => ConstrainedBox(
                        constraints: const BoxConstraints(
                          minWidth: _minScaleCardWidth,
                          maxWidth: _maxScaleCardWidth,
                        ),
                        child: _buildScaleCard(context, l10n, s),
                      ),
                    )
                    .toList(),
              ),
            );
          }
        } else if (constraints.maxWidth >= _tabletBreakpoint) {
          content = SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: sortedScales
                  .map(
                    (s) => ConstrainedBox(
                      constraints: const BoxConstraints(
                        minWidth: _minScaleCardWidth,
                        maxWidth: _maxScaleCardWidth,
                      ),
                      child: _buildScaleCard(context, l10n, s),
                    ),
                  )
                  .toList(),
            ),
          );
        } else {
          content = Column(
            children: sortedScales
                .map((s) => _buildScaleCard(context, l10n, s))
                .toList(),
          );
        }

        return Container(
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            borderRadius: BorderRadius.circular(AppSpacing.s12),
            border: Border.all(
              color: Theme.of(context).colorScheme.outlineVariant,
            ),
          ),
          clipBehavior: Clip.antiAlias,
          child: content,
        );
      },
    );
  }

  Widget _buildScaleCard(
    BuildContext context,
    AppLocalizations l10n,
    MatrixScale scale,
  ) {
    final theme = Theme.of(context);
    final gradeName = scale.name != null
        ? scale.name!.get(Localizations.localeOf(context).languageCode)
        : '';

    return Card(
      margin: AppSpacing.p8,
      elevation: 0,
      color: theme.colorScheme.surfaceContainerHighest,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        side: BorderSide(color: theme.colorScheme.outlineVariant),
      ),
      child: InkWell(
        onTap: () => _editScale(context, scale),
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        child: Padding(
          padding: AppSpacing.p12,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min, // To allow Row stretch gracefully
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      l10n.gradeScoreLabel(
                        scale.score.toString(),
                        gradeName.isNotEmpty ? "- $gradeName" : "",
                      ),
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  IconButton(
                    icon: Icon(
                      Icons.edit,
                      size: AppSpacing.s16 + AppSpacing.s4,
                      color: theme.colorScheme.primary,
                    ),
                    onPressed: () => _editScale(context, scale),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                  AppSpacing.w8,
                  IconButton(
                    icon: Icon(
                      Icons.delete,
                      size: AppSpacing.s16 + AppSpacing.s4,
                      color: theme.colorScheme.error,
                    ),
                    onPressed: () => _deleteScale(scale),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ],
              ),
              const Divider(),
              if (scale.aiLabel.isNotEmpty) ...[
                Text(
                  l10n.barsMatrixAiPrefix(scale.aiLabel),
                  style: theme.textTheme.labelMedium?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.w600,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                AppSpacing.h8,
              ],
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: scale.claims.length,
                separatorBuilder: (context, _) => AppSpacing.h8,
                itemBuilder: (context, idx) {
                  final claim = scale.claims[idx];
                  final labelTrans = claim.label.get(
                    Localizations.localeOf(context).languageCode,
                  );
                  return Container(
                    padding: AppSpacing.p8,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surface,
                      borderRadius: BorderRadius.circular(AppSpacing.s4),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          labelTrans,
                          style: theme.textTheme.bodyMedium,
                          maxLines: 4,
                          overflow: TextOverflow.ellipsis,
                        ),
                        if (claim.tdaAssertions.isNotEmpty) ...[
                          AppSpacing.h4,
                          Text(
                            claim.tdaAssertions.first.conceptDescription,
                            style: theme.textTheme.labelSmall?.copyWith(
                              fontStyle: FontStyle.italic,
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          AppSpacing.h4,
                          Wrap(
                            spacing: AppSpacing.s4,
                            runSpacing: AppSpacing.s4,
                            children: [
                              ...claim.tdaAssertions
                                  .take(3)
                                  .map(
                                    (atom) => Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: AppSpacing.s4,
                                        vertical: AppSpacing.s2,
                                      ),
                                      decoration: BoxDecoration(
                                        color: atom.inverseEvidence
                                            ? theme.colorScheme.errorContainer
                                            : theme
                                                  .colorScheme
                                                  .tertiaryContainer,
                                        borderRadius: BorderRadius.circular(
                                          AppSpacing.s4,
                                        ),
                                      ),
                                      child: Tooltip(
                                        message: atom.conceptDescription,
                                        child: ConstrainedBox(
                                          constraints: const BoxConstraints(
                                            maxWidth: _maxAtomChipWidth,
                                          ),
                                          child: Text(
                                            atom.conceptDescription,
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                            style: theme.textTheme.labelSmall
                                                ?.copyWith(
                                                  color: atom.inverseEvidence
                                                      ? theme
                                                            .colorScheme
                                                            .onErrorContainer
                                                      : theme
                                                            .colorScheme
                                                            .onTertiaryContainer,
                                                ),
                                          ),
                                        ),
                                      ),
                                    ),
                                  ),
                              if (claim.tdaAssertions.length > 3)
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: AppSpacing.s4,
                                    vertical: AppSpacing.s2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: theme
                                        .colorScheme
                                        .surfaceContainerHighest,
                                    borderRadius: BorderRadius.circular(
                                      AppSpacing.s4,
                                    ),
                                  ),
                                  child: Text(
                                    l10n.barsMatrixMoreAssertions(
                                      claim.tdaAssertions.length - 3,
                                    ),
                                    style: theme.textTheme.labelSmall?.copyWith(
                                      color: theme.colorScheme.onSurfaceVariant,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        ],
                      ],
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _editScale(BuildContext context, MatrixScale scale) async {
    final result = await showDialog<MatrixScale>(
      context: context,
      builder: (ctx) => ScaleEditorModal(initialScale: scale),
    );
    if (result != null) {
      final idx = scales.indexWhere(
        (s) => s.score == scale.score && s.aiLabel == scale.aiLabel,
      );
      if (idx >= 0) {
        final newList = List<MatrixScale>.from(scales);
        newList[idx] = result;
        onChanged(newList);
      }
    }
  }

  void _deleteScale(MatrixScale scale) {
    final idx = scales.indexWhere(
      (s) => s.score == scale.score && s.aiLabel == scale.aiLabel,
    );
    if (idx >= 0) {
      final newList = List<MatrixScale>.from(scales)..removeAt(idx);
      onChanged(newList);
    }
  }
}
