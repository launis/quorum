import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:go_router/go_router.dart';
import 'package:file_picker/file_picker.dart';

import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/router/router.dart';

part 'new_execution_view.g.dart';

// 1. Provider to fetch available workflows
@riverpod
Future<List<Map<String, dynamic>>> availableWorkflows(Ref ref) async {
  final dio = ref.watch(apiClientProvider);
  final response = await dio.get(
    '/studio/workflows',
  ); // Note: Reusing the studio endpoint for now since there's no public one yet

  final List<dynamic> data = SafeCast.safeList(response.data);
  return data.map((e) => SafeCast.safeMap(e)).toList();
}

@riverpod
class NewExecutionController extends _$NewExecutionController {
  @override
  FutureOr<void> build() {
    return null;
  }

  Future<void> startExecution({
    required String workflowId,
    required Map<String, dynamic> collectedInputs,
  }) async {
    state = const AsyncLoading();
    try {
      final dio = ref.read(apiClientProvider);

      final response = await dio.post(
        '/execution/executions/',
        data: {'workflow_id': workflowId, 'raw_inputs': collectedInputs},
      );

      final executionId = SafeCast.safeString(response.data['id']);
      state = const AsyncValue.data(null);

      // Navigate to details via the router using context? Cannot do context here cleanly
      // We will throw the ID to UI instead of storing it
      throw Exception('SUCCESS:$executionId');
    } catch (e) {
      if (e.toString().startsWith('Exception: SUCCESS:')) {
        rethrow;
      }
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

// 3. UI View
class NewExecutionView extends ConsumerStatefulWidget {
  const NewExecutionView({super.key});

  @override
  ConsumerState<NewExecutionView> createState() => _NewExecutionViewState();
}

class _NewExecutionViewState extends ConsumerState<NewExecutionView> {
  Map<String, dynamic>? _selectedWorkflow;
  final Map<String, dynamic> _compiledInputs = {};

  // To keep track of filename for UI
  final Map<String, String> _selectedFileNames = {};

  // Controllers for text fields
  final Map<String, TextEditingController> _textControllers = {};

  @override
  void dispose() {
    for (final c in _textControllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  void _onWorkflowSelected(Map<String, dynamic>? workflow) {
    if (workflow == null) return;
    setState(() {
      _selectedWorkflow = workflow;
      _compiledInputs.clear();
      _selectedFileNames.clear();

      for (final c in _textControllers.values) {
        c.dispose();
      }
      _textControllers.clear();
    });
  }

  Future<void> _pickFile(String inputKey) async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'txt', 'docx'],
      withData: true,
    );

    if (result != null && result.files.single.bytes != null) {
      Uint8List fileBytes = result.files.single.bytes!;
      String fileName = result.files.single.name;
      String base64String = base64Encode(fileBytes);

      setState(() {
        _compiledInputs[inputKey] = base64String;
        _selectedFileNames[inputKey] = fileName;
      });
    }
  }

  void _submit() async {
    if (_selectedWorkflow == null) return;

    // Harvest text controller inputs
    _textControllers.forEach((key, controller) {
      if (controller.text.isNotEmpty) {
        _compiledInputs[key] = controller.text;
      }
    });

    final workflowId = SafeCast.safeString(_selectedWorkflow!['id']);

    try {
      await ref
          .read(newExecutionControllerProvider.notifier)
          .startExecution(
            workflowId: workflowId,
            collectedInputs: _compiledInputs,
          );
    } catch (e) {
      if (e.toString().startsWith('Exception: SUCCESS:')) {
        final execId = e.toString().split('SUCCESS:')[1];
        // Safe context routing using GoRouter Codegen
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Execution started successfully!')),
          );
          ExecutionRoute(executionId: execId).go(context);
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(newExecutionControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('New Analysis Pipeline (SDUI)'),
        leading: BackButton(onPressed: () => context.go('/dashboard')),
      ),
      body: Row(
        children: [
          // Sidebar: Workflow selector
          Expanded(flex: 1, child: _buildWorkflowSidebar()),
          const VerticalDivider(width: 1),
          // Main content: Dynamic Form
          Expanded(flex: 2, child: _buildDynamicForm(state)),
        ],
      ),
    );
  }

  Widget _buildWorkflowSidebar() {
    final asyncWorkflows = ref.watch(availableWorkflowsProvider);

    return asyncWorkflows.when(
      data: (workflows) {
        if (workflows.isEmpty) {
          return const Center(child: Text('No workflows available.'));
        }
        return ListView.builder(
          itemCount: workflows.length,
          itemBuilder: (context, index) {
            final wf = workflows[index];
            final id = SafeCast.safeString(wf['id']);
            
            final nameMap = SafeCast.safeMap(wf['name']);
            final titleStr = nameMap.isNotEmpty 
                ? (nameMap['translations']?[nameMap['default_locale']] ?? nameMap['default_locale'] ?? id)
                : (SafeCast.safeString(wf['name']).isNotEmpty ? SafeCast.safeString(wf['name']) : id);

            final descMap = SafeCast.safeMap(wf['description']);
            final descStr = descMap.isNotEmpty 
                ? (descMap['translations']?[descMap['default_locale']] ?? descMap['default_locale'] ?? '')
                : SafeCast.safeString(wf['description']);

            final isSelected = _selectedWorkflow?['id'] == id;

            return ListTile(
              title: Text(
                '$titleStr\n($id)',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text(
                descStr,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              selected: isSelected,
              selectedTileColor: Theme.of(context).colorScheme.primaryContainer,
              onTap: () => _onWorkflowSelected(wf),
            );
          },
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, st) => Center(child: Text('Error loading workflows: $e')),
    );
  }

  Widget _buildDynamicForm(AsyncValue<void> state) {
    if (_selectedWorkflow == null) {
      return const Center(
        child: Text('Select a workflow from the list to begin.'),
      );
    }

    final id = SafeCast.safeString(_selectedWorkflow!['id']);
    final expectedInputsRaw = _selectedWorkflow!['expected_inputs'];

    // Parse expected_inputs gracefully (V2 List of ExpectedInput objects)
    Map<String, String> expectedInputs = {};
    if (expectedInputsRaw is List) {
      for (final e in expectedInputsRaw) {
        final item = SafeCast.safeMap(e);
        final key = SafeCast.safeString(item['input_key']);
        if (key.isNotEmpty) {
          final modes = SafeCast.safeList(item['input_modes'])
              .map((m) => m.toString())
              .toList();
          final hint = modes.contains('file') ? 'file' : 'text';
          expectedInputs[key] = hint;
        }
      }
    }

    if (expectedInputs.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.flash_on, size: 60, color: Colors.orange),
            const SizedBox(height: 16),
            Text(
              'No inputs strictly required for \n$id',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 24),
            _buildSubmitButton(state),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Configure Inputs for $id',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 24),

          ...expectedInputs.entries.map((entry) {
            final inputKey = entry.key;
            final typeHint = entry.value; // e.g. "file", "text"

            return Padding(
              padding: const EdgeInsets.only(bottom: 24),
              child: _buildInputWidget(inputKey, typeHint),
            );
          }),

          const Divider(height: 48),

          if (state.hasError) ...[
            Text(
              'Error: ${state.error}',
              style: const TextStyle(color: Colors.red),
            ),
            const SizedBox(height: 16),
          ],

          _buildSubmitButton(state),
        ],
      ),
    );
  }

  Widget _buildInputWidget(String inputKey, String typeHint) {
    final safeHint = typeHint.toLowerCase();

    if (safeHint == 'file' || safeHint == 'pdf') {
      final fileName = _selectedFileNames[inputKey];
      final hasFile = fileName != null;

      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey.shade300),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Icon(
              hasFile ? Icons.check_circle : Icons.upload_file,
              color: hasFile ? Colors.green : Colors.grey,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Input: $inputKey',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    hasFile ? 'Selected: $fileName' : 'No file selected',
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                  ),
                ],
              ),
            ),
            ElevatedButton.icon(
              onPressed: () => _pickFile(inputKey),
              icon: const Icon(Icons.attach_file),
              label: const Text('Browse'),
            ),
          ],
        ),
      );
    }

    // Default: text
    if (!_textControllers.containsKey(inputKey)) {
      _textControllers[inputKey] = TextEditingController();
    }

    return TextField(
      controller: _textControllers[inputKey],
      maxLines: 5,
      decoration: InputDecoration(
        labelText: 'Input: $inputKey',
        alignLabelWithHint: true,
        border: const OutlineInputBorder(),
        helperText: 'Type: $typeHint',
      ),
    );
  }

  Widget _buildSubmitButton(AsyncValue<void> state) {
    if (state.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return SizedBox(
      width: double.infinity,
      height: 50,
      child: FilledButton.icon(
        onPressed: _submit,
        icon: const Icon(Icons.rocket_launch),
        label: const Text('Start AI Execution', style: TextStyle(fontSize: 16)),
      ),
    );
  }
}
