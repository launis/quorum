import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/orchestration/presentation/providers/wizard_provider.dart';
import 'package:client_app/features/orchestration/presentation/widgets/wizard/file_input_field.dart';
import 'package:client_app/features/orchestration/domain/models/workflow.dart';
import 'package:client_app/features/orchestration/presentation/providers/workflow_controller.dart';
import 'package:client_app/l10n/app_localizations.dart';

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

    final workflow = workflowAsync.asData?.value.firstWhere(
      (w) => w.id == workflowId,
      orElse:
          () => Workflow(
            id: 'unknown',
            name: l10n.unknownWorkflow,
            description: '',
          ),
    );

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
            ...workflow.uiSchema!.entries.map((entry) {
              final val = entry.value as Map<String, dynamic>;
              final key = entry.key;
              final type = val['type'] as String? ?? 'text';
              final label = val['label'] as String? ?? key;
              final iconData = _getIcon(val['icon'] as String?);
              final minLines = val['minLines'] as int? ?? 1;

              if (type == 'file') {
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
    IconData? icon,
    int minLines = 1,
  }) {
    return TextFormField(
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
