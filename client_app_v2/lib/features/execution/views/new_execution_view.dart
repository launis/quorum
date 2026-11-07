import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:go_router/go_router.dart';
import 'package:file_picker/file_picker.dart';

import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:client_app/core/models/enums.dart';

import 'package:client_app/router/router.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_error_ext.dart';

part 'new_execution_view.g.dart';

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
    required Map<String, WorkflowInputValue> collectedInputs,
    required String targetLocale,
    String? profileId,
  }) async {
    state = const AsyncLoading();
    try {
      final client = ref.read(executionClientProvider);
      final request = ExecutionCreateRequestDto(
        workflowId: workflowId,
        targetLocale: targetLocale,
        rawInputs: WorkflowInputs(
          language: targetLocale,
          dynamicInputs: collectedInputs,
        ),
        profileId: profileId,
      );

      final response = await client.startExecution(request: request);

      final executionId = response.id;
      state = const AsyncValue.data(null);

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

class NewExecutionView extends ConsumerStatefulWidget {
  const NewExecutionView({super.key});

  @override
  ConsumerState<NewExecutionView> createState() => _NewExecutionViewState();
}

class _NewExecutionViewState extends ConsumerState<NewExecutionView> {
  Workflow? _selectedWorkflow;
  String? _selectedProfileId;
  bool _autoGenerateReport = true;

  // Phase 5, Step 5.2: Store typed WorkflowInputValue entries instead of Map<String, Object?>.
  final Map<String, WorkflowInputValue> _compiledInputs = {};
  final Map<String, String> _selectedFileNames = {};
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
    final FilePickerResult? result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'txt', 'docx'],
      withData: true,
    );
    if (!mounted) return;

    if (result != null && result.files.isNotEmpty) {
      final platformFile = result.files.single;
      Uint8List? fileBytes = platformFile.bytes;
      if (fileBytes == null && platformFile.path != null) {
        fileBytes = File(platformFile.path!).readAsBytesSync();
      }

      if (fileBytes != null) {
        final String fileName = platformFile.name;
        final String base64String = base64Encode(fileBytes);

        setState(() {
          _compiledInputs[inputKey] = WorkflowInputValue.file(
            filename: fileName,
            contentBase64: base64String,
          );
          _selectedFileNames[inputKey] = fileName;
        });
      }
    }
  }

  void _syncTextControllersToCompiledInputs() {
    _textControllers.forEach((key, controller) {
      if (controller.text.isNotEmpty) {
        if (key.contains('|||')) {
          final parts = key.split('|||');
          final semanticRole = parts[0];
          final qId = parts[1];
          final existingAnswers =
              _compiledInputs[semanticRole]?.questionnaireValue ??
              const <String, String>{};
          _compiledInputs[semanticRole] = WorkflowInputValue.questionnaire(
            <String, String>{...existingAnswers, qId: controller.text},
          );
        } else {
          final hasFile = _compiledInputs[key]?.fileValue != null;
          if (!hasFile) {
            _compiledInputs[key] = WorkflowInputValue.text(controller.text);
          }
        }
      }
    });
  }

  Future<void> _openTaskAssignmentDialog() async {
    final workflow = _selectedWorkflow;
    if (workflow == null) return;
    _syncTextControllersToCompiledInputs();
    final localeCode = Localizations.localeOf(context).languageCode;
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => _TaskAssignmentConfigDialog(
        workflow: workflow,
        profileId: _selectedProfileId,
        initialCompiledInputs: Map<String, WorkflowInputValue>.from(
          _compiledInputs,
        ),
        targetLocale: localeCode,
      ),
    );
  }

  void _submit() async {
    if (_selectedWorkflow == null) return;

    _syncTextControllersToCompiledInputs();

    for (final item in _selectedWorkflow!.expectedInputs) {
      final key = item.inputKey;
      final isRequired = item.required;

      if (isRequired && key.isNotEmpty) {
        final val = _compiledInputs[key];
        final bool isEmpty = val == null || !val.isNotEmpty;

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
          return;
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

    return AppErrorBoundary(
      child: Scaffold(
        appBar: AppBar(
          title: Text(AppLocalizations.of(context)!.newAnalysisPipelineTitle),
          leading: BackButton(onPressed: () => context.go('/dashboard')),
        ),
        body: Row(
          children: [
            Expanded(flex: 1, child: _buildWorkflowSidebar()),
            const VerticalDivider(width: 1),
            Expanded(flex: 2, child: _buildDynamicForm(state)),
          ],
        ),
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
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
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
      AsyncLoading() => const Center(child: CircularProgressIndicator()),
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
            AppSpacing.h16,
            Text(
              AppLocalizations.of(context)!.noInputsRequired(id),
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            AppSpacing.h24,
            _buildSubmitButton(state),
          ],
        ),
      );
    }

    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 1200),
        child: SingleChildScrollView(
          padding: AppSpacing.p24,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                AppLocalizations.of(context)!.configureInputsFor(titleStr),
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              AppSpacing.h24,

              ...expectedInputsList.map((item) {
                final modes = item.inputModes;

                if (modes.contains('questionnaire')) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.s24),
                    child: _buildQuestionnaireWidget(item),
                  );
                }

                final showFile = modes.contains('file');
                final showText =
                    modes.contains('paste') ||
                    modes.contains('text') ||
                    (!showFile && !modes.contains('questionnaire'));

                return Padding(
                  padding: const EdgeInsets.only(bottom: AppSpacing.s24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (showFile) ...[
                        _buildInputWidget(item, 'file'),
                        if (showText) AppSpacing.h16,
                      ],
                      if (showText) _buildInputWidget(item, 'text'),
                    ],
                  ),
                );
              }),

              const Divider(height: 48),

              if (wf.outputProfiles.isNotEmpty) ...[
                _buildProfileSelector(wf),
                AppSpacing.h24,
              ],

              if (state.hasError) ...[
                ErrorView(error: state.error!, compact: true),
                AppSpacing.h16,
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
        padding: AppSpacing.p16,
        decoration: BoxDecoration(
          border: Border.all(color: theme.colorScheme.outlineVariant),
          borderRadius: BorderRadius.circular(AppSpacing.s8),
        ),
        child: Row(
          children: [
            Icon(
              hasFile ? Icons.check_circle : Icons.upload_file,
              color: hasFile
                  ? theme.colorScheme.primary
                  : theme.colorScheme.onSurfaceVariant,
            ),
            AppSpacing.w16,
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (description.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(
                        top: AppSpacing.s2,
                        bottom: AppSpacing.s4,
                      ),
                      child: Text(
                        description,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                  Text(
                    hasFile
                        ? AppLocalizations.of(context)!.selectedFile(fileName)
                        : AppLocalizations.of(context)!.noFileSelected,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    overflow: TextOverflow.ellipsis,
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
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppLocalizations.of(context)!.questionnaireTitle(title),
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            AppSpacing.h16,
            ...defs.map((def) {
              final qId = def.questionId;
              final qLabel = def.question.get(locale);

              final mapKey = "$inputKey|||$qId";
              if (!_textControllers.containsKey(mapKey)) {
                _textControllers[mapKey] = TextEditingController();
              }

              return Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.s16),
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

  Widget _buildProfileSelector(Workflow wf) {
    final outputProfiles = wf.outputProfiles;
    final locale = Localizations.localeOf(context).languageCode;
    final List<MapEntry<String, String>> profiles = [];

    outputProfiles.forEach((key, profile) {
      profiles.add(MapEntry(key, profile.name.get(locale)));
    });

    final String defaultId = wf.defaultProfileId;
    final currentId =
        _selectedProfileId != null &&
            outputProfiles.containsKey(_selectedProfileId)
        ? _selectedProfileId
        : (outputProfiles.containsKey(defaultId) ? defaultId : null);

    String? descriptionText;
    if (currentId != null && outputProfiles.containsKey(currentId)) {
      final profileObj = outputProfiles[currentId]!;
      descriptionText = profileObj.description?.get(locale);
    }

    return Card(
      elevation: 0,
      color: Theme.of(
        context,
      ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
      shape: RoundedRectangleBorder(
        side: BorderSide(color: Theme.of(context).colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.auto_awesome_mosaic,
                  color: Theme.of(context).colorScheme.primary,
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    AppLocalizations.of(context)!.printVariantSelectorTitle,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            AppSpacing.h8,
            Text(
              AppLocalizations.of(context)!.printVariantSelectorDescription,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
            AppSpacing.h16,
            DropdownButtonFormField<String>(
              isExpanded: true,
              initialValue: currentId,
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
                  child: Text(entry.value, overflow: TextOverflow.ellipsis),
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
            AppSpacing.h12,
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
            if (descriptionText != null && descriptionText.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: AppSpacing.s16),
                child: Container(
                  padding: AppSpacing.p12,
                  decoration: BoxDecoration(
                    color: Theme.of(
                      context,
                    ).colorScheme.tertiaryContainer.withAlpha(80),
                    border: Border(
                      left: BorderSide(
                        color: Theme.of(context).colorScheme.tertiary,
                        width: AppSpacing.s4,
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
                      AppSpacing.w12,
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

    final authUser = ref.watch(authControllerProvider).value;
    final canAssignTask =
        authUser != null &&
        (authUser.role == UserRole.manager ||
            authUser.role == UserRole.admin ||
            authUser.role == UserRole.root);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SizedBox(
          width: double.infinity,
          height: 50,
          child: FilledButton.icon(
            onPressed: _submit,
            icon: const Icon(Icons.rocket_launch),
            label: Text(
              AppLocalizations.of(context)!.startAiExecution,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Theme.of(context).colorScheme.onPrimary,
              ),
            ),
          ),
        ),
        if (canAssignTask) ...[
          AppSpacing.h12,
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              key: const Key('assign_as_task_btn'),
              onPressed: _openTaskAssignmentDialog,
              icon: const Icon(Icons.assignment_ind_outlined),
              label: Text(
                AppLocalizations.of(context)!.assignAsTimeBoundTaskBtn,
              ),
            ),
          ),
        ],
      ],
    );
  }
}

/// Task assignment configuration dialog for single and batch workflow assignments.
class _TaskAssignmentConfigDialog extends ConsumerStatefulWidget {
  final Workflow workflow;
  final String? profileId;
  final Map<String, WorkflowInputValue> initialCompiledInputs;
  final String targetLocale;

  const _TaskAssignmentConfigDialog({
    required this.workflow,
    required this.profileId,
    required this.initialCompiledInputs,
    required this.targetLocale,
  });

  @override
  ConsumerState<_TaskAssignmentConfigDialog> createState() =>
      _TaskAssignmentConfigDialogState();
}

class _TaskAssignmentConfigDialogState
    extends ConsumerState<_TaskAssignmentConfigDialog> {
  final TextEditingController _singleEmailController = TextEditingController();
  final TextEditingController _batchEmailsController = TextEditingController();
  final TextEditingController _deadlineHoursController = TextEditingController(
    text: '72',
  );
  final TextEditingController _durationMinutesController =
      TextEditingController();

  bool _isBatchMode = false;
  late Set<String> _assigneeInputKeys;
  AssignmentResultVisibility _resultVisibility =
      AssignmentResultVisibility.confirmationOnly;
  final List<ExecutionAssignmentRecipientDto> _parsedBatchRecipients = [];

  bool _isSubmitting = false;
  Object? _error;
  ExecutionAssignmentResponseDto? _createdSingle;
  ExecutionAssignmentBatchResponseDto? _createdBatch;

  @override
  void initState() {
    super.initState();
    _assigneeInputKeys = {
      for (final item in widget.workflow.expectedInputs)
        if (!widget.initialCompiledInputs.containsKey(item.inputKey))
          item.inputKey,
    };
  }

  @override
  void dispose() {
    _singleEmailController.dispose();
    _batchEmailsController.dispose();
    _deadlineHoursController.dispose();
    _durationMinutesController.dispose();
    super.dispose();
  }

  void _parseBatchText(String raw) {
    final lines = raw
        .split(RegExp(r'[\r\n,;]+'))
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .toList();
    setState(() {
      _parsedBatchRecipients
        ..clear()
        ..addAll(
          lines.map((line) => ExecutionAssignmentRecipientDto(email: line)),
        );
    });
  }

  Future<void> _importCsvFile() async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['csv', 'txt'],
      withData: true,
    );
    if (!mounted || result == null || result.files.isEmpty) return;
    final platformFile = result.files.single;
    Uint8List? bytes = platformFile.bytes;
    if (bytes == null && platformFile.path != null) {
      bytes = File(platformFile.path!).readAsBytesSync();
    }
    if (bytes == null) return;
    final content = utf8.decode(bytes);
    final rows = content
        .split(RegExp(r'\r?\n'))
        .map((r) => r.trim())
        .where((r) => r.isNotEmpty)
        .toList();
    final parsed = <ExecutionAssignmentRecipientDto>[];
    for (final row in rows) {
      final cols = row.split(',').map((c) => c.trim()).toList();
      if (cols.isEmpty || cols[0].toLowerCase() == 'email') continue;
      parsed.add(
        ExecutionAssignmentRecipientDto(
          email: cols[0],
          name: cols.length > 1 && cols[1].isNotEmpty ? cols[1] : null,
          targetLocale: cols.length > 2 && cols[2].isNotEmpty ? cols[2] : null,
        ),
      );
    }
    setState(() {
      _isBatchMode = true;
      _parsedBatchRecipients
        ..clear()
        ..addAll(parsed);
      _batchEmailsController.text = parsed.map((r) => r.email).join('\n');
    });
  }

  Future<void> _submitAssignment() async {
    final hours = int.tryParse(_deadlineHoursController.text.trim()) ?? 72;
    final hardDeadline = DateTime.now().toUtc().add(Duration(hours: hours));
    final durationMinutes = int.tryParse(
      _durationMinutesController.text.trim(),
    );
    final relativeDurationSeconds =
        durationMinutes != null && durationMinutes > 0
        ? durationMinutes * 60
        : null;

    final lockedMap = <String, WorkflowInputValue>{
      for (final entry in widget.initialCompiledInputs.entries)
        if (!_assigneeInputKeys.contains(entry.key)) entry.key: entry.value,
    };
    final lockedInputs = WorkflowInputs(
      language: widget.targetLocale,
      dynamicInputs: lockedMap,
    );

    setState(() {
      _isSubmitting = true;
      _error = null;
    });

    try {
      final client = ref.read(executionClientProvider);
      if (_isBatchMode) {
        if (_parsedBatchRecipients.isEmpty) {
          _parseBatchText(_batchEmailsController.text);
        }
        final batchRes = await client.createAssignmentBatch(
          ExecutionAssignmentBatchCreateDto(
            recipients: _parsedBatchRecipients,
            workflowId: widget.workflow.id,
            outputProfileId: widget.profileId,
            targetLocale: widget.targetLocale,
            lockedInputs: lockedInputs,
            assigneeInputKeys: _assigneeInputKeys.toList(),
            resultVisibility: _resultVisibility,
            hardDeadlineAt: hardDeadline,
            relativeDurationSeconds: relativeDurationSeconds,
          ),
        );
        if (!mounted) return;
        setState(() {
          _createdBatch = batchRes;
          _isSubmitting = false;
        });
      } else {
        final singleRes = await client.createAssignment(
          ExecutionAssignmentCreateDto(
            assignedEmail: _singleEmailController.text.trim(),
            workflowId: widget.workflow.id,
            outputProfileId: widget.profileId,
            targetLocale: widget.targetLocale,
            lockedInputs: lockedInputs,
            assigneeInputKeys: _assigneeInputKeys.toList(),
            resultVisibility: _resultVisibility,
            hardDeadlineAt: hardDeadline,
            relativeDurationSeconds: relativeDurationSeconds,
          ),
        );
        if (!mounted) return;
        setState(() {
          _createdSingle = singleRes;
          _isSubmitting = false;
        });
      }
    } catch (e, stack) {
      ref
          .read(loggerServiceProvider)
          .error(
            'TaskAssignmentConfigDialog',
            'SUBMIT_ASSIGNMENT_FAILED',
            e,
            stack,
          );
      if (!mounted) return;
      setState(() {
        _error = e;
        _isSubmitting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return AlertDialog(
      key: const Key('task_assignment_config_dialog'),
      title: Text(
        l10n.taskBuilderDialogTitle,
        style: theme.textTheme.titleLarge?.copyWith(
          fontWeight: FontWeight.bold,
        ),
      ),
      content: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 640),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Wrap(
                spacing: AppSpacing.s8,
                children: [
                  ChoiceChip(
                    key: const Key('task_builder_single_mode_chip'),
                    label: Text(l10n.taskBuilderSingleEmailLabel),
                    selected: !_isBatchMode,
                    onSelected: (_) => setState(() => _isBatchMode = false),
                  ),
                  ChoiceChip(
                    key: const Key('task_builder_batch_mode_chip'),
                    label: Text(l10n.taskBuilderBatchEmailsLabel),
                    selected: _isBatchMode,
                    onSelected: (_) => setState(() => _isBatchMode = true),
                  ),
                ],
              ),
              AppSpacing.h16,
              if (!_isBatchMode)
                TextField(
                  key: const Key('task_builder_single_email_field'),
                  controller: _singleEmailController,
                  decoration: InputDecoration(
                    labelText: l10n.taskBuilderSingleEmailLabel,
                    border: const OutlineInputBorder(),
                  ),
                )
              else ...[
                TextField(
                  key: const Key('task_builder_batch_emails_field'),
                  controller: _batchEmailsController,
                  maxLines: 3,
                  onChanged: _parseBatchText,
                  decoration: InputDecoration(
                    labelText: l10n.taskBuilderBatchEmailsLabel,
                    border: const OutlineInputBorder(),
                  ),
                ),
                AppSpacing.h8,
                OutlinedButton.icon(
                  key: const Key('task_builder_import_csv_btn'),
                  onPressed: _importCsvFile,
                  icon: const Icon(Icons.upload_file),
                  label: Text(l10n.taskBuilderUploadCsvBtn),
                ),
                if (_parsedBatchRecipients.isNotEmpty) ...[
                  AppSpacing.h8,
                  Wrap(
                    spacing: AppSpacing.s8,
                    runSpacing: AppSpacing.s4,
                    children: _parsedBatchRecipients.map((recipient) {
                      return InputChip(
                        label: Text(recipient.email),
                        onDeleted: () {
                          setState(() {
                            _parsedBatchRecipients.remove(recipient);
                          });
                        },
                      );
                    }).toList(),
                  ),
                ],
              ],
              AppSpacing.h16,
              Text(
                l10n.taskBuilderAssigneeInputsTitle,
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              AppSpacing.h8,
              Wrap(
                spacing: AppSpacing.s8,
                runSpacing: AppSpacing.s8,
                children: widget.workflow.expectedInputs.map((item) {
                  final key = item.inputKey;
                  final selected = _assigneeInputKeys.contains(key);
                  return FilterChip(
                    key: Key('task_builder_assignee_chip_$key'),
                    label: Text(key),
                    selected: selected,
                    onSelected: (val) {
                      setState(() {
                        if (val) {
                          _assigneeInputKeys.add(key);
                        } else {
                          _assigneeInputKeys.remove(key);
                        }
                      });
                    },
                  );
                }).toList(),
              ),
              AppSpacing.h16,
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      key: const Key('task_builder_deadline_hours_field'),
                      controller: _deadlineHoursController,
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(
                        labelText: l10n.taskBuilderHardDeadlineLabel,
                        border: const OutlineInputBorder(),
                      ),
                    ),
                  ),
                  AppSpacing.w12,
                  Expanded(
                    child: TextField(
                      key: const Key('task_builder_duration_minutes_field'),
                      controller: _durationMinutesController,
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(
                        labelText: l10n.taskBuilderRelativeDurationLabel,
                        border: const OutlineInputBorder(),
                      ),
                    ),
                  ),
                ],
              ),
              AppSpacing.h16,
              DropdownButtonFormField<AssignmentResultVisibility>(
                key: const Key('task_builder_visibility_dropdown'),
                isExpanded: true,
                initialValue: _resultVisibility,
                decoration: InputDecoration(
                  labelText: l10n.taskBuilderResultVisibilityLabel,
                  border: const OutlineInputBorder(),
                ),
                items: [
                  DropdownMenuItem(
                    value: AssignmentResultVisibility.confirmationOnly,
                    child: Text(
                      l10n.taskBuilderVisibilityConfirmation,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: AssignmentResultVisibility.fullReportAccess,
                    child: Text(
                      l10n.taskBuilderVisibilityFullReport,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
                onChanged: (val) {
                  if (val != null) {
                    setState(() => _resultVisibility = val);
                  }
                },
              ),
              if (_error != null) ...[
                AppSpacing.h12,
                ErrorView(error: _error!, compact: true),
              ],
              if (_createdSingle != null) ...[
                AppSpacing.h16,
                Card(
                  elevation: 2,
                  color: theme.colorScheme.primaryContainer,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppSpacing.s12),
                  ),
                  child: Padding(
                    padding: AppSpacing.p12,
                    child: Row(
                      children: [
                        Expanded(
                          child: SelectableText(
                            key: const Key('task_builder_magic_link_text'),
                            l10n.taskBuilderMagicLinkReady(
                              '/task/${_createdSingle!.id}',
                            ),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.copy),
                          onPressed: () {
                            Clipboard.setData(
                              ClipboardData(
                                text: '/task/${_createdSingle!.id}',
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                ),
              ],
              if (_createdBatch != null) ...[
                AppSpacing.h16,
                OutlinedButton.icon(
                  key: const Key('task_builder_export_csv_btn'),
                  onPressed: () {
                    final csvLines = <String>[
                      'email,assignment_id,magic_link',
                      for (final item in _createdBatch!.assignments)
                        '${item.assignedEmail},${item.id},/task/${item.id}',
                    ].join('\n');
                    Clipboard.setData(ClipboardData(text: csvLines));
                  },
                  icon: const Icon(Icons.download_outlined),
                  label: Text(l10n.taskBuilderExportCsvBtn),
                ),
              ],
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(l10n.cancel),
        ),
        OutlinedButton.icon(
          key: const Key('task_builder_submit_btn'),
          onPressed: _isSubmitting ? null : _submitAssignment,
          icon: const Icon(Icons.send_outlined),
          label: Text(
            _isBatchMode
                ? l10n.taskBuilderSubmitBatchBtn
                : l10n.taskBuilderSubmitSingleBtn,
          ),
        ),
      ],
    );
  }
}
