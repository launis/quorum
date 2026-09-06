import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Config card for executiveSummaryBlock with dedicated synthesis directives and length constraint.
class ExecutiveSummaryBlockCard extends StatelessWidget {
  final OutputProfile payload;
  final void Function(OutputProfile) updatePayload;
  final Widget? dragHandle;

  const ExecutiveSummaryBlockCard({
    super.key,
    required this.payload,
    required this.updatePayload,
    this.dragHandle,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.executiveSummaryBlock,
    );

    return BaseBlockCard(
      blockType: TargetBlockType.executiveSummaryBlock,
      title: l10n.blockExecutiveSummaryTitle,
      subtitle: l10n.blockExecutiveSummarySubtitle,
      icon: Icons.summarize_outlined,
      isIncluded: isIncluded,
      dragHandle: dragHandle,
      onToggle: (enabled) {
        final newOrder = List<TargetBlockType>.from(payload.targetBlockOrder);
        if (enabled) {
          if (!newOrder.contains(TargetBlockType.executiveSummaryBlock)) {
            newOrder.add(TargetBlockType.executiveSummaryBlock);
          }
        } else {
          newOrder.remove(TargetBlockType.executiveSummaryBlock);
        }
        updatePayload(payload.copyWith(targetBlockOrder: newOrder));
      },
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextFormField(
            key: const Key('profile_executive_summary_directive_field'),
            initialValue: payload.executiveSummaryDirective,
            maxLines: 4,
            decoration: InputDecoration(
              labelText: l10n.profileExecutiveSummaryDirectiveLabel,
              border: const OutlineInputBorder(),
            ),
            onChanged: (val) {
              final trimmed = val.trim();
              updatePayload(
                payload.copyWith(
                  executiveSummaryDirective: trimmed.isEmpty ? null : trimmed,
                ),
              );
            },
          ),
          AppSpacing.h16,
          TextFormField(
            initialValue: payload.synthesisLengthConstraint?.toString() ?? '',
            keyboardType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            decoration: InputDecoration(
              labelText: l10n.profileSynthesisLengthLabel,
              hintText: l10n.profileSynthesisLengthHint,
              border: const OutlineInputBorder(),
              isDense: true,
            ),
            onChanged: (val) {
              final trimmed = val.trim();
              updatePayload(
                payload.copyWith(
                  synthesisLengthConstraint: trimmed.isNotEmpty
                      ? int.tryParse(trimmed)
                      : null,
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
