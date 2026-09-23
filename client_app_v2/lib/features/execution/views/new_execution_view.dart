import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:go_router/go_router.dart';
import 'package:file_picker/file_picker.dart';

import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';

import 'package:client_app/router/router.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_error_ext.dart';

part 'new_execution_view.g.dart';

// 1. Provider to fetch available workflows
@riverpod
Future<List<Workflow>> availableWorkflows(Ref ref) async {
  final client = ref.watch(studioClientProvider);
  return await client.getWorkflows();
}

@riverpod
class NewExecutionController extends _$NewExecutionController {
  @override
  FutureOr<void> build() {
    return null;
  }

  Future<String> startExecution({
    required String workflowId,
    required Map<String, dynamic> collectedInputs,
    required String targetLocale,
    String? profileId,
  }) async {
    state = const AsyncLoading();
    try {
      final client = ref.read(executionClientProvider);
      final request = ExecutionCreateRequestDto(
        workflowId: workflowId,
        targetLocale: targetLocale,
        rawInputs: {'dynamic_inputs': collectedInputs},
        profileId: profileId,
      );

      final response = await client.startExecution(request: request);

      final executionId = response.id;
      state = const AsyncValue.data(null);

      // Return the ID properly instead of throwing an Error
      return executionId;
    } catch (e, stack) {
      ref
          .read(loggerServiceProvider)
          .error('NewExecutionController', 'START_EXECUTION_FAILED', e, stack);
      state = AsyncValue.error(e, stack);
      rethrow;
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
  Workflow? _selectedWorkflow;
  String? _selectedProfileId;
  bool _autoGenerateReport = true;

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

  void _onWorkflowSelected(Workflow? workflow) {
    if (workflow == null) return;
    setState(() {
      _selectedWorkflow = workflow;
      _selectedProfileId = workflow.defaultProfileId.isNotEmpty
          ? workflow.defaultProfileId
          : null;
      _autoGenerateReport = _selectedProfileId != null;
      _compiledInputs.clear();
      _selectedFileNames.clear();

      for (final c in _textControllers.values) {
        c.dispose();
      }
      _textControllers.clear();
    });
  }

  Future<void> _pickFile(String inputKey) async {
    FilePickerResult? result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'txt', 'docx'],
      withData: true,
    );

    if (result != null && result.files.isNotEmpty) {
      final platformFile = result.files.single;
      Uint8List? fileBytes = platformFile.bytes;
      if (fileBytes == null && platformFile.path != null) {
        fileBytes = File(platformFile.path!).readAsBytesSync();
      }

      if (fileBytes != null) {
        String fileName = platformFile.name;
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

    // Validate required inputs (Fail-Fast Client-Side)
    for (final item in _selectedWorkflow!.expectedInputs) {
      final key = item.inputKey;
      final isRequired = item.required;

      if (isRequired && key.isNotEmpty) {
        final val = _compiledInputs[key];
        bool isEmpty = true;

        if (val is String && val.trim().isNotEmpty) {
          isEmpty = false;
        } else if (val is Map && val.isNotEmpty) {
          isEmpty = false;
        }

        if (isEmpty) {
          if (mounted) {
            final l10n = AppLocalizations.of(context)!;
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(l10n.fillRequiredInputs),
                backgroundColor: Theme.of(context).colorScheme.error,
                duration: const Duration(seconds: 4),
              ),
            );
          }
          return; // Halt submission
        }
      }
    }

    final workflowId = _selectedWorkflow!.id;

    try {
      final localeCode = Localizations.localeOf(context).languageCode;
      final execId = await ref
          .read(newExecutionControllerProvider.notifier)
          .startExecution(
            workflowId: workflowId,
            collectedInputs: _compiledInputs,
            targetLocale: localeCode,
            profileId: _selectedProfileId,
          );

      // Safe context routing using GoRouter Codegen
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              AppLocalizations.of(context)!.executionStartedSuccessfully,
            ),
          ),
        );
        ExecutionRoute(
          executionId: execId,
          autoGenerateReport: _autoGenerateReport,
        ).go(context);
      }
    } catch (e) {
      if (mounted) {
        final l10n = AppLocalizations.of(context)!;
        final errorMsg = AppExceptionX.extractLocalizedHint(e, l10n);

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.failedToStartExecution(errorMsg)),
            backgroundColor: Theme.of(context).colorScheme.error,
            duration: const Duration(seconds: 7),
          ),
        );
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

    return switch (asyncWorkflows) {
      AsyncData(:final value) =>
        value.isEmpty
            ? Center(
                child: Text(AppLocalizations.of(context)!.noWorkflowsAvailable),
              )
            : ListView.builder(
                itemCount: value.length,
                itemBuilder: (context, index) {
                  final wf = value[index];
                  final id = wf.id;
                  final locale = Localizations.localeOf(context).languageCode;
                  final titleStr = wf.name.get(locale);
                  final descStr = wf.description.get(locale);
                  final isSelected = _selectedWorkflow?.id == id;

                  return ListTile(
                    title: Text(
                      titleStr,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(
                      descStr,
                      maxLines: 4,
                      overflow: TextOverflow.ellipsis,
                    ),
                    selected: isSelected,
                    selectedTileColor: Theme.of(
                      context,
                    ).colorScheme.primaryContainer,
                    onTap: () => _onWorkflowSelected(wf),
                  );
                },
              ),
      AsyncError(:final error, :final stackTrace) => ErrorView(
        error: error,
        stackTrace: stackTrace,
        compact: true,
        onRetry: () => ref.invalidate(availableWorkflowsProvider),
      ),
      _ => const Center(child: CircularProgressIndicator()),
    };
  }

  Widget _buildDynamicForm(AsyncValue<void> state) {
    if (_selectedWorkflow == null) {
      return Center(
        child: Text(AppLocalizations.of(context)!.selectWorkflowPrompt),
      );
    }

    final wf = _selectedWorkflow!;
    final id = wf.id;
    final expectedInputsList = wf.expectedInputs;
    final titleStr = wf.name.get(Localizations.localeOf(context).languageCode);

    if (expectedInputsList.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.flash_on,
              size: 60,
              color: Theme.of(context).colorScheme.primary,
            ),
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

    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 1200),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                AppLocalizations.of(context)!.configureInputsFor(titleStr),
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 24),

              ...expectedInputsList.map((item) {
                final modes = item.inputModes;

                // Handle questionnaire first
                if (modes.contains('questionnaire')) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 24),
                    child: _buildQuestionnaireWidget(item),
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
                        _buildInputWidget(item, 'file'),
                        if (showText) const SizedBox(height: 16),
                      ],
                      if (showText) _buildInputWidget(item, 'text'),
                    ],
                  ),
                );
              }),

              const Divider(height: 48),

              // Epic 47 Phase 2: Orchestration decoupled these from ExecutionCreate.
              // Now managed exclusively via OutputProfile.
              // _buildStrictnessSelector(),
              // const SizedBox(height: 24),
              // _buildScoringStrategySelector(),
              // const SizedBox(height: 24),
              _buildProfileSelector(),

              const SizedBox(height: 24),

              if (state.hasError) ...[
                ErrorView(error: state.error!, compact: true),
                const SizedBox(height: 16),
              ],

              _buildSubmitButton(state),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInputWidget(ExpectedInput item, String typeHint) {
    final inputKey = item.inputKey;
    final safeHint = typeHint.toLowerCase();
    final locale = Localizations.localeOf(context).languageCode;
    final label = '${item.label.get(locale)}${item.required ? ' *' : ''}';
    final description = item.description.get(locale);

    if (safeHint == 'file' || safeHint == 'pdf') {
      final fileName = _selectedFileNames[inputKey];
      final hasFile = fileName != null;

      final theme = Theme.of(context);

      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(color: theme.colorScheme.outlineVariant),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Icon(
              hasFile ? Icons.check_circle : Icons.upload_file,
              color: hasFile
                  ? theme.colorScheme.primary
                  : theme.colorScheme.onSurfaceVariant,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  if (description.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 2, bottom: 4),
                      child: Text(
                        description,
                        style: TextStyle(
                          color: theme.colorScheme.onSurfaceVariant,
                          fontSize: 12,
                        ),
                      ),
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

    final hasFileMode = item.inputModes.contains('file');
    final textLabel = hasFileMode
        ? AppLocalizations.of(context)!.pasteTextLabel
        : label;
    final textHelper = (hasFileMode || description.isEmpty)
        ? AppLocalizations.of(context)!.inputTypeHint(typeHint)
        : description;

    return TextField(
      controller: _textControllers[inputKey],
      maxLines: 5,
      decoration: InputDecoration(
        labelText: textLabel,
        alignLabelWithHint: true,
        border: const OutlineInputBorder(),
        helperText: textHelper,
      ),
    );
  }

  Widget _buildQuestionnaireWidget(ExpectedInput item) {
    final inputKey = item.inputKey;
    final defs = item.questionnaireDefinition;
    final locale = Localizations.localeOf(context).languageCode;
    final title = item.label.get(locale);

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
            ...defs.map((def) {
              final qId = def.questionId;
              final qLabel = def.question.get(locale);

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

  Widget _buildProfileSelector() {
    if (_selectedWorkflow == null) return const SizedBox();
    final wf = _selectedWorkflow!;

    final outputProfiles = wf.outputProfiles;
    if (outputProfiles.isEmpty) {
      return const SizedBox();
    }

    final locale = Localizations.localeOf(context).languageCode;
    final List<MapEntry<String, String>> profiles = [];

    outputProfiles.forEach((key, profile) {
      profiles.add(MapEntry(key, profile.name.get(locale)));
    });

    final String defaultId = wf.defaultProfileId;

    return Card(
      elevation: 0,
      color: Theme.of(
        context,
      ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
      shape: RoundedRectangleBorder(
        side: BorderSide(color: Theme.of(context).colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.auto_awesome_mosaic,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  AppLocalizations.of(context)!.printVariantSelectorTitle,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              AppLocalizations.of(context)!.printVariantSelectorDescription,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              isExpanded: true,
              initialValue:
                  _selectedProfileId != null &&
                      outputProfiles.containsKey(_selectedProfileId)
                  ? _selectedProfileId
                  : (outputProfiles.containsKey(defaultId) ? defaultId : null),
              decoration: InputDecoration(
                filled: true,
                fillColor: Theme.of(context).colorScheme.surface,
                labelText: AppLocalizations.of(
                  context,
                )!.printVariantSelectorTitle,
                border: const OutlineInputBorder(),
              ),
              items: profiles.map((entry) {
                return DropdownMenuItem<String>(
                  value: entry.key,
                  child: Text(entry.value),
                );
              }).toList(),
              onChanged: (val) {
                if (val != null) {
                  setState(() {
                    _selectedProfileId = val;
                    _autoGenerateReport = true;
                  });
                }
              },
            ),
            const SizedBox(height: 12),
            CheckboxListTile(
              value: _autoGenerateReport,
              title: Text(
                AppLocalizations.of(context)!.autoGenerateReportLabel,
                style: Theme.of(
                  context,
                ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
              ),
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
              onChanged: (val) {
                setState(() {
                  _autoGenerateReport = val ?? false;
                });
              },
            ),
            Builder(
              builder: (context) {
                final currentId =
                    _selectedProfileId != null &&
                        outputProfiles.containsKey(_selectedProfileId)
                    ? _selectedProfileId
                    : (outputProfiles.containsKey(defaultId)
                          ? defaultId
                          : null);

                String? descriptionText;
                if (currentId != null &&
                    outputProfiles.containsKey(currentId)) {
                  final profileObj = outputProfiles[currentId]!;
                  descriptionText = profileObj.description?.get(locale);
                }

                if (descriptionText != null && descriptionText.isNotEmpty) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 16.0),
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Theme.of(
                          context,
                        ).colorScheme.tertiaryContainer.withAlpha(80),
                        border: Border(
                          left: BorderSide(
                            color: Theme.of(context).colorScheme.tertiary,
                            width: 4,
                          ),
                        ),
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            Icons.info_outline,
                            color: Theme.of(context).colorScheme.tertiary,
                            size: 20,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              descriptionText,
                              style: Theme.of(context).textTheme.bodySmall
                                  ?.copyWith(
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.onTertiaryContainer,
                                    fontStyle: FontStyle.italic,
                                  ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }
                return const SizedBox();
              },
            ),
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
}
