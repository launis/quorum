import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/tabs/profile_metadata_section.dart';
import 'package:client_app/features/studio/views/widgets/profile/tabs/profile_xai_extensions_section.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Tab 2: Scoring strategy, scale normalization, identity metadata, and XAI extensions.
class ProfileScoringTab extends ConsumerWidget {
  final String id;
  const ProfileScoringTab({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(outputProfileFormProvider(id));
    final payload = formState.value;
    if (payload == null) return const SizedBox.shrink();

    void updatePayload(OutputProfile p) {
      ref.read(outputProfileFormProvider(id).notifier).updatePayload(p);
    }

    return ListView(
      padding: AppSpacing.p16,
      children: [
        Card(
          child: Padding(
            padding: AppSpacing.p16,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                InputDecorator(
                  decoration: InputDecoration(
                    labelText: l10n.profileDisplayScaleLabel,
                    isDense: true,
                    border: const OutlineInputBorder(),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<DisplayScale>(
                      value: payload.displayScale,
                      isDense: true,
                      isExpanded: true,
                      items: [
                        DropdownMenuItem(
                          value: DisplayScale.original,
                          child: Text(
                            l10n.displayScaleOriginal,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        DropdownMenuItem(
                          value: DisplayScale.custom,
                          child: Text(
                            l10n.displayScaleCustom,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        DropdownMenuItem(
                          value: DisplayScale.normalized100,
                          child: Text(
                            l10n.displayScaleNormalized100,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                      onChanged: (val) {
                        if (val != null) {
                          updatePayload(payload.copyWith(displayScale: val));
                        }
                      },
                    ),
                  ),
                ),
                AppSpacing.h24,
                Text(
                  l10n.scoringEngineTitle,
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                AppSpacing.h8,
                InputDecorator(
                  decoration: InputDecoration(
                    labelText: l10n.strictnessSelectorTitle,
                    isDense: true,
                    border: const OutlineInputBorder(),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<int>(
                      value:
                          payload.strictnessLevel ??
                          StrictnessLevel.balanced.value,
                      isDense: true,
                      isExpanded: true,
                      items: StrictnessLevel.values.map((lvl) {
                        return DropdownMenuItem<int>(
                          value: lvl.value,
                          child: Text(switch (lvl) {
                            StrictnessLevel.fullFlexibility =>
                              l10n.strictnessFullFlex,
                            StrictnessLevel.lenient => l10n.strictnessLenient,
                            StrictnessLevel.balanced => l10n.strictnessBalanced,
                            StrictnessLevel.strict => l10n.strictnessStrict,
                            StrictnessLevel.absolute => l10n.strictnessAbsolute,
                          }, overflow: TextOverflow.ellipsis),
                        );
                      }).toList(),
                      onChanged: (val) {
                        updatePayload(payload.copyWith(strictnessLevel: val));
                      },
                    ),
                  ),
                ),
                AppSpacing.h16,
                InputDecorator(
                  decoration: InputDecoration(
                    labelText: l10n.analysisLevelLabel,
                    isDense: true,
                    border: const OutlineInputBorder(),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<ScoringStrategy?>(
                      value: payload.scoringStrategy,
                      isDense: true,
                      isExpanded: true,
                      items: [
                        DropdownMenuItem<ScoringStrategy?>(
                          value: null,
                          child: Text(
                            l10n.noneDefaultLabel,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        ...ScoringStrategy.values.map((strategy) {
                          return DropdownMenuItem<ScoringStrategy?>(
                            value: strategy,
                            child: Text(switch (strategy) {
                              ScoringStrategy.waterfall =>
                                l10n.strategyKoearvostelu,
                              ScoringStrategy.average =>
                                l10n.strategyLineaarinenKeskiarvo,
                              ScoringStrategy.weightedAverage =>
                                l10n.strategyPainotettuKeskiarvo,
                              ScoringStrategy.pureMath =>
                                l10n.strategyPuhdasMatematiikka,
                            }, overflow: TextOverflow.ellipsis),
                          );
                        }),
                      ],
                      onChanged: (val) {
                        updatePayload(payload.copyWith(scoringStrategy: val));
                      },
                    ),
                  ),
                ),
                AppSpacing.h24,
                ProfileMetadataSection(id: id),
                AppSpacing.h16,
                TextFormField(
                  initialValue: payload.maxExtensionItems.toString(),
                  decoration: InputDecoration(
                    labelText: l10n.maxExtensionItemsLabel,
                    border: const OutlineInputBorder(),
                    helperText: l10n.maxExtensionItemsHelper,
                  ),
                  keyboardType: TextInputType.number,
                  onChanged: (val) {
                    final parsed = int.tryParse(val);
                    if (parsed != null && parsed >= 1 && parsed <= 100) {
                      updatePayload(
                        payload.copyWith(maxExtensionItems: parsed),
                      );
                    }
                  },
                  validator: (val) {
                    if (val == null || val.isEmpty) return null;
                    final parsed = int.tryParse(val);
                    if (parsed == null || parsed < 1 || parsed > 100) {
                      return l10n.extensionItemsMustBeIntError;
                    }
                    return null;
                  },
                ),
                AppSpacing.h24,
                ProfileXaiExtensionsSection(id: id),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
