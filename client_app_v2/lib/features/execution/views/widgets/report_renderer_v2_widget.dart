import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/execution/views/widgets/sdui_blocks_renderer.dart';

// Phase 3, Step 2: Create ReportRendererV2Widget
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
    final widgets = <Widget>[];

    // 1. Inner SDUI Blocks (Polymorphic SDUI Parity)
    if (payload.innerSduiBlocks.isNotEmpty) {
      widgets.add(
        Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.s24,
            vertical: AppSpacing.s8,
          ),
          child: SduiBlocksRenderer(
            blocks: payload.innerSduiBlocks,
            mcpToolAudit: payload.mcpToolAudit,
          ),
        ),
      );
    } else {
      // V2 ARCHITECTURE VIOLATION fallback
      widgets.add(
        Container(
          margin: const EdgeInsets.symmetric(
            horizontal: AppSpacing.s24,
            vertical: AppSpacing.s16,
          ),
          padding: const EdgeInsets.all(AppSpacing.s16),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.errorContainer,
            border: Border(
              left: BorderSide(
                color: Theme.of(context).colorScheme.error,
                width: 4,
              ),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'V2 ARCHITECTURE VIOLATION',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: Theme.of(context).colorScheme.onErrorContainer,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: AppSpacing.s8),
              Text(
                'FAIL-FAST MANDATE: This execution lacks explicit ReportDataDTO mapping securely populated from backend APIs.',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onErrorContainer,
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
