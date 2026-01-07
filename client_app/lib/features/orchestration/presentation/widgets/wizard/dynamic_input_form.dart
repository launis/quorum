import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/orchestration/presentation/providers/wizard_provider.dart';
import 'package:client_app/features/orchestration/presentation/widgets/wizard/file_input_field.dart';

class DynamicInputForm extends ConsumerStatefulWidget {
  const DynamicInputForm({super.key});

  @override
  ConsumerState<DynamicInputForm> createState() => _DynamicInputFormState();
}

class _DynamicInputFormState extends ConsumerState<DynamicInputForm> {
  final _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    final workflowId = ref.watch(
      wizardStateProvider.select((s) => s.selectedWorkflowId),
    );
    final inputs = ref.watch(wizardStateProvider.select((s) => s.inputs));

    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Configure Inputs: $workflowId',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 16),

          if (workflowId == 'fused_audit_chain' ||
              workflowId == 'sequential_audit_chain') ...[
            // Audit Workflows require file inputs
            _buildFileInput(
              label: '1. Chat History / Evidence (Chat Logs)',
              keyName: 'history_text',
              icon: Icons.history,
              currentValue: inputs['history_text'] as PlatformFile?,
            ),
            const SizedBox(height: 16),
            _buildFileInput(
              label: '2. Product / Evaluation Target (Final Product)',
              keyName: 'product_text',
              icon: Icons.inventory_2,
              currentValue: inputs['product_text'] as PlatformFile?,
            ),
            const SizedBox(height: 16),
            _buildFileInput(
              label: '3. Reflection / Self-Evaluation',
              keyName: 'reflection_text',
              icon: Icons.lightbulb,
              currentValue: inputs['reflection_text'] as PlatformFile?,
            ),
          ] else if (workflowId == 'deep_research') ...[
            _buildTextField(
              label: 'Research Topic',
              keyName: 'topic',
              icon: Icons.search,
            ),
            const SizedBox(height: 16),
            _buildTextField(
              label: 'Context URLs (comma separated)',
              keyName: 'urls',
              icon: Icons.link,
            ),
          ] else ...[
            // Default generic fallback
            _buildTextField(
              label: 'General Input',
              keyName: 'input_text',
              icon: Icons.message,
              minLines: 5,
            ),
          ],
        ],
      ),
    );
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
          return 'This file is required.';
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
          return 'This field is required.';
        }
        return null;
      },
      onChanged: (value) {
        ref.read(wizardStateProvider.notifier).updateInput(keyName, value);
      },
    );
  }
}
