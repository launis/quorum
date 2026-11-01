import 'package:flutter/material.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/features/execution/views/widgets/sdui_blocks_renderer.dart';
import 'package:client_app/core/theme/app_spacing.dart';

class SduiGridWidget extends StatelessWidget {
  final SduiGridBlock block;

  const SduiGridWidget({super.key, required this.block});

  @override
  Widget build(BuildContext context) {
    if (block.items.isEmpty) return const SizedBox();

    final rows = <Widget>[];
    for (var i = 0; i < block.items.length; i += 2) {
      if (i > 0) {
        rows.add(AppSpacing.h8);
      }
      final firstItem = block.items[i];
      final secondItem = i + 1 < block.items.length ? block.items[i + 1] : null;
      rows.add(
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(child: _buildGridCell(context, firstItem)),
            AppSpacing.w8,
            Expanded(
              child: secondItem != null
                  ? _buildGridCell(context, secondItem)
                  : const SizedBox(),
            ),
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: rows,
      ),
    );
  }

  Widget _buildGridCell(BuildContext context, SduiBlockDTO item) {
    return Card(
      elevation: 0,
      margin: EdgeInsets.zero,
      color: Theme.of(
        context,
      ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s8),
      ),
      child: Padding(
        padding: AppSpacing.p12,
        child: SduiBlocksRenderer(blocks: [item]),
      ),
    );
  }
}
