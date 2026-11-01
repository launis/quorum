import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

const double _kInspectorPaneWidth = 350.0;
const double _kDividerHeight = 1.0;
const double _kRemoveIconSize = 20.0;
const double _kAddIconSize = 16.0;

class InspectorPane extends StatelessWidget {
  final String? selectedStepId;
  final Workflow workflow;
  final List<NodeStrategy> availableBlueprints;
  final void Function(String stepId, StepRule updatedStep) onStepUpdated;
  final VoidCallback onAddStep;
  final void Function(String stepId) onDeleteStep;

  const InspectorPane({
    super.key,
    required this.selectedStepId,
    required this.workflow,
    required this.availableBlueprints,
    required this.onStepUpdated,
    required this.onAddStep,
    required this.onDeleteStep,
  });

  void _validateInvariants() {
    if (workflow.id.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: Workflow ID cannot be empty in InspectorPane.',
      );
    }
    for (final NodeStrategy bp in availableBlueprints) {
      if (bp.id.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: Blueprint ID cannot be empty in InspectorPane.',
        );
      }
    }
    if (selectedStepId != null && selectedStepId!.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: selectedStepId cannot be blank in InspectorPane.',
      );
    }
  }

  StepRule _resolveSelectedStep(String stepId) {
    for (final StepRule step in workflow.steps) {
      if (step.id == stepId) {
        return step;
      }
    }
    throw AppException.validation(
      'Selected step definition not found: $stepId. Data is corrupted.',
    );
  }

  @override
  Widget build(BuildContext context) {
    _validateInvariants();

    final AppLocalizations l10n = AppLocalizations.of(context)!;
    final ThemeData theme = Theme.of(context);

    if (selectedStepId == null) {
      return Container(
        width: _kInspectorPaneWidth,
        color: theme.cardColor,
        child: Column(
          children: <Widget>[
            Padding(
              padding: AppSpacing.p16,
              child: Text(
                l10n.systemInspectorTitle,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const Spacer(),
            Padding(
              padding: AppSpacing.p16,
              child: Text(
                l10n.studioSelectStepPrompt,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
            ),
            const Spacer(),
            Padding(
              padding: AppSpacing.p16,
              child: FilledButton.icon(
                key: const ValueKey<String>('inspector_add_step_btn'),
                onPressed: onAddStep,
                icon: const Icon(Icons.add),
                label: Text(
                  l10n.studioWorkflowAddStepNodeBtn,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ),
          ],
        ),
      );
    }

    final String activeStepId = selectedStepId!;
    final StepRule stepDef = _resolveSelectedStep(activeStepId);

    return Container(
      width: _kInspectorPaneWidth,
      color: theme.cardColor,
      child: Column(
        children: <Widget>[
          Padding(
            padding: AppSpacing.p16,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Expanded(
                  child: Text(
                    l10n.studioConfigurationTitle,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                IconButton(
                  key: const ValueKey<String>('inspector_delete_step_btn'),
                  tooltip: l10n.delete,
                  icon: Icon(Icons.delete, color: theme.colorScheme.error),
                  onPressed: () => onDeleteStep(activeStepId),
                ),
              ],
            ),
          ),
          const Divider(height: _kDividerHeight),
          Expanded(
            child: SingleChildScrollView(
              padding: AppSpacing.p16,
              child: _buildInspectorForm(context, theme, stepDef, l10n),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInspectorForm(
    BuildContext context,
    ThemeData theme,
    StepRule stepDef,
    AppLocalizations l10n,
  ) {
    final String activeStepId = stepDef.id;
    final String currentLocale = Localizations.localeOf(context).languageCode;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        Text(
          l10n.studioWorkflowNodeIdOpaque,
          style: theme.textTheme.labelMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.onSurfaceVariant,
          ),
          overflow: TextOverflow.ellipsis,
        ),
        SelectableText(
          stepDef.id,
          style: theme.textTheme.bodyMedium?.copyWith(fontFamily: 'monospace'),
        ),
        AppSpacing.h16,
        DropdownButtonFormField<String>(
          key: ValueKey<String>(
            'inspector_blueprint_dropdown_${stepDef.id}_${stepDef.taskBlueprint}',
          ),
          decoration: InputDecoration(
            labelText: l10n.studioWorkflowTaskBlueprint,
            isDense: true,
          ),
          isExpanded: true,
          initialValue:
              availableBlueprints.any(
                (NodeStrategy bp) => bp.id == stepDef.taskBlueprint,
              )
              ? stepDef.taskBlueprint
              : null,
          items: availableBlueprints.map((NodeStrategy bp) {
            final String id = bp.id;
            final String label = bp.name.get(currentLocale);

            return DropdownMenuItem<String>(
              value: id,
              child: Text(label, overflow: TextOverflow.ellipsis),
            );
          }).toList(),
          onChanged: (String? val) {
            if (val != null) {
              onStepUpdated(activeStepId, stepDef.copyWith(taskBlueprint: val));
            }
          },
        ),
        AppSpacing.h16,
        Text(
          l10n.studioWorkflowDependsOn,
          style: theme.textTheme.labelMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          overflow: TextOverflow.ellipsis,
        ),
        AppSpacing.h4,
        TextFormField(
          key: ValueKey<String>(
            'inspector_depends_on_${stepDef.id}_${stepDef.dependsOn.join(",")}',
          ),
          initialValue: stepDef.dependsOn.join(', '),
          decoration: const InputDecoration(
            isDense: true,
            border: OutlineInputBorder(),
          ),
          onFieldSubmitted: (String val) {
            final List<String> newDependsOn = val
                .split(',')
                .map((String e) => e.trim())
                .where((String e) => e.isNotEmpty)
                .toList();
            onStepUpdated(
              activeStepId,
              stepDef.copyWith(dependsOn: newDependsOn),
            );
          },
        ),
        AppSpacing.h16,
        Text(
          l10n.studioWorkflowInputMappings,
          style: theme.textTheme.labelMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          overflow: TextOverflow.ellipsis,
        ),
        ...stepDef.inputMappings.entries.map((MapEntry<String, String> e) {
          return Padding(
            padding: const EdgeInsets.only(top: AppSpacing.s8),
            child: Row(
              children: <Widget>[
                Expanded(
                  flex: 1,
                  child: TextFormField(
                    key: ValueKey<String>(
                      'inspector_mapping_key_${stepDef.id}_${e.key}',
                    ),
                    initialValue: e.key,
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      hintText: l10n.studioWorkflowTargetArgName,
                    ),
                    onFieldSubmitted: (String rawKey) {
                      final String newKey = rawKey.trim();
                      if (newKey.isNotEmpty && newKey != e.key) {
                        final Map<String, String> newMappings =
                            Map<String, String>.from(stepDef.inputMappings);
                        final String? val = newMappings.remove(e.key);
                        if (val != null) {
                          newMappings[newKey] = val;
                          onStepUpdated(
                            activeStepId,
                            stepDef.copyWith(inputMappings: newMappings),
                          );
                        }
                      }
                    },
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  flex: 2,
                  child: TextFormField(
                    key: ValueKey<String>(
                      'inspector_mapping_val_${stepDef.id}_${e.key}_${e.value}',
                    ),
                    initialValue: e.value,
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      hintText: l10n.studioWorkflowSourceToken,
                    ),
                    onFieldSubmitted: (String newVal) {
                      final Map<String, String> newMappings =
                          Map<String, String>.from(stepDef.inputMappings);
                      newMappings[e.key] = newVal.trim();
                      onStepUpdated(
                        activeStepId,
                        stepDef.copyWith(inputMappings: newMappings),
                      );
                    },
                  ),
                ),
                IconButton(
                  key: ValueKey<String>(
                    'inspector_mapping_remove_${stepDef.id}_${e.key}',
                  ),
                  tooltip: l10n.delete,
                  icon: Icon(
                    Icons.remove_circle,
                    color: theme.colorScheme.error,
                    size: _kRemoveIconSize,
                  ),
                  onPressed: () {
                    final Map<String, String> newMappings =
                        Map<String, String>.from(stepDef.inputMappings);
                    newMappings.remove(e.key);
                    onStepUpdated(
                      activeStepId,
                      stepDef.copyWith(inputMappings: newMappings),
                    );
                  },
                ),
              ],
            ),
          );
        }),
        AppSpacing.h8,
        Align(
          alignment: Alignment.centerLeft,
          child: TextButton.icon(
            key: const ValueKey<String>('inspector_add_mapping_btn'),
            onPressed: () {
              final Map<String, String> newMappings = Map<String, String>.from(
                stepDef.inputMappings,
              );
              newMappings['new_param_${newMappings.length}'] = r'$inputs.';
              onStepUpdated(
                activeStepId,
                stepDef.copyWith(inputMappings: newMappings),
              );
            },
            icon: const Icon(Icons.add, size: _kAddIconSize),
            label: Text(
              l10n.workflowAddMappingBtn,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ),
      ],
    );
  }
}
