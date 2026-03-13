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
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

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
    int strictnessLevel = 3,
  }) async {
    state = const AsyncLoading();
    try {
      final dio = ref.read(apiClientProvider);

      final response = await dio.post(
        '/execution/executions/',
        data: {
          'workflow_id': workflowId,
          'raw_inputs': collectedInputs,
          'strictness_level': strictnessLevel,
        },
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

  int _strictnessLevel = 3;

  void _onWorkflowSelected(Map<String, dynamic>? workflow) {
    if (workflow == null) return;
    setState(() {
      _selectedWorkflow = workflow;
      _compiledInputs.clear();
      _selectedFileNames.clear();
      _strictnessLevel = 3; // Reset to default

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
        _compiledInputs[inputKey] = {
          'filename': fileName,
          'content_base64': base64String,
        };
        _selectedFileNames[inputKey] = fileName;
      });
    }
  }

  void _submit() async {
    if (_selectedWorkflow == null) return;

    // Harvest text controller inputs
    _textControllers.forEach((key, controller) {
      if (controller.text.isNotEmpty) {
        if (key.contains('|||')) {
          final parts = key.split('|||');
          final semanticRole = parts[0];
          final qId = parts[1];
          if (_compiledInputs[semanticRole] == null ||
              _compiledInputs[semanticRole] is! Map) {
            _compiledInputs[semanticRole] = <String, dynamic>{};
          }
          (_compiledInputs[semanticRole] as Map<String, dynamic>)[qId] =
              controller.text;
        } else {
          // Prioritize file upload if one is already selected
          final hasFile =
              _compiledInputs.containsKey(key) &&
              _compiledInputs[key] is Map &&
              (_compiledInputs[key] as Map).containsKey('content_base64');
          if (!hasFile) {
            _compiledInputs[key] = controller.text;
          }
        }
      }
    });

    final workflowId = SafeCast.safeString(_selectedWorkflow!['id']);

    try {
      await ref
          .read(newExecutionControllerProvider.notifier)
          .startExecution(
            workflowId: workflowId,
            collectedInputs: _compiledInputs,
            strictnessLevel: _strictnessLevel,
          );
    } catch (e) {
      if (e.toString().startsWith('Exception: SUCCESS:')) {
        final execId = e.toString().split('SUCCESS:')[1];
        // Safe context routing using GoRouter Codegen
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                AppLocalizations.of(context)!.executionStartedSuccessfully,
              ),
            ),
          );
          ExecutionRoute(executionId: execId).go(context);
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                AppLocalizations.of(
                  context,
                )!.failedToStartExecution(e.toString()),
              ),
              backgroundColor: Theme.of(context).colorScheme.error,
              duration: const Duration(seconds: 5),
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(newExecutionControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.newAnalysisPipelineTitle),
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
            final titleStr =
                nameMap.isNotEmpty
                    ? (nameMap['translations']?[nameMap['default_locale']] ??
                        nameMap['default_locale'] ??
                        id)
                    : (SafeCast.safeString(wf['name']).isNotEmpty
                        ? SafeCast.safeString(wf['name'])
                        : id);

            final descMap = SafeCast.safeMap(wf['description']);
            final descStr =
                descMap.isNotEmpty
                    ? (descMap['translations']?[descMap['default_locale']] ??
                        descMap['default_locale'] ??
                        '')
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
      error:
          (e, st) => ErrorView(
            error: e,
            stackTrace: st,
            compact: true,
            onRetry: () => ref.invalidate(availableWorkflowsProvider),
          ),
    );
  }

  Widget _buildDynamicForm(AsyncValue<void> state) {
    if (_selectedWorkflow == null) {
      return Center(
        child: Text(AppLocalizations.of(context)!.selectWorkflowPrompt),
      );
    }

    final id = SafeCast.safeString(_selectedWorkflow!['id']);
    final expectedInputsRaw = _selectedWorkflow!['expected_inputs'];

    // Parse expected_inputs gracefully (V2 List of ExpectedInput objects)
    List<Map<String, dynamic>> expectedInputsList = [];
    if (expectedInputsRaw is List) {
      for (final e in expectedInputsRaw) {
        final item = SafeCast.safeMap(e);
        final key = SafeCast.safeString(item['input_key']);
        if (key.isNotEmpty) {
          expectedInputsList.add(item);
        }
      }
    }

    if (expectedInputsList.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.flash_on, size: 60, color: Colors.orange),
            const SizedBox(height: 16),
            Text(
              AppLocalizations.of(context)!.noInputsRequired(id),
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
            AppLocalizations.of(context)!.configureInputsFor(id),
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 24),

          ...expectedInputsList.map((item) {
            final inputKey = SafeCast.safeString(item['input_key']);
            final modes =
                SafeCast.safeList(
                  item['input_modes'],
                ).map((m) => m.toString()).toList();

            // Handle questionnaire first
            if (modes.contains('questionnaire')) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 24),
                child: _buildQuestionnaireWidget(inputKey, item),
              );
            }

            final showFile = modes.contains('file');
            final showText =
                modes.contains('paste') ||
                modes.contains('text') ||
                (!showFile && !modes.contains('questionnaire'));

            return Padding(
              padding: const EdgeInsets.only(bottom: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (showFile) ...[
                    _buildInputWidget(inputKey, 'file'),
                    if (showText) const SizedBox(height: 16),
                  ],
                  if (showText) _buildInputWidget(inputKey, 'text'),
                ],
              ),
            );
          }),

          const Divider(height: 48),

          _buildStrictnessSelector(),
          const SizedBox(height: 24),

          if (state.hasError) ...[
            ErrorView(error: state.error!, compact: true),
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
                    AppLocalizations.of(context)!.inputLabel(inputKey),
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    hasFile
                        ? AppLocalizations.of(context)!.selectedFile(fileName)
                        : AppLocalizations.of(context)!.noFileSelected,
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                  ),
                ],
              ),
            ),
            ElevatedButton.icon(
              onPressed: () => _pickFile(inputKey),
              icon: const Icon(Icons.attach_file),
              label: Text(AppLocalizations.of(context)!.browseFile),
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
        labelText: AppLocalizations.of(context)!.inputLabel(inputKey),
        alignLabelWithHint: true,
        border: const OutlineInputBorder(),
        helperText: AppLocalizations.of(context)!.inputTypeHint(typeHint),
      ),
    );
  }

  Widget _buildQuestionnaireWidget(String inputKey, Map<String, dynamic> item) {
    final defs = SafeCast.safeList(item['questionnaire_definition']);
    final labelObj = SafeCast.safeMap(item['label']);
    final translations = SafeCast.safeMap(labelObj['translations']);
    final defaultLocale = SafeCast.safeString(labelObj['default_locale'], 'en');
    String title = SafeCast.safeString(translations['fi']);
    if (title.isEmpty) title = SafeCast.safeString(translations[defaultLocale]);
    if (title.isEmpty) title = inputKey;

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: Theme.of(context).colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppLocalizations.of(context)!.questionnaireTitle(title),
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ...defs.map((defInput) {
              final def = SafeCast.safeMap(defInput);
              final qId = SafeCast.safeString(def['question_id']);
              final qLabelObj = SafeCast.safeMap(def['question']);
              final qTranslations = SafeCast.safeMap(qLabelObj['translations']);
              final qDefaultLocale = SafeCast.safeString(
                qLabelObj['default_locale'],
                'en',
              );

              String qLabel = '';
              if (qTranslations.isNotEmpty) {
                qLabel = SafeCast.safeString(qTranslations['fi']);
                if (qLabel.isEmpty) {
                  qLabel = SafeCast.safeString(qTranslations[qDefaultLocale]);
                }
              }
              if (qLabel.isEmpty) qLabel = qId;

              // Use custom key with separator
              final mapKey = "$inputKey|||$qId";
              if (!_textControllers.containsKey(mapKey)) {
                _textControllers[mapKey] = TextEditingController();
              }

              return Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: TextField(
                  controller: _textControllers[mapKey],
                  decoration: InputDecoration(
                    labelText: qLabel,
                    border: const OutlineInputBorder(),
                  ),
                  maxLines: 3,
                ),
              );
            }),
          ],
        ),
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
        label: Text(
          AppLocalizations.of(context)!.startAiExecution,
          style: const TextStyle(fontSize: 16),
        ),
      ),
    );
  }

  Widget _buildStrictnessSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          AppLocalizations.of(context)!.strictnessLevelTitle,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceContainerHighest.withOpacity(0.5),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: Theme.of(context).colorScheme.outlineVariant,
            ),
          ),
          child: Column(
            children: [
              Slider(
                value: _strictnessLevel.toDouble(),
                min: 1,
                max: 5,
                divisions: 4,
                label: _getStrictnessLabel(_strictnessLevel),
                onChanged: (double value) {
                  setState(() {
                    _strictnessLevel = value.toInt();
                  });
                },
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('1', style: Theme.of(context).textTheme.bodySmall),
                    Text('5', style: Theme.of(context).textTheme.bodySmall),
                  ],
                ),
              ),
              const SizedBox(height: 8),
              Text(
                _getStrictnessLabel(_strictnessLevel),
                style: const TextStyle(fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _getStrictnessLabel(int level) {
    switch (level) {
      case 1:
        return AppLocalizations.of(context)!.strictnessGricean;
      case 2:
        return AppLocalizations.of(context)!.strictnessLiteral;
      case 3:
        return AppLocalizations.of(context)!.strictnessCausal;
      case 4:
        return AppLocalizations.of(context)!.strictnessFalsification;
      case 5:
        return AppLocalizations.of(context)!.strictnessZeroTrust;
      default:
        return AppLocalizations.of(context)!.strictnessCausal;
    }
  }
}
