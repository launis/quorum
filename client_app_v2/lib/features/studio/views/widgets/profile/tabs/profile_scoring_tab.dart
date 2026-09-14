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
              ],
            ),
          ),
        ),
        AppSpacing.h16,
        Card(
          child: Padding(
            padding: AppSpacing.p16,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        l10n.strictnessSliderHeader,
                        style: Theme.of(context).textTheme.titleSmall,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.primaryContainer,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        '${payload.strictnessLevel}%',
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: Theme.of(
                            context,
                          ).colorScheme.onPrimaryContainer,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                AppSpacing.h12,
                Wrap(
                  spacing: AppSpacing.s8,
                  runSpacing: AppSpacing.s4,
                  children:
                      [
                        (0, l10n.strictnessPresetFree),
                        (50, l10n.strictnessPresetNormal),
                        (85, l10n.strictnessPresetStrict),
                        (100, l10n.strictnessPresetAbsolute),
                      ].map((preset) {
                        final (val, label) = preset;
                        return ChoiceChip(
                          label: Text(label),
                          selected: payload.strictnessLevel == val,
                          onSelected: (selected) {
                            if (selected) {
                              updatePayload(
                                payload.copyWith(strictnessLevel: val),
                              );
                            }
                          },
                        );
                      }).toList(),
                ),
                AppSpacing.h8,
                Slider(
                  value: payload.strictnessLevel.toDouble(),
                  min: 0,
                  max: 100,
                  divisions: 100,
                  label: '${payload.strictnessLevel}%',
                  semanticFormatterCallback: (val) =>
                      l10n.strictnessSliderSemanticLabel(val.round()),
                  onChanged: (val) => updatePayload(
                    payload.copyWith(strictnessLevel: val.round()),
                  ),
                ),
                AppSpacing.h8,
                Builder(
                  builder: (context) {
                    final level = payload.strictnessLevel;
                    final Color consequenceBgColor;
                    final Color consequenceTextColor;
                    final IconData consequenceIcon;
                    final String consequenceDescription;

                    if (level == 0) {
                      consequenceBgColor = Theme.of(
                        context,
                      ).colorScheme.tertiaryContainer;
                      consequenceTextColor = Theme.of(
                        context,
                      ).colorScheme.onTertiaryContainer;
                      consequenceIcon = Icons.info_outline;
                      consequenceDescription = l10n.strictnessConsequenceFree;
                    } else if (level <= 50) {
                      consequenceBgColor = Theme.of(
                        context,
                      ).colorScheme.primaryContainer;
                      consequenceTextColor = Theme.of(
                        context,
                      ).colorScheme.onPrimaryContainer;
                      consequenceIcon = Icons.check_circle_outline;
                      consequenceDescription = l10n.strictnessConsequenceNormal;
                    } else if (level <= 85) {
                      consequenceBgColor = Theme.of(
                        context,
                      ).colorScheme.secondaryContainer;
                      consequenceTextColor = Theme.of(
                        context,
                      ).colorScheme.onSecondaryContainer;
                      consequenceIcon = Icons.shield_outlined;
                      consequenceDescription = l10n.strictnessConsequenceStrict;
                    } else {
                      consequenceBgColor = Theme.of(
                        context,
                      ).colorScheme.errorContainer;
                      consequenceTextColor = Theme.of(
                        context,
                      ).colorScheme.onErrorContainer;
                      consequenceIcon = Icons.warning_amber_rounded;
                      consequenceDescription =
                          l10n.strictnessConsequenceAbsolute;
                    }

                    return Card(
                      color: consequenceBgColor,
                      elevation: 0,
                      child: Padding(
                        padding: AppSpacing.p12,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  consequenceIcon,
                                  size: 16,
                                  color: consequenceTextColor,
                                ),
                                AppSpacing.w8,
                                Expanded(
                                  child: Text(
                                    l10n.strictnessConsequenceTitle,
                                    style: Theme.of(context)
                                        .textTheme
                                        .labelMedium
                                        ?.copyWith(
                                          color: consequenceTextColor,
                                          fontWeight: FontWeight.bold,
                                        ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                            AppSpacing.h4,
                            Text(
                              consequenceDescription,
                              style: Theme.of(context).textTheme.bodySmall
                                  ?.copyWith(color: consequenceTextColor),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
        AppSpacing.h16,
        Card(
          child: Padding(
            padding: AppSpacing.p16,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  l10n.penaltiesSectionTitle,
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                AppSpacing.h16,
                TextFormField(
                  initialValue: (payload.securityPenalty * 100).toStringAsFixed(
                    payload.securityPenalty * 100 ==
                            (payload.securityPenalty * 100).roundToDouble()
                        ? 0
                        : 1,
                  ),
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: InputDecoration(
                    labelText: l10n.penaltySecurityLabel,
                    isDense: true,
                    border: const OutlineInputBorder(),
                    suffixText: '%',
                  ),
                  onChanged: (val) {
                    if (val.trim().isEmpty) {
                      updatePayload(payload.copyWith(securityPenalty: 0.0));
                      return;
                    }
                    final parsed = double.tryParse(val.trim());
                    if (parsed != null && parsed >= 0.0 && parsed <= 100.0) {
                      updatePayload(
                        payload.copyWith(securityPenalty: parsed / 100.0),
                      );
                    }
                  },
                ),
                AppSpacing.h16,
                TextFormField(
                  initialValue: (payload.postHocPenalty * 100).toStringAsFixed(
                    payload.postHocPenalty * 100 ==
                            (payload.postHocPenalty * 100).roundToDouble()
                        ? 0
                        : 1,
                  ),
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: InputDecoration(
                    labelText: l10n.penaltyPostHocLabel,
                    isDense: true,
                    border: const OutlineInputBorder(),
                    suffixText: '%',
                  ),
                  onChanged: (val) {
                    if (val.trim().isEmpty) {
                      updatePayload(payload.copyWith(postHocPenalty: 0.0));
                      return;
                    }
                    final parsed = double.tryParse(val.trim());
                    if (parsed != null && parsed >= 0.0 && parsed <= 100.0) {
                      updatePayload(
                        payload.copyWith(postHocPenalty: parsed / 100.0),
                      );
                    }
                  },
                ),
                AppSpacing.h16,
                TextFormField(
                  initialValue: (payload.passivityPenalty * 100)
                      .toStringAsFixed(
                        payload.passivityPenalty * 100 ==
                                (payload.passivityPenalty * 100).roundToDouble()
                            ? 0
                            : 1,
                      ),
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: InputDecoration(
                    labelText: l10n.penaltyPassivityLabel,
                    isDense: true,
                    border: const OutlineInputBorder(),
                    suffixText: '%',
                  ),
                  onChanged: (val) {
                    if (val.trim().isEmpty) {
                      updatePayload(payload.copyWith(passivityPenalty: 0.0));
                      return;
                    }
                    final parsed = double.tryParse(val.trim());
                    if (parsed != null && parsed >= 0.0 && parsed <= 100.0) {
                      updatePayload(
                        payload.copyWith(passivityPenalty: parsed / 100.0),
                      );
                    }
                  },
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
