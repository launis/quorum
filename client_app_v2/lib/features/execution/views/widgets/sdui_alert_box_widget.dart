import 'package:flutter/material.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:client_app/core/models/enums.dart';

class SduiAlertBoxWidget extends StatelessWidget {
  final SduiAlertBoxBlock block;

  const SduiAlertBoxWidget({super.key, required this.block});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    Color borderColor;
    Color bgColor;
    IconData icon;

    switch (block.severity) {
      case AlertSeverity.success:
        borderColor = AppColors.intentSuccess;
        bgColor = AppColors.intentSuccess.withValues(alpha: 0.1);
        icon = Icons.check_circle_outline;
        break;
      case AlertSeverity.warning:
        borderColor = AppColors.intentWarning;
        bgColor = AppColors.intentWarning.withValues(alpha: 0.1);
        icon = Icons.warning_amber_rounded;
        break;
      case AlertSeverity.criticalOverride:
      case AlertSeverity.error:
        borderColor = theme.colorScheme.error;
        bgColor = theme.colorScheme.errorContainer;
        icon = Icons.error_outline;
        break;
      case AlertSeverity.info:
        borderColor = AppColors.intentInfo;
        bgColor = AppColors.intentInfo.withValues(alpha: 0.1);
        icon = Icons.info_outline;
        break;
    }

    return Container(
      margin: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
      padding: const EdgeInsets.all(AppSpacing.s12),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        border: Border(
          left: BorderSide(color: borderColor, width: AppSpacing.s4),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: borderColor, size: 24),
          AppSpacing.w8,
          Expanded(child: OutputRenderer(markdownContent: block.text)),
        ],
      ),
    );
  }
}
