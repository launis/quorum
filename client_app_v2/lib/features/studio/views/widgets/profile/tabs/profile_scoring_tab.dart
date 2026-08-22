import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Tab 2: Pure mathematical scoring parameters and scale normalization.
class ProfileScoringTab extends ConsumerWidget {
  final String id;
  const ProfileScoringTab({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(outputProfileFormProvider(id));
    final payload = formState.value;
    if (payload == null) {
      throw StateError(
        'Profile payload must not be null when rendering ProfileScoringTab',
      );
    }

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
                          if (val == DisplayScale.custom) {
                            updatePayload(
                              payload.copyWith(
                                displayScale: val,
                                customScaleMin: payload.customScaleMin ?? 4.0,
                                customScaleMax: payload.customScaleMax ?? 10.0,
                              ),
                            );
                          } else {
                            updatePayload(
                              payload.copyWith(
                                displayScale: val,
                                customScaleMin: null,
                                customScaleMax: null,
                              ),
                            );
                          }
                        }
                      },
                    ),
                  ),
                ),
                if (payload.displayScale == DisplayScale.custom) ...[
                  AppSpacing.h16,
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: TextFormField(
                          initialValue:
                              payload.customScaleMin?.toString() ?? '4.0',
                          keyboardType: const TextInputType.numberWithOptions(
                            decimal: true,
                            signed: true,
                          ),
                          decoration: InputDecoration(
                            labelText: l10n.customScaleMinLabel,
                            isDense: true,
                            border: const OutlineInputBorder(),
                          ),
                          onChanged: (val) {
                            updatePayload(
                              payload.copyWith(
                                customScaleMin: double.tryParse(val.trim()),
                              ),
                            );
                          },
                          validator: (val) {
                            if (payload.displayScale == DisplayScale.custom) {
                              if (val == null || val.trim().isEmpty) {
                                return l10n.fieldRequired;
                              }
                              if (double.tryParse(val.trim()) == null) {
                                return l10n.customScaleInvalidNumber;
                              }
                            }
                            return null;
                          },
                        ),
                      ),
                      AppSpacing.w16,
                      Expanded(
                        child: TextFormField(
                          initialValue:
                              payload.customScaleMax?.toString() ?? '10.0',
                          keyboardType: const TextInputType.numberWithOptions(
                            decimal: true,
                            signed: true,
                          ),
                          decoration: InputDecoration(
                            labelText: l10n.customScaleMaxLabel,
                            isDense: true,
                            border: const OutlineInputBorder(),
                          ),
                          onChanged: (val) {
                            updatePayload(
                              payload.copyWith(
                                customScaleMax: double.tryParse(val.trim()),
                              ),
                            );
                          },
                          validator: (val) {
                            if (payload.displayScale == DisplayScale.custom) {
                              if (val == null || val.trim().isEmpty) {
                                return l10n.fieldRequired;
                              }
                              final parsed = double.tryParse(val.trim());
                              if (parsed == null) {
                                return l10n.customScaleInvalidNumber;
                              }
                              if (payload.customScaleMin != null &&
                                  parsed <= payload.customScaleMin!) {
                                return l10n.customScaleMaxMustBeGreater;
                              }
                            }
                            return null;
                          },
                        ),
                      ),
                    ],
                  ),
                ],
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
              ],
            ),
          ),
        ),
      ],
    );
  }
}
