import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';

/// Card widget displaying a materialized report artifact in the master list or grid.
class ReportArtifactCard extends StatelessWidget {
  final ReportArtifactSummary report;
  final bool isSelected;
  final VoidCallback? onSelect;
  final VoidCallback? onDownloadPdf;
  final VoidCallback? onDownloadExcel;
  final VoidCallback? onDownloadCsv;
  final VoidCallback? onRegenerate;
  final VoidCallback? onDelete;

  const ReportArtifactCard({
    super.key,
    required this.report,
    this.isSelected = false,
    this.onSelect,
    this.onDownloadPdf,
    this.onDownloadExcel,
    this.onDownloadCsv,
    this.onRegenerate,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;

    final (badgeColor, badgeTextColor, statusLabel) = switch (report.status) {
      ReportStatus.ready => (
        colorScheme.primaryContainer,
        colorScheme.onPrimaryContainer,
        l10n.reportStatusReady,
      ),
      ReportStatus.generating => (
        colorScheme.tertiaryContainer,
        colorScheme.onTertiaryContainer,
        l10n.reportStatusGenerating,
      ),
      ReportStatus.pending => (
        colorScheme.surfaceContainerHigh,
        colorScheme.onSurfaceVariant,
        l10n.reportStatusPending,
      ),
      ReportStatus.failed => (
        colorScheme.errorContainer,
        colorScheme.onErrorContainer,
        l10n.reportStatusFailed,
      ),
    };

    return AppErrorBoundary(
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        child: Card(
          elevation: isSelected ? 4 : 1,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: isSelected
                ? BorderSide(color: colorScheme.primary, width: 2)
                : BorderSide(
                    color: colorScheme.outlineVariant.withValues(alpha: 0.5),
                  ),
          ),
          color: isSelected
              ? colorScheme.primaryContainer.withValues(alpha: 0.15)
              : colorScheme.surface,
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: onSelect,
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.s12,
                vertical: AppSpacing.s8,
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Row(
                          children: [
                            Flexible(
                              flex: 3,
                              fit: FlexFit.loose,
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 6,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: badgeColor,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  statusLabel,
                                  style: theme.textTheme.labelSmall?.copyWith(
                                    color: badgeTextColor,
                                    fontWeight: FontWeight.bold,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ),
                            AppSpacing.w4,
                            Flexible(
                              flex: 1,
                              fit: FlexFit.loose,
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 4,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: colorScheme.surfaceContainerHigh,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  report.locale.toUpperCase(),
                                  style: theme.textTheme.labelSmall?.copyWith(
                                    color: colorScheme.onSurfaceVariant,
                                    fontWeight: FontWeight.w600,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ),
                            AppSpacing.w4,
                            Expanded(
                              flex: 2,
                              child: Text(
                                report.id,
                                style: theme.textTheme.labelSmall?.copyWith(
                                  color: colorScheme.outline,
                                  fontFamily: 'monospace',
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                        AppSpacing.h8,
                        Text(
                          report.title,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: isSelected
                                ? FontWeight.bold
                                : FontWeight.w600,
                            color: isSelected
                                ? colorScheme.primary
                                : colorScheme.onSurface,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  AppSpacing.w8,
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (onDownloadPdf != null &&
                          report.status == ReportStatus.ready)
                        IconButton(
                          icon: const Icon(Icons.picture_as_pdf_outlined),
                          iconSize: 18,
                          style: IconButton.styleFrom(
                            visualDensity: VisualDensity.compact,
                            padding: EdgeInsets.zero,
                            minimumSize: const Size(26, 26),
                            maximumSize: const Size(26, 26),
                            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                          ),
                          tooltip: l10n.downloadPdfTooltip,
                          mouseCursor: SystemMouseCursors.click,
                          onPressed: onDownloadPdf,
                        ),
                      if (onDownloadExcel != null &&
                          report.status == ReportStatus.ready)
                        IconButton(
                          icon: const Icon(Icons.table_chart_outlined),
                          iconSize: 18,
                          style: IconButton.styleFrom(
                            visualDensity: VisualDensity.compact,
                            padding: EdgeInsets.zero,
                            minimumSize: const Size(26, 26),
                            maximumSize: const Size(26, 26),
                            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                          ),
                          tooltip: l10n.downloadExcelTooltip,
                          mouseCursor: SystemMouseCursors.click,
                          onPressed: onDownloadExcel,
                        ),
                      if (onDownloadCsv != null &&
                          report.status == ReportStatus.ready)
                        IconButton(
                          icon: const Icon(Icons.description_outlined),
                          iconSize: 18,
                          style: IconButton.styleFrom(
                            visualDensity: VisualDensity.compact,
                            padding: EdgeInsets.zero,
                            minimumSize: const Size(26, 26),
                            maximumSize: const Size(26, 26),
                            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                          ),
                          tooltip: l10n.downloadCsvTooltip,
                          mouseCursor: SystemMouseCursors.click,
                          onPressed: onDownloadCsv,
                        ),
                      if (onRegenerate != null &&
                          report.status != ReportStatus.generating)
                        IconButton(
                          icon: const Icon(Icons.refresh),
                          iconSize: 18,
                          style: IconButton.styleFrom(
                            visualDensity: VisualDensity.compact,
                            padding: EdgeInsets.zero,
                            minimumSize: const Size(26, 26),
                            maximumSize: const Size(26, 26),
                            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                          ),
                          tooltip: l10n.regenerateReportTooltip,
                          mouseCursor: SystemMouseCursors.click,
                          onPressed: onRegenerate,
                        ),
                      if (onDelete != null)
                        IconButton(
                          icon: Icon(
                            Icons.delete_outline,
                            color: colorScheme.error,
                          ),
                          iconSize: 18,
                          style: IconButton.styleFrom(
                            visualDensity: VisualDensity.compact,
                            padding: EdgeInsets.zero,
                            minimumSize: const Size(26, 26),
                            maximumSize: const Size(26, 26),
                            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                          ),
                          tooltip: l10n.deleteReportTooltip,
                          mouseCursor: SystemMouseCursors.click,
                          onPressed: () => _confirmDelete(context),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _confirmDelete(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    showDialog<bool>(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        title: Text(l10n.deleteReportConfirmTitle),
        content: Text(l10n.deleteReportConfirmMessage),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogCtx).pop(false),
            child: Text(l10n.discardButtonLabel),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(dialogCtx).colorScheme.error,
              foregroundColor: Theme.of(dialogCtx).colorScheme.onError,
            ),
            onPressed: () {
              Navigator.of(dialogCtx).pop(true);
              onDelete?.call();
            },
            child: Text(l10n.deleteReportTooltip),
          ),
        ],
      ),
    );
  }
}
