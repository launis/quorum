import 'package:flutter/material.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';

import 'package:client_app/l10n/gen/app_localizations.dart';

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
    final l10n = AppLocalizations.of(context)!;
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.printableSourcesBlock,
    );

    return BaseBlockCard(
      blockType: TargetBlockType.printableSourcesBlock,
      title: l10n.blockBibliographyTitle,
      subtitle: l10n.blockBibliographySubtitle,
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
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(vertical: AppSpacing.s4),
            child: Text(
              l10n.bibliographyCardHint,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
          AppSpacing.h12,
          Text(
            l10n.sourcesDisplayModeLabel,
            style: Theme.of(
              context,
            ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
          ),
          AppSpacing.h8,
          SegmentedButton<SourcesDisplayMode>(
            segments: [
              ButtonSegment<SourcesDisplayMode>(
                value: SourcesDisplayMode.verifiedEvidence,
                icon: const Icon(Icons.verified_outlined),
                label: Text(l10n.sourcesDisplayModeVerifiedEvidence),
                tooltip: l10n.sourcesDisplayModeVerifiedEvidenceDesc,
              ),
              ButtonSegment<SourcesDisplayMode>(
                value: SourcesDisplayMode.simpleBibliography,
                icon: const Icon(Icons.format_list_bulleted_outlined),
                label: Text(l10n.sourcesDisplayModeSimpleBibliography),
                tooltip: l10n.sourcesDisplayModeSimpleBibliographyDesc,
              ),
            ],
            selected: {payload.sourcesDisplayMode},
            onSelectionChanged: (Set<SourcesDisplayMode> selected) {
              if (selected.isNotEmpty) {
                updatePayload(
                  payload.copyWith(sourcesDisplayMode: selected.first),
                );
              }
            },
          ),
          AppSpacing.h12,
          SwitchListTile.adaptive(
            contentPadding: EdgeInsets.zero,
            dense: true,
            title: Text(
              l10n.showSourcesSummaryBoxLabel,
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
            ),
            subtitle: Text(
              l10n.showSourcesSummaryBoxDesc,
              style: Theme.of(context).textTheme.bodySmall,
            ),
            value: payload.showSourcesSummaryBox,
            onChanged: (bool value) {
              updatePayload(payload.copyWith(showSourcesSummaryBox: value));
            },
          ),
        ],
      ),
    );
  }
}
