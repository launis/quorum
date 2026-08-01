import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
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
    final l10n = AppLocalizations.of(context)!;
    final locale = Localizations.localeOf(context).languageCode;
    final widgets = <Widget>[];

    // 0. Top Titles (Profile Name & Description)
    final profileName = payload.profileName?.get(locale);
    if (profileName != null && profileName.isNotEmpty) {
      widgets.add(
        Padding(
          padding: const EdgeInsets.fromLTRB(
            AppSpacing.s24,
            AppSpacing.s24,
            AppSpacing.s24,
            AppSpacing.s8,
          ),
          child: Text(
            profileName,
            style: Theme.of(
              context,
            ).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
        ),
      );
    }

    final profileDescription = payload.profileDescription?.get(locale);
    if (profileDescription != null && profileDescription.isNotEmpty) {
      widgets.add(
        Padding(
          padding: const EdgeInsets.fromLTRB(
            AppSpacing.s24,
            0,
            AppSpacing.s24,
            AppSpacing.s16,
          ),
          child: Text(
            profileDescription,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ),
      );
    }

    // 0.5 Cover Metadata
    if (payload.visibleMetadata.isNotEmpty) {
      final metaItems = <Widget>[];
      for (final meta in payload.visibleMetadata) {
        String? label;
        String? value;
        switch (meta) {
          case 'date':
            label = l10n.metaDate.split(' (')[0];
            value = payload.localTimeStr ?? payload.createdAt;
            break;
          case 'organization':
            label = l10n.metaOrganization.split(' (')[0];
            value = payload.orgName;
            break;
          case 'user':
            label = l10n.metaUser.split(' (')[0];
            value = payload.userName;
            break;
          case 'scoring_engine':
            label = l10n.metaScoringEngine.split(' (')[0];
            value = payload.scoringEngineName;
            break;
          case 'strictness':
            label = l10n.metaStrictness.split(' (')[0];
            value = payload.strictnessLevel?.toString();
            break;
          case 'cost':
            label = l10n.metaCost.split(' (')[0];
            value = payload.costEstimate != null
                ? '\$${payload.costEstimate!.toStringAsFixed(4)}'
                : null;
            break;
          case 'tokens':
            label = l10n.metaTokens.split(' (')[0];
            value = payload.totalTokens?.toString();
            break;
        }

        if (label != null && value != null && value.isNotEmpty) {
          metaItems.add(
            Padding(
              padding: const EdgeInsets.only(
                right: AppSpacing.s16,
                bottom: AppSpacing.s8,
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '$label: ',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).colorScheme.outline,
                    ),
                  ),
                  Text(
                    value,
                    style: const TextStyle(fontWeight: FontWeight.w500),
                  ),
                ],
              ),
            ),
          );
        }
      }

      if (metaItems.isNotEmpty) {
        widgets.add(
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.s24,
              vertical: AppSpacing.s8,
            ),
            child: Wrap(children: metaItems),
          ),
        );
      }
    }

    // 1. Inner SDUI Blocks (e.g. Header)
    if (payload.innerSduiBlocks.isNotEmpty) {
      widgets.add(
        Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.s24,
            vertical: AppSpacing.s8,
          ),
          child: SduiBlocksRenderer(blocks: payload.innerSduiBlocks),
        ),
      );
    }

    // 2. Global Score
    if (payload.globalScore != null) {
      widgets.add(
        Container(
          margin: const EdgeInsets.symmetric(
            horizontal: AppSpacing.s24,
            vertical: AppSpacing.s16,
          ),
          padding: const EdgeInsets.all(AppSpacing.s16),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(AppSpacing.s8),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l10n.scorecard_global_average,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                '${payload.globalScore!.toStringAsFixed(2)}/100',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      );
    }

    // 3. Layouts removed per Phase 3

    if (widgets.isEmpty) {
      return const SizedBox();
    }

    return ListView(
      padding: EdgeInsets.zero,
      shrinkWrap: true,
      primary: false,
      children: widgets,
    );
  }
}
