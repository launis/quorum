import 'package:flutter/material.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/scale_editor_modal.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// **Desktop-First V2 BARS Matrix Builder**
/// Interactive layout to build 5-portainen (1-5) evaluation matrices.
/// Complies with Macro-Breakpoint Three-Pane rule and handles deep atomization scales.
class BarsMatrixBuilder extends StatelessWidget {
  final List<MatrixScale> scales;
  final void Function(List<MatrixScale>) onChanged;

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
        // Evaluate the Macro-Breakpoint Desktop-First responsiveness
        final isDesktop =
            constraints.maxWidth >=
            800; // >=800 enables Split-Screen or Three-Pane

        // Sort the scales to always process 1 -> 5
        final sortedScales = List<MatrixScale>.from(scales)
          ..sort((a, b) => a.score.compareTo(b.score));

        return Container(
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: Theme.of(context).colorScheme.outlineVariant,
            ),
          ),
          clipBehavior: Clip.antiAlias,
          child: InteractiveViewer(
            panEnabled: !isDesktop, // Allow panning tightly nested forms
            scaleEnabled: false,
            child: isDesktop
                ? Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: sortedScales
                        .map(
                          (s) => Expanded(
                            child: _buildScaleCard(context, l10n, s),
                          ),
                        )
                        .toList(),
                  )
                : Column(
                    children: sortedScales
                        .map((s) => _buildScaleCard(context, l10n, s))
                        .toList(),
                  ),
          ),
        );
      },
    );
  }

  Widget _buildScaleCard(
    BuildContext context,
    AppLocalizations l10n,
    MatrixScale scale,
  ) {
    final gradeName = scale.name != null
        ? scale.name!.translations[scale.name!.defaultLocale] ??
              scale.name!.defaultLocale
        : '';

    return Card(
      margin: const EdgeInsets.all(8.0),
      elevation: 0,
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(color: Theme.of(context).colorScheme.outlineVariant),
      ),
      child: InkWell(
        onTap: () => _editScale(context, scale),
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
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
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  IconButton(
                    icon: Icon(
                      Icons.edit,
                      size: 20,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    onPressed: () => _editScale(context, scale),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: Icon(
                      Icons.delete,
                      size: 20,
                      color: Theme.of(context).colorScheme.error,
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
                  "AI: ${scale.aiLabel}",
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 8),
              ],
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: scale.claims.length,
                separatorBuilder: (context, _) => const SizedBox(height: 8),
                itemBuilder: (context, idx) {
                  final claim = scale.claims[idx];
                  final labelTrans =
                      claim.label.translations[claim.label.defaultLocale] ??
                      claim.label.defaultLocale;
                  return Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surface,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          labelTrans,
                          style: const TextStyle(fontSize: 13),
                          maxLines: 4,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          claim.aiDescription,
                          style: TextStyle(
                            fontSize: 11,
                            color: Theme.of(
                              context,
                            ).colorScheme.onSurfaceVariant,
                            fontStyle: FontStyle.italic,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        if (claim.tdaAssertions.isNotEmpty) ...[
                          const SizedBox(height: 4),
                          Wrap(
                            spacing: 4,
                            runSpacing: 4,
                            children: [
                              ...claim.tdaAssertions
                                  .take(3)
                                  .map(
                                    (atom) => Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 4,
                                        vertical: 2,
                                      ),
                                      decoration: BoxDecoration(
                                        color: atom.inverseEvidence
                                            ? Theme.of(
                                                context,
                                              ).colorScheme.errorContainer
                                            : Theme.of(
                                                context,
                                              ).colorScheme.tertiaryContainer,
                                        borderRadius: BorderRadius.circular(4),
                                      ),
                                      child: Tooltip(
                                        message: atom.conceptDescription,
                                        child: ConstrainedBox(
                                          constraints: const BoxConstraints(
                                            maxWidth: 150,
                                          ),
                                          child: Text(
                                            atom.conceptDescription,
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                            style: TextStyle(
                                              fontSize: 9,
                                              color: atom.inverseEvidence
                                                  ? Theme.of(context)
                                                        .colorScheme
                                                        .onErrorContainer
                                                  : Theme.of(context)
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
                                    horizontal: 4,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.surfaceContainerHighest,
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    "+ ${claim.tdaAssertions.length - 3} lisää",
                                    style: TextStyle(
                                      fontSize: 9,
                                      color: Theme.of(
                                        context,
                                      ).colorScheme.onSurfaceVariant,
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
