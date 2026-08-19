import 'package:flutter/material.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';

/// Card for printableSourcesBlock (Bibliography & Sources).
class BibliographyBlockCard extends StatelessWidget {
  final OutputProfile payload;
  final void Function(OutputProfile) updatePayload;
  final Widget? dragHandle;

  const BibliographyBlockCard({
    super.key,
    required this.payload,
    required this.updatePayload,
    this.dragHandle,
  });

  @override
  Widget build(BuildContext context) {
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.printableSourcesBlock,
    );

    return BaseBlockCard(
      blockType: TargetBlockType.printableSourcesBlock,
      title: 'Bibliography & Sources',
      subtitle: 'Printable citations, sources, and verified references section',
      icon: Icons.menu_book_outlined,
      isIncluded: isIncluded,
      dragHandle: dragHandle,
      onToggle: (enabled) {
        final newOrder = List<TargetBlockType>.from(payload.targetBlockOrder);
        if (enabled) {
          if (!newOrder.contains(TargetBlockType.printableSourcesBlock)) {
            newOrder.add(TargetBlockType.printableSourcesBlock);
          }
        } else {
          newOrder.remove(TargetBlockType.printableSourcesBlock);
        }
        updatePayload(payload.copyWith(targetBlockOrder: newOrder));
      },
      body: Padding(
        padding: const EdgeInsets.symmetric(vertical: AppSpacing.s4),
        child: Text(
          'Formatted source document list and exact quote citations will be rendered at the end of the report.',
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ),
    );
  }
}
