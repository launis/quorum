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
    return AppErrorBoundary(
      child: Builder(
        builder: (context) {
          final theme = Theme.of(context);
          final colorScheme = theme.colorScheme;
          final textTheme = theme.textTheme;
          final langCode = Localizations.localeOf(context).languageCode;
          final summaryText = block.summary.get(langCode);

          return Container(
            margin: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
            padding: AppSpacing.p12,
            decoration: BoxDecoration(
              color: colorScheme.surfaceContainerLow,
              borderRadius: BorderRadius.circular(AppSpacing.s8),
              border: Border.all(color: colorScheme.outlineVariant),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.hub_outlined,
                      color: colorScheme.primary,
                      size: AppSpacing.s24,
                    ),
                    AppSpacing.w8,
                    Expanded(
                      child: Text(
                        summaryText,
                        style: textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: colorScheme.onSurface,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    AppSpacing.w8,
                    Flexible(
                      child: Container(
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
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ),
                    AppSpacing.w8,
                    Flexible(
                      child: OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          visualDensity: VisualDensity.compact,
                          padding: const EdgeInsets.symmetric(
                            horizontal: AppSpacing.s8,
                            vertical: AppSpacing.s4,
                          ),
                        ),
                        icon: const Icon(
                          Icons.fullscreen,
                          size: AppSpacing.s16,
                        ),
                        label: Text(
                          AppLocalizations.of(context)!.causalInspectorTitle,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        onPressed: () => showDialog<void>(
                          context: context,
                          builder: (ctx) => CausalInspectorModal(block: block),
                        ),
                      ),
                    ),
                  ],
                ),
                // Phase 3, Step 3.3: Render inline short-circuit blocker chips and Toulmin falsification badges
                if (block.shortCircuitedByClaims.any(
                  (c) => c.trim().isNotEmpty,
                )) ...[
                  AppSpacing.h8,
                  ...block.shortCircuitedByClaims
                      .map((c) => c.trim())
                      .where((c) => c.isNotEmpty)
                      .toSet()
                      .map(
                        (claim) => Padding(
                          padding: const EdgeInsets.only(bottom: AppSpacing.s4),
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: AppSpacing.s8,
                              vertical: AppSpacing.s4,
                            ),
                            decoration: BoxDecoration(
                              color: colorScheme.errorContainer,
                              borderRadius: BorderRadius.circular(
                                AppSpacing.s4,
                              ),
                              border: Border.all(color: colorScheme.error),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  Icons.block,
                                  size: AppSpacing.s16,
                                  color: colorScheme.onErrorContainer,
                                ),
                                AppSpacing.w8,
                                Expanded(
                                  child: Text(
                                    claim,
                                    style: textTheme.bodySmall?.copyWith(
                                      color: colorScheme.onErrorContainer,
                                    ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                ],
                if (block.falsifiedWarrantClaims.any(
                  (c) => c.trim().isNotEmpty,
                )) ...[
                  AppSpacing.h8,
                  ...block.falsifiedWarrantClaims
                      .map((c) => c.trim())
                      .where((c) => c.isNotEmpty)
                      .toSet()
                      .map(
                        (claim) => Padding(
                          padding: const EdgeInsets.only(bottom: AppSpacing.s4),
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: AppSpacing.s8,
                              vertical: AppSpacing.s4,
                            ),
                            decoration: BoxDecoration(
                              color: colorScheme.tertiaryContainer,
                              borderRadius: BorderRadius.circular(
                                AppSpacing.s4,
                              ),
                              border: Border.all(color: colorScheme.tertiary),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  Icons.gavel,
                                  size: AppSpacing.s16,
                                  color: colorScheme.onTertiaryContainer,
                                ),
                                AppSpacing.w8,
                                Expanded(
                                  child: Text(
                                    claim,
                                    style: textTheme.bodySmall?.copyWith(
                                      color: colorScheme.onTertiaryContainer,
                                    ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }
}
