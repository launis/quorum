import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/execution/views/widgets/sdui_blocks_renderer.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Renders a server-driven execution report payload via polymorphic SDUI blocks.
class ReportRendererV2Widget extends StatelessWidget {
  final ReportDataDto payload;
  final String executionId;

  const ReportRendererV2Widget({
    super.key,
    required this.payload,
    required this.executionId,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;
    final widgets = <Widget>[];

    if (payload.innerSduiBlocks.isNotEmpty) {
      widgets.add(
        Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.s24,
            vertical: AppSpacing.s8,
          ),
          child: AppErrorBoundary(
            child: SduiBlocksRenderer(
              blocks: payload.innerSduiBlocks,
              mcpToolAudit: payload.mcpToolAudit,
            ),
          ),
        ),
      );
    } else {
      widgets.add(
        Container(
          margin: const EdgeInsets.symmetric(
            horizontal: AppSpacing.s24,
            vertical: AppSpacing.s16,
          ),
          padding: AppSpacing.p16,
          decoration: BoxDecoration(
            color: colorScheme.errorContainer,
            border: Border(
              left: BorderSide(color: colorScheme.error, width: AppSpacing.s4),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.error_outline,
                    color: colorScheme.onErrorContainer,
                    size: AppSpacing.s24,
                  ),
                  AppSpacing.w8,
                  Expanded(
                    child: Text(
                      l10n.sharedNoReportData,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.titleLarge?.copyWith(
                        color: colorScheme.onErrorContainer,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              AppSpacing.h8,
              Text(
                l10n.reportEmptyProfile,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: colorScheme.onErrorContainer,
                ),
              ),
            ],
          ),
        ),
      );
    }

    return ListView(
      padding: EdgeInsets.zero,
      shrinkWrap: true,
      primary: false,
      children: widgets,
    );
  }
}
