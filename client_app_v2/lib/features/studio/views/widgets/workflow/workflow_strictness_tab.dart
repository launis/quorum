import 'package:flutter/material.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// **WorkflowStrictnessTab**
///
/// Componentized UI widget representing Tab 4 of the Workflow Builder.
/// Governs sovereign evaluation strictness (0–100 continuous slider, preset chips,
/// and dynamic semantic consequence card) anchored at the workflow definition level.
class WorkflowStrictnessTab extends StatelessWidget {
  final Workflow workflow;
  final Function(Workflow) onChanged;

  const WorkflowStrictnessTab({
    super.key,
    required this.workflow,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return SingleChildScrollView(
      padding: AppSpacing.p16,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
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
                          '${workflow.defaultStrictnessLevel}%',
                          style: Theme.of(context).textTheme.labelSmall
                              ?.copyWith(
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
                            selected: workflow.defaultStrictnessLevel == val,
                            onSelected: (selected) {
                              if (selected) {
                                onChanged(
                                  workflow.copyWith(
                                    defaultStrictnessLevel: val,
                                  ),
                                );
                              }
                            },
                          );
                        }).toList(),
                  ),
                  AppSpacing.h8,
                  Slider(
                    value: workflow.defaultStrictnessLevel.toDouble(),
                    min: 0,
                    max: 100,
                    divisions: 100,
                    label: '${workflow.defaultStrictnessLevel}%',
                    semanticFormatterCallback: (val) =>
                        l10n.strictnessSliderSemanticLabel(val.round()),
                    onChanged: (val) => onChanged(
                      workflow.copyWith(defaultStrictnessLevel: val.round()),
                    ),
                  ),
                  AppSpacing.h8,
                  Builder(
                    builder: (context) {
                      final level = workflow.defaultStrictnessLevel;
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
                        consequenceDescription =
                            l10n.strictnessConsequenceNormal;
                      } else if (level <= 85) {
                        consequenceBgColor = Theme.of(
                          context,
                        ).colorScheme.secondaryContainer;
                        consequenceTextColor = Theme.of(
                          context,
                        ).colorScheme.onSecondaryContainer;
                        consequenceIcon = Icons.shield_outlined;
                        consequenceDescription =
                            l10n.strictnessConsequenceStrict;
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
                    initialValue: (workflow.securityPenalty * 100)
                        .toStringAsFixed(
                          workflow.securityPenalty * 100 ==
                                  (workflow.securityPenalty * 100)
                                      .roundToDouble()
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
                        onChanged(workflow.copyWith(securityPenalty: 0.0));
                        return;
                      }
                      final parsed = double.tryParse(val.trim());
                      if (parsed != null && parsed >= 0.0 && parsed <= 100.0) {
                        onChanged(
                          workflow.copyWith(securityPenalty: parsed / 100.0),
                        );
                      }
                    },
                  ),
                  AppSpacing.h16,
                  TextFormField(
                    initialValue: (workflow.postHocPenalty * 100)
                        .toStringAsFixed(
                          workflow.postHocPenalty * 100 ==
                                  (workflow.postHocPenalty * 100)
                                      .roundToDouble()
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
                        onChanged(workflow.copyWith(postHocPenalty: 0.0));
                        return;
                      }
                      final parsed = double.tryParse(val.trim());
                      if (parsed != null && parsed >= 0.0 && parsed <= 100.0) {
                        onChanged(
                          workflow.copyWith(postHocPenalty: parsed / 100.0),
                        );
                      }
                    },
                  ),
                  AppSpacing.h16,
                  TextFormField(
                    initialValue: (workflow.passivityPenalty * 100)
                        .toStringAsFixed(
                          workflow.passivityPenalty * 100 ==
                                  (workflow.passivityPenalty * 100)
                                      .roundToDouble()
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
                        onChanged(workflow.copyWith(passivityPenalty: 0.0));
                        return;
                      }
                      final parsed = double.tryParse(val.trim());
                      if (parsed != null && parsed >= 0.0 && parsed <= 100.0) {
                        onChanged(
                          workflow.copyWith(passivityPenalty: parsed / 100.0),
                        );
                      }
                    },
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
