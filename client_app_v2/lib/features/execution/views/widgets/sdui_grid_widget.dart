import 'package:flutter/material.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/core/theme/app_spacing.dart';

class SduiGridWidget extends StatelessWidget {
  final SduiGridBlock block;

  const SduiGridWidget({super.key, required this.block});

  @override
  Widget build(BuildContext context) {
    if (block.items.isEmpty) return const SizedBox();

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final halfWidth = (constraints.maxWidth - AppSpacing.s8) / 2;
          return Wrap(
            spacing: AppSpacing.s8,
            runSpacing: AppSpacing.s8,
            children: block.items.map((item) {
              return SizedBox(
                width: halfWidth,
                child: Card(
                  elevation: 0,
                  margin: EdgeInsets.zero,
                  color: Theme.of(
                    context,
                  ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppSpacing.s8),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(AppSpacing.s12),
                    child: OutputRenderer(markdownContent: item),
                  ),
                ),
              );
            }).toList(),
          );
        },
      ),
    );
  }
}
