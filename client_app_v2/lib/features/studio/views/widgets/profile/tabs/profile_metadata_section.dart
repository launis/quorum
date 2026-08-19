import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Section widget for selecting visible identity metadata fields in reports.
class ProfileMetadataSection extends ConsumerWidget {
  final String id;
  const ProfileMetadataSection({super.key, required this.id});

  static const _masterOrder = [
    'date',
    'organization',
    'user',
    'scoring_engine',
    'strictness',
    'cost',
    'tokens',
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(outputProfileFormProvider(id));
    final payload = formState.value;
    if (payload == null) return const SizedBox.shrink();

    void updatePayload(OutputProfile p) {
      ref.read(outputProfileFormProvider(id).notifier).updatePayload(p);
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          l10n.identityMetadataTitle,
          style: Theme.of(context).textTheme.titleSmall,
        ),
        AppSpacing.h8,
        ..._masterOrder.map((meta) {
          final String title = switch (meta) {
            'date' => l10n.metaDate,
            'organization' => l10n.metaOrganization,
            'user' => l10n.metaUser,
            'scoring_engine' => l10n.metaScoringEngine,
            'strictness' => l10n.metaStrictness,
            'cost' => l10n.metaCost,
            'tokens' => l10n.metaTokens,
            _ => meta,
          };
          return CheckboxListTile(
            title: Text(title),
            value: payload.visibleMetadata.contains(meta),
            onChanged: (val) {
              final list = List<String>.from(payload.visibleMetadata);
              if (val == true) {
                if (!list.contains(meta)) list.add(meta);
              } else {
                list.remove(meta);
              }
              list.sort(
                (a, b) => _masterOrder
                    .indexOf(a)
                    .compareTo(_masterOrder.indexOf(b)),
              );
              updatePayload(payload.copyWith(visibleMetadata: list));
            },
            controlAffinity: ListTileControlAffinity.leading,
          );
        }),
      ],
    );
  }
}
