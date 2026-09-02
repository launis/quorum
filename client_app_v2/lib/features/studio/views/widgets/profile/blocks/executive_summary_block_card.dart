import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
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
          I18nTextField(
            label: l10n.profileExecutiveSummaryDirectiveLabel,
            initialData: payload.executiveSummaryDirective,
            onChanged: (val) {
              final isEmpty =
                  val.translations.isEmpty ||
                  val.translations.values.every((v) => v.trim().isEmpty);
              updatePayload(
                payload.copyWith(
                  executiveSummaryDirective: isEmpty ? null : val,
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
              hintText: 'esim. 1000 merkkiä',
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
