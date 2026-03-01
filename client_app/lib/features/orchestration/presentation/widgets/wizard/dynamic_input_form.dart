import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/orchestration/presentation/providers/wizard_provider.dart';
import 'package:client_app/features/orchestration/presentation/widgets/wizard/file_input_field.dart';
import 'package:client_app/features/orchestration/presentation/widgets/wizard/omni_input_box.dart';
import 'package:client_app/features/orchestration/presentation/providers/workflow_controller.dart';
import 'package:client_app/features/orchestration/presentation/widgets/reflection_mode_selector.dart';
import 'package:client_app/features/orchestration/presentation/widgets/guided_reflection_form.dart';
import 'package:client_app/features/orchestration/presentation/providers/reflection_form_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class DynamicInputForm extends ConsumerStatefulWidget {
  const DynamicInputForm({super.key});

  @override
  ConsumerState<DynamicInputForm> createState() => _DynamicInputFormState();
}

class _DynamicInputFormState extends ConsumerState<DynamicInputForm> {
  final _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final workflowId = ref.watch(
      wizardStateProvider.select((s) => s.selectedWorkflowId),
    );
    final workflowAsync = ref.watch(workflowListProvider);
    final inputs = ref.watch(wizardStateProvider.select((s) => s.inputs));

    final workflow =
        workflowAsync.asData?.value
            .where((w) => w.id == workflowId)
            .firstOrNull;

    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            l10n.configureInputs(workflowId.isEmpty ? '...' : workflowId),
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 16),

          if (workflowId.isEmpty)
            Center(
              child: Text(
                l10n.selectWorkflowRequired,
                style: TextStyle(color: Theme.of(context).disabledColor),
              ),
            )
          else if (workflow != null &&
              (workflow.uiSchema?.isNotEmpty ?? false)) ...[
            // Dynamic rendering from Schema
            ...workflow.uiSchema!.entries
                .where((e) => e.key != 'default_model_mapping')
                .map((entry) {
                  final val = entry.value as Map<String, dynamic>;
                  final key = entry.key;
                  final type = val['type'] as String? ?? 'text';
                  final label = _getLocalizedLabel(
                    context,
                    val['label'] as String? ?? key,
                  );
                  final iconData = _getIcon(val['icon'] as String?);
                  final minLines = val['minLines'] as int? ?? 1;

                  // Check if it's one of the main Omni fields
                  final isOmniField =
                      [
                        'INPUT_HISTORY_TEXT',
                        'INPUT_PRODUCT_TEXT',
                        'INPUT_REFLECTION_TEXT',
                      ].contains(val['label']) ||
                      key == 'history_text' ||
                      key == 'product_text' ||
                      key == 'reflection_text';

                  if (isOmniField) {
                    if (key == 'reflection_text' || val['label'] == 'INPUT_REFLECTION_TEXT') {
                      final reflectionMode = ref.watch(reflectionFormControllerProvider.select((s) => s.value?.inputMode));
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            const ReflectionModeSelector(),
                            const SizedBox(height: 16),
                            if (reflectionMode == ReflectionInputMode.file)
                              _buildFileInput(
                                label: label,
                                keyName: key,
                                icon: iconData,
                                currentValue: inputs[key] as PlatformFile?,
                              )
                            else
                              const GuidedReflectionForm(),
                          ],
                        ),
                      );
                    }
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 16.0),
                      child: OmniInputBox(
                        label: label,
                        keyName: key,
                        icon: iconData,
                        minLines: minLines,
                        currentValue: inputs[key],
                        onChanged: (value) {
                          ref
                              .read(wizardStateProvider.notifier)
                              .updateInput(key, value);
                        },
                      ),
                    );
                  } else if (type == 'file') {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 16.0),
                      child: _buildFileInput(
                        label: label,
                        keyName: key,
                        icon: iconData,
                        currentValue: inputs[key] as PlatformFile?,
                      ),
                    );
                  } else {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 16.0),
                      child: _buildTextField(
                        label: label,
                        keyName: key,
                        currentValue: inputs[key] as String?,
                        icon: iconData,
                        minLines: minLines,
                      ),
                    );
                  }
                }),
          ] else
            Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  l10n.fillRequiredInputs, // Or a specific "No inputs needed" string
                  style: TextStyle(color: Theme.of(context).disabledColor),
                ),
              ),
            ),
        ],
      ),
    );
  }

  String _getLocalizedLabel(BuildContext context, String key) {
    final l10n = AppLocalizations.of(context)!;
    switch (key) {
      case 'INPUT_HISTORY_TEXT':
        return l10n.inputChatHistory;
      case 'INPUT_PRODUCT_TEXT':
        return l10n.inputProductTarget;
      case 'INPUT_REFLECTION_TEXT':
        return l10n.inputReflection;
      default:
        return key;
    }
  }

  IconData? _getIcon(String? iconName) {
    if (iconName == null) return null;
    switch (iconName) {
      case 'history':
        return Icons.history;
      case 'inventory_2':
        return Icons.inventory_2;
      case 'lightbulb':
        return Icons.lightbulb;
      case 'search':
        return Icons.search;
      case 'link':
        return Icons.link;
      case 'message':
        return Icons.message;
      default:
        return Icons.insert_drive_file;
    }
  }

  Widget _buildFileInput({
    required String label,
    required String keyName,
    required PlatformFile? currentValue,
    IconData? icon,
  }) {
    return FileInputField(
      label: label,
      icon: icon,
      value: currentValue,
      validator: (value) {
        if (value == null) {
          return AppLocalizations.of(context)!.fileRequired;
        }
        return null;
      },
      onFileSelected: (file) {
        ref.read(wizardStateProvider.notifier).updateInput(keyName, file);
      },
      onClear: () {
        ref.read(wizardStateProvider.notifier).updateInput(keyName, null);
      },
    );
  }

  Widget _buildTextField({
    required String label,
    required String keyName,
    String? currentValue,
    IconData? icon,
    int minLines = 1,
  }) {
    return TextFormField(
      key: ValueKey(keyName),
      initialValue: currentValue,
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
        prefixIcon: icon != null ? Icon(icon) : null,
        alignLabelWithHint: minLines > 1,
      ),
      minLines: minLines,
      maxLines: minLines + 5,
      validator: (value) {
        if (value == null || value.isEmpty) {
          return AppLocalizations.of(context)!.fieldRequired;
        }
        return null;
      },
      onChanged: (value) {
        ref.read(wizardStateProvider.notifier).updateInput(keyName, value);
      },
    );
  }
}
