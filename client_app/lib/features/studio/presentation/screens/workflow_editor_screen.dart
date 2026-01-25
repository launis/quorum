import 'package:client_app/features/orchestration/presentation/widgets/sdui/dynamic_form.dart';
import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// **Workflow Editor Screen**
///
/// A dynamic editor for Workflow Definitions, powered by SDUI.
/// Fetches the JSON Schema from [StudioController] and renders a [DynamicFormWidget].
class WorkflowEditorScreen extends ConsumerStatefulWidget {
  const WorkflowEditorScreen({super.key});

  @override
  ConsumerState<WorkflowEditorScreen> createState() =>
      _WorkflowEditorScreenState();
}

class _WorkflowEditorScreenState extends ConsumerState<WorkflowEditorScreen> {
  Map<String, dynamic>? _schema;
  final Map<String, dynamic> _formData = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSchema();
  }

  Future<void> _loadSchema() async {
    try {
      final schema =
          await ref
              .read(studioControllerProvider.notifier)
              .fetchWorkflowSchema();
      if (mounted) {
        setState(() {
          _schema = schema;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Failed to load schema: $e')));
        setState(() => _isLoading = false);
      }
    }
  }

  void _onSave() async {
    if (_schema == null) return;

    // Validate if necessary (Form Widget handles field validation visually)
    // We could add a 'validate' method to DynamicFormWidget via GlobalKey if strictly needed,
    // but for now we rely on user filling it out.

    await ref.read(studioControllerProvider.notifier).saveWorkflow(_formData);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Workflow saved successfully!')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Workflow Editor'),
        actions: [
          if (!_isLoading && _schema != null)
            IconButton(
              icon: const Icon(Icons.save),
              onPressed: _onSave,
              tooltip: 'Save Workflow',
            ),
        ],
      ),
      floatingActionButton:
          !_isLoading && _schema != null
              ? FloatingActionButton.extended(
                onPressed: _onSave,
                label: const Text('Save'),
                icon: const Icon(Icons.save),
              )
              : null,
      body:
          _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _schema == null
              ? const Center(
                child: Text('Failed to load editor configuration.'),
              )
              : SingleChildScrollView(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Edit Workflow Definition',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Define the metadata and properties for this workflow.',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.outline,
                      ),
                    ),
                    const SizedBox(height: 32),
                    DynamicFormWidget(
                      schema: _schema!,
                      // Initial data could also be fetched; empty for new creation
                      initialData: const {},
                      onChanged: (data) {
                        _formData.clear();
                        _formData.addAll(data);
                      },
                    ),
                    const SizedBox(height: 80), // Fab spacing
                  ],
                ),
              ),
    );
  }
}
