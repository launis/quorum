import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';

class PdfExportGuideDialog extends StatelessWidget {
  const PdfExportGuideDialog({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return AlertDialog(
      titlePadding: AppSpacing.p16,
      contentPadding: const EdgeInsets.symmetric(horizontal: AppSpacing.s16),
      actionsPadding: AppSpacing.p16,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      title: Row(
        children: [
          Icon(
            Icons.menu_book_outlined,
            color: theme.colorScheme.primary,
            size: 24,
          ),
          AppSpacing.w8,
          Expanded(
            child: Text(
              l10n.chatIngressGuideTitle,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 20),
            tooltip: l10n.close,
            mouseCursor: SystemMouseCursors.click,
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
      content: SizedBox(
        width: 620,
        height: 420,
        child: DefaultTabController(
          length: 3,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TabBar(
                labelColor: theme.colorScheme.primary,
                unselectedLabelColor: theme.colorScheme.onSurfaceVariant,
                indicatorColor: theme.colorScheme.primary,
                tabs: [
                  Tab(text: l10n.chatIngressTabChatGpt),
                  Tab(text: l10n.chatIngressTabGemini),
                  Tab(text: l10n.chatIngressTabClaude),
                ],
              ),
              AppSpacing.h16,
              Expanded(
                child: TabBarView(
                  children: [
                    _buildChatGptTab(context, l10n, theme),
                    _buildGeminiTab(context, l10n, theme),
                    _buildClaudeTab(context, l10n, theme),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
      actions: [
        FilledButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(l10n.close),
        ),
      ],
    );
  }

  Widget _buildChatGptTab(
    BuildContext context,
    AppLocalizations l10n,
    ThemeData theme,
  ) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: AppSpacing.p12,
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer.withAlpha(80),
              borderRadius: BorderRadius.circular(AppSpacing.s8),
              border: Border.all(
                color: theme.colorScheme.primary.withAlpha(60),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.recommend_outlined,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.chatGptRecommendedMethod,
                    style: theme.textTheme.labelLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ),
              ],
            ),
          ),
          AppSpacing.h12,
          _buildStepRow(context, l10n.chatGptStep1),
          AppSpacing.h8,
          _buildStepRow(context, l10n.chatGptStep2),
          AppSpacing.h8,
          _buildStepRow(context, l10n.chatGptStep3),
          AppSpacing.h12,
          Container(
            padding: AppSpacing.p12,
            decoration: BoxDecoration(
              color: theme.colorScheme.surfaceContainerHighest.withAlpha(100),
              borderRadius: BorderRadius.circular(AppSpacing.s8),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.check_circle_outline,
                  color: theme.colorScheme.secondary,
                  size: 18,
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.chatGptClipboardBenefit,
                    style: theme.textTheme.bodySmall,
                  ),
                ),
              ],
            ),
          ),
          AppSpacing.h12,
          Container(
            padding: AppSpacing.p12,
            decoration: BoxDecoration(
              color: theme.colorScheme.errorContainer.withAlpha(60),
              borderRadius: BorderRadius.circular(AppSpacing.s8),
              border: Border.all(color: theme.colorScheme.error.withAlpha(100)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.warning_amber_rounded,
                  color: theme.colorScheme.error,
                  size: 20,
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.chatGptPdfWarning,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.error,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGeminiTab(
    BuildContext context,
    AppLocalizations l10n,
    ThemeData theme,
  ) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: AppSpacing.p12,
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer.withAlpha(80),
              borderRadius: BorderRadius.circular(AppSpacing.s8),
              border: Border.all(
                color: theme.colorScheme.primary.withAlpha(60),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.recommend_outlined,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.geminiRecommendedMethod,
                    style: theme.textTheme.labelLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ),
              ],
            ),
          ),
          AppSpacing.h12,
          _buildStepRow(context, l10n.geminiStep1),
          AppSpacing.h8,
          _buildStepRow(context, l10n.geminiStep2),
          AppSpacing.h8,
          _buildStepRow(context, l10n.geminiStep3),
          AppSpacing.h12,
          Container(
            padding: AppSpacing.p12,
            decoration: BoxDecoration(
              color: theme.colorScheme.surfaceContainerHighest.withAlpha(100),
              borderRadius: BorderRadius.circular(AppSpacing.s8),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.verified_outlined,
                  color: theme.colorScheme.primary,
                  size: 18,
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.geminiBenefit,
                    style: theme.textTheme.bodySmall,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildClaudeTab(
    BuildContext context,
    AppLocalizations l10n,
    ThemeData theme,
  ) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: AppSpacing.p12,
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer.withAlpha(80),
              borderRadius: BorderRadius.circular(AppSpacing.s8),
              border: Border.all(
                color: theme.colorScheme.primary.withAlpha(60),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.recommend_outlined,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.claudeRecommendedMethod,
                    style: theme.textTheme.labelLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ),
              ],
            ),
          ),
          AppSpacing.h12,
          _buildStepRow(context, l10n.claudeStep1),
          AppSpacing.h8,
          _buildStepRow(context, l10n.claudeStep2),
        ],
      ),
    );
  }

  Widget _buildStepRow(BuildContext context, String text) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.s4),
      child: Text(text, style: theme.textTheme.bodyMedium),
    );
  }
}
