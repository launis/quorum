import 'package:flutter/material.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';

/// Reusable baseline card for pure-computed blocks that require only the
/// Universal Baseline Toggle switch without nested configuration.
class SimpleToggleBlockCard extends StatelessWidget {
  final TargetBlockType blockType;
  final String title;
  final String subtitle;
  final IconData icon;
  final OutputProfile payload;
  final void Function(OutputProfile) updatePayload;
  final Widget? dragHandle;

  const SimpleToggleBlockCard({
    super.key,
    required this.blockType,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.payload,
    required this.updatePayload,
    this.dragHandle,
  });

  @override
  Widget build(BuildContext context) {
    final isIncluded = payload.targetBlockOrder.contains(blockType);

    return BaseBlockCard(
      blockType: blockType,
      title: title,
      subtitle: subtitle,
      icon: icon,
      isIncluded: isIncluded,
      dragHandle: dragHandle,
      onToggle: (enabled) {
        final newOrder = List<TargetBlockType>.from(payload.targetBlockOrder);
        if (enabled) {
          if (!newOrder.contains(blockType)) {
            newOrder.add(blockType);
          }
        } else {
          newOrder.remove(blockType);
        }
        updatePayload(payload.copyWith(targetBlockOrder: newOrder));
      },
    );
  }
}
