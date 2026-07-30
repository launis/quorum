import 'package:flutter/material.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:client_app/features/execution/views/widgets/sdui_alert_box_widget.dart';
import 'package:client_app/features/execution/views/widgets/sdui_grid_widget.dart';

class SduiBlocksRenderer extends StatelessWidget {
  final List<SduiBlockDTO> blocks;

  const SduiBlocksRenderer({super.key, required this.blocks});

  @override
  Widget build(BuildContext context) {
    if (blocks.isEmpty) return const SizedBox();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: blocks.map((block) {
        if (block is SduiAccordionBlock) {
          return _buildAccordion(context, block);
        }
        if (block is SduiHeaderBlock) {
          return _buildHeader(context, block);
        }
        if (block is SduiAlertBoxBlock) {
          return SduiAlertBoxWidget(block: block);
        }
        if (block is SduiGridBlock) {
          return SduiGridWidget(block: block);
        }

        String? text;
        if (block is SduiMarkdownBlock) {
          text = block.text;
        } else if (block is SduiParagraphBlock) {
          text = block.text;
        }

        if (text != null && text.isNotEmpty) {
          return Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.s8),
            child: OutputRenderer(markdownContent: text),
          );
        }
        return const SizedBox();
      }).toList(),
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

  Widget _buildHeader(BuildContext context, SduiHeaderBlock block) {
    final theme = Theme.of(context);
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
                            'Meta Costs',
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
                            'Meta Tokens',
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
}
