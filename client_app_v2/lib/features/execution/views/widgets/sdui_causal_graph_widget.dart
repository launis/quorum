import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/execution/presentation/causal_inspector_modal.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Server-driven UI widget rendering the compact Causal Inspector action card.
///
/// In the main UI stream, displays a compact single-row header containing
/// the summary, intact status badge, and an inspector button that launches
/// [CausalInspectorModal] for full interactive causal exploration.
/// Adheres strictly to Flutter Theme Sovereignty.
class SduiCausalGraphWidget extends StatelessWidget {
  final SduiCausalGraphBlock block;

  const SduiCausalGraphWidget({super.key, required this.block});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final langCode = Localizations.localeOf(context).languageCode;
    final summaryText = block.summary.get(langCode);

    return AppErrorBoundary(
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
        padding: const EdgeInsets.all(AppSpacing.s12),
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainerLow,
          borderRadius: BorderRadius.circular(AppSpacing.s8),
          border: Border.all(color: colorScheme.outlineVariant),
        ),
        child: Row(
          children: [
            Icon(Icons.hub_outlined, color: colorScheme.primary, size: 20),
            AppSpacing.w8,
            Expanded(
              child: Text(
                summaryText.isNotEmpty
                    ? summaryText
                    : 'Causal Discovery & Fault Analysis',
                style: textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: colorScheme.onSurface,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
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
                  color: colorScheme.primary.withValues(alpha: 0.2),
                ),
              ),
              child: Text(
                '${block.intactClaimsCount} / ${block.totalClaimsCount} Intact',
                style: textTheme.labelSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: colorScheme.onPrimaryContainer,
                ),
              ),
            ),
            AppSpacing.w8,
            OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                visualDensity: VisualDensity.compact,
                padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.s8,
                  vertical: AppSpacing.s4,
                ),
              ),
              icon: const Icon(Icons.fullscreen, size: 16),
              label: Text(AppLocalizations.of(context)!.causalInspectorTitle),
              onPressed: () => showDialog<void>(
                context: context,
                builder: (ctx) => CausalInspectorModal(block: block),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
