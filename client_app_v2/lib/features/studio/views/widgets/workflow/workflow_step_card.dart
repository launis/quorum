import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';

/// **WorkflowStepCard**
///
/// Componentized UI widget representing a single execution step node
/// inside the workflow builder. Enforces the 3-Zone Architecture:
/// - Zone A: Input Processing (Step 1)
/// - Zone B: Dynamic Specialists (Steps 2..N)
/// - Zone C: Pipeline Funnel Anchors (Steps N+1..N+3)
///
/// Enforces Opaque Stripe IDs and protects System Core steps from deletion.
class WorkflowStepCard extends StatelessWidget {
  final int index;
  final StepRule stepDef;
  final List<NodeStrategy> blueprints;
  final List<StepRule> allSteps;
  final List<Map<String, dynamic>> mcpGateways;
  final List<ExpectedInput> globalWorkflowInputs;
  final AppLocalizations l10n;
  final Function(StepRule) onChanged;
  final VoidCallback onDelete;

  const WorkflowStepCard({
    super.key,
    required this.index,
    required this.stepDef,
    required this.blueprints,
    required this.allSteps,
    required this.mcpGateways,
    required this.globalWorkflowInputs,
    required this.l10n,
    required this.onChanged,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final stepIdStr = stepDef.id;
    final locale = Localizations.localeOf(context).languageCode;

    final currentBlueprint = blueprints
        .where((b) => b.id == stepDef.taskBlueprint)
        .firstOrNull;

    final bool isSystemCoreStep =
        index == 0 || (currentBlueprint?.isSystemCore ?? false);
    final bool isZoneA = index == 0;
    final bool isZoneC = index > 0 && isSystemCoreStep;

    final previousSteps = allSteps
        .map((s) => s.id)
        .where((id) => id.isNotEmpty && id != stepIdStr)
        .toList();

    final dependsOn = List<String>.from(stepDef.dependsOn);
    final mappings = Map<String, String>.from(stepDef.inputMappings);

    String getBlueprintLabel(String stepId) {
      if (stepId.isEmpty) return '';
      final bp = blueprints.firstWhere(
        (b) => b.id == stepId,
        orElse: () => const NodeStrategy.logic(
          id: '',
          slug: '',
          hook: '',
          name: I18nText(translations: {'en': ''}),
        ),
      );
      if (bp.id.isNotEmpty) {
        final label = bp.name.get(locale);
        return label.isNotEmpty ? label : bp.slug;
      }
      return stepId;
    }

    void update(StepRule updated) {
      onChanged(updated);
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header Row: Step Count + Delete Action (if not protected)
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Text(
                      l10n.studioWorkflowStepCount(index + 1),
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    if (isSystemCoreStep) ...[
                      const SizedBox(width: 8),
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
                          l10n.studioSystemCoreBadge,
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: Theme.of(
                              context,
                            ).colorScheme.onPrimaryContainer,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                if (!isSystemCoreStep)
                  IconButton(
                    icon: Icon(
                      Icons.delete,
                      color: Theme.of(context).colorScheme.error,
                    ),
                    onPressed: onDelete,
                  ),
              ],
            ),
            const Divider(),

            // ID & Blueprint Row
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.studioWorkflowNodeIdOpaque,
                        style: TextStyle(
                          fontSize: 12,
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                      ),
                      const SizedBox(height: 4),
                      SelectableText(
                        stepIdStr,
                        style: const TextStyle(
                          fontFamily: 'monospace',
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: isSystemCoreStep
                      ? Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              l10n.studioWorkflowTaskProfileTitle,
                              style: TextStyle(
                                fontSize: 12,
                                color: Theme.of(
                                  context,
                                ).colorScheme.onSurfaceVariant,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              getBlueprintLabel(stepDef.taskBlueprint),
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        )
                      : DropdownButtonFormField<String>(
                          isExpanded: true,
                          decoration: InputDecoration(
                            labelText: l10n.studioWorkflowTaskProfileTitle,
                          ),
                          initialValue:
                              blueprints
                                  .where((bp) => !bp.isSystemCore)
                                  .any((bp) => bp.id == stepDef.taskBlueprint)
                              ? stepDef.taskBlueprint
                              : null,
                          items: blueprints.where((bp) => !bp.isSystemCore).map(
                            (bp) {
                              final label = getBlueprintLabel(bp.id);
                              return DropdownMenuItem(
                                value: bp.id,
                                child: Text(
                                  label,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              );
                            },
                          ).toList(),
                          onChanged: (val) {
                            if (val != null) {
                              update(stepDef.copyWith(taskBlueprint: val));
                            }
                          },
                        ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // ZONE-BASED BODY RENDERING
            if (isZoneA) ...[
              // ZONE A: Input Ingestion Anchor (Step 1)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Theme.of(
                    context,
                  ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: Theme.of(context).colorScheme.outlineVariant,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.studioWorkflowStep1IngestionTitle,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      l10n.studioWorkflowStep1IngestionSubtitle,
                      style: TextStyle(
                        fontSize: 12,
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.secondaryContainer,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        l10n.studioWorkflowStep1OutputBadge,
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: Theme.of(
                            context,
                          ).colorScheme.onSecondaryContainer,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ] else if (isZoneC) ...[
              // ZONE C: Pipeline Funnel Anchors (Protected Automated Steps)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Theme.of(
                    context,
                  ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: Theme.of(context).colorScheme.outlineVariant,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.studioWorkflowZoneCAutoTitle,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      l10n.studioWorkflowXaiReporterPayloadDesc,
                      style: TextStyle(
                        fontSize: 12,
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.tertiaryContainer,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        l10n.studioWorkflowXaiReporterAggregateBadge,
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: Theme.of(
                            context,
                          ).colorScheme.onTertiaryContainer,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ] else ...[
              // ZONE B: Dynamic Specialists (Steps 2..N)

              // 1. Execution Order & Dependencies
              Text(
                l10n.studioWorkflowExecutionOrderTitle,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 2),
              Text(
                l10n.studioWorkflowExecutionOrderSubtitle,
                style: TextStyle(
                  fontSize: 12,
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 8),
              if (previousSteps.isEmpty)
                Text(
                  l10n.studioWorkflowNoDependencies,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                )
              else
                Wrap(
                  spacing: 8,
                  children: previousSteps.map((prevId) {
                    final isSelected = dependsOn.contains(prevId);

                    String displayLabel = prevId;
                    final matchingNode = allSteps
                        .where((s) => s.id == prevId)
                        .firstOrNull;
                    if (matchingNode != null &&
                        matchingNode.taskBlueprint.isNotEmpty) {
                      final readableName = getBlueprintLabel(
                        matchingNode.taskBlueprint,
                      );
                      displayLabel = readableName.isNotEmpty
                          ? readableName
                          : prevId;
                    }

                    return FilterChip(
                      label: Text(
                        displayLabel,
                        overflow: TextOverflow.ellipsis,
                      ),
                      selected: isSelected,
                      onSelected: (bool selected) {
                        final newDependsOn = List<String>.from(dependsOn);
                        if (selected) {
                          if (!newDependsOn.contains(prevId)) {
                            newDependsOn.add(prevId);
                          }
                        } else {
                          newDependsOn.remove(prevId);
                        }
                        update(stepDef.copyWith(dependsOn: newDependsOn));
                      },
                    );
                  }).toList(),
                ),

              const SizedBox(height: 16),

              // 2. Input Scope Selection (Categorized Sections)
              // Section 1: Atomized Materials ($inputs.*)
              Text(
                l10n.studioWorkflowAtomicScopeTitle,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 2),
              Text(
                l10n.studioWorkflowAtomicScopeSubtitle,
                style: TextStyle(
                  fontSize: 12,
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 8),

              if (globalWorkflowInputs.isEmpty)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4.0),
                  child: Text(
                    l10n.studioWorkflowNoSelectableInputs,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                )
              else
                Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: Theme.of(context).colorScheme.outlineVariant,
                    ),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    children: globalWorkflowInputs.map((ei) {
                      final targetKey = ei.inputKey;
                      final sourceValue = r'$inputs.' + ei.inputKey;
                      final isSemanticMapped =
                          mappings.containsValue(sourceValue) &&
                          mappings[targetKey] != sourceValue;
                      final isSelected =
                          mappings[targetKey] == sourceValue ||
                          isSemanticMapped;
                      final isReadOnly = isSemanticMapped;
                      final labelText = ei.label.get(locale);

                      return CheckboxListTile(
                        title: Text(
                          l10n.studioWorkflowInputPrefix(labelText),
                          overflow: TextOverflow.ellipsis,
                        ),
                        subtitle: Text(
                          sourceValue,
                          overflow: TextOverflow.ellipsis,
                        ),
                        value: isSelected,
                        onChanged: isReadOnly
                            ? null
                            : (bool? checked) {
                                final newMappings = Map<String, String>.from(
                                  mappings,
                                );
                                if (checked == true) {
                                  newMappings[targetKey] = sourceValue;
                                } else {
                                  newMappings.remove(targetKey);
                                }
                                update(
                                  stepDef.copyWith(inputMappings: newMappings),
                                );
                              },
                        controlAffinity: ListTileControlAffinity.leading,
                        dense: true,
                      );
                    }).toList(),
                  ),
                ),

              // Section 2: Prior Step Reports ($steps.*)
              if (dependsOn.isNotEmpty) ...[
                Text(
                  l10n.studioWorkflowPriorStepsTitle,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 2),
                Text(
                  l10n.studioWorkflowPriorStepsSubtitle,
                  style: TextStyle(
                    fontSize: 12,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: Theme.of(context).colorScheme.outlineVariant,
                    ),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    children: dependsOn.map((prevId) {
                      final targetKey = prevId;
                      final sourceValue = r'$steps.' + prevId;
                      final isSemanticMapped =
                          mappings.containsValue(sourceValue) &&
                          mappings[targetKey] != sourceValue;
                      final isGlobalStepsMapped = mappings.containsValue(
                        r'$steps',
                      );
                      final isSelected =
                          mappings[targetKey] == sourceValue ||
                          isSemanticMapped ||
                          isGlobalStepsMapped;
                      final isReadOnly =
                          isSemanticMapped || isGlobalStepsMapped;

                      final matchingNode = allSteps
                          .where((s) => s.id == prevId)
                          .firstOrNull;
                      String labelStr = prevId;
                      if (matchingNode != null &&
                          matchingNode.taskBlueprint.isNotEmpty) {
                        final resolved = getBlueprintLabel(
                          matchingNode.taskBlueprint,
                        );
                        if (resolved.isNotEmpty) {
                          labelStr = resolved;
                        }
                      }

                      return CheckboxListTile(
                        title: Text(
                          l10n.studioWorkflowStepPrefix(labelStr),
                          overflow: TextOverflow.ellipsis,
                        ),
                        subtitle: Text(
                          sourceValue,
                          overflow: TextOverflow.ellipsis,
                        ),
                        value: isSelected,
                        onChanged: isReadOnly
                            ? null
                            : (bool? checked) {
                                final newMappings = Map<String, String>.from(
                                  mappings,
                                );
                                if (checked == true) {
                                  newMappings[targetKey] = sourceValue;
                                } else {
                                  newMappings.remove(targetKey);
                                }
                                update(
                                  stepDef.copyWith(inputMappings: newMappings),
                                );
                              },
                        controlAffinity: ListTileControlAffinity.leading,
                        dense: true,
                      );
                    }).toList(),
                  ),
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }
}
