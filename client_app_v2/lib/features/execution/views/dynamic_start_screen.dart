import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/core/api/workflow_client.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/shared/widgets/omni_input_box.dart';

import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/models/workflow_ui_schema.dart';
import 'package:client_app/features/studio/models/workflow.dart';

part 'dynamic_start_screen.g.dart';

/// Fetches the workflow UI input schema from the backend API.
@riverpod
Future<WorkflowUiSchema> workflowUiSchema(Ref ref, String workflowId) async {
  final client = ref.watch(workflowClientProvider);
  return await client.getWorkflowUiSchema(workflowId);
}

/// Renders required workflow inputs using strongly typed [WorkflowUiSchema]
/// and [ExpectedInput] models matching the backend Pydantic SSOT contract.
class DynamicStartScreen extends HookConsumerWidget {
  final String workflowId;

  const DynamicStartScreen({super.key, required this.workflowId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final schemaAsync = ref.watch(workflowUiSchemaProvider(workflowId));
    final collectedInputs = useRef<Map<String, WorkflowInputValue>>(
      <String, WorkflowInputValue>{},
    );
    final formKey = useMemoized(() => GlobalKey<FormState>());

    return AppErrorBoundary(
      child: switch (schemaAsync) {
        AsyncData(:final value) => _buildContent(
          context,
          ref,
          value.expectedInputs,
          collectedInputs.value,
          formKey,
        ),
        AsyncError(:final error, :final stackTrace) => ErrorView(
          error: error,
          stackTrace: stackTrace,
          compact: true,
          onRetry: () => ref.invalidate(workflowUiSchemaProvider(workflowId)),
        ),
        AsyncLoading() => const Center(child: CircularProgressIndicator()),
      },
    );
  }

  void _onStart(
    BuildContext context,
    WidgetRef ref,
    Map<String, WorkflowInputValue> collectedInputs,
    GlobalKey<FormState> formKey,
  ) {
    if (formKey.currentState?.validate() ?? false) {
      final targetLocale = Localizations.localeOf(context).languageCode;
      final inputsDto = WorkflowInputs(
        language: targetLocale,
        dynamicInputs: Map<String, WorkflowInputValue>.from(collectedInputs),
      );
      ref
          .read(executionControllerProvider.notifier)
          .startExecution(workflowId, inputsDto, targetLocale: targetLocale);
    }
  }

  Widget _buildContent(
    BuildContext context,
    WidgetRef ref,
    List<ExpectedInput> expectedInputs,
    Map<String, WorkflowInputValue> collectedInputs,
    GlobalKey<FormState> formKey,
  ) {
    final locale = Localizations.localeOf(context).languageCode;
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: AppSpacing.p24,
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(
            maxWidth: AppSpacing.s300 + AppSpacing.s300,
          ),
          child: Form(
            key: formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  l10n.startWorkflowTitle(workflowId),
                  style: theme.textTheme.headlineMedium,
                  overflow: TextOverflow.ellipsis,
                ),
                AppSpacing.h24,

                // Iterate typed expectedInputs to build OmniInputBoxes
                ...expectedInputs.map((input) {
                  final semanticRole = input.inputKey;
                  final requiredParam = input.required;
                  final label = input.label.get(locale);
                  final isQuestionnaire = input.inputModes.contains(
                    'questionnaire',
                  );
                  final isAssignment = input.inputModes.contains('assignment');

                  return Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.s16),
                    child: isQuestionnaire
                        ? _buildQuestionnaire(
                            context,
                            semanticRole,
                            label,
                            input.questionnaireDefinition,
                            collectedInputs,
                          )
                        : HookBuilder(
                            builder: (ctx) {
                              final localValue = useState<Object?>(
                                collectedInputs[semanticRole]?.textValue,
                              );

                              return OmniInputBox(
                                label: label + (requiredParam ? ' *' : ''),
                                keyName: semanticRole,
                                currentValue: localValue.value,
                                icon: isAssignment
                                    ? Icons.assignment_outlined
                                    : null,
                                onChanged: (Object? val) {
                                  localValue.value = val;
                                  if (val is PlatformFile &&
                                      val.bytes != null) {
                                    collectedInputs[semanticRole] =
                                        WorkflowInputValue.file(
                                          filename: val.name,
                                          contentBase64: base64Encode(
                                            val.bytes!,
                                          ),
                                        );
                                  } else if (val is String) {
                                    collectedInputs[semanticRole] =
                                        WorkflowInputValue.text(val);
                                  } else if (val == null) {
                                    collectedInputs.remove(semanticRole);
                                  }
                                },
                              );
                            },
                          ),
                  );
                }),

                AppSpacing.h24,
                FilledButton.icon(
                  onPressed: () =>
                      _onStart(context, ref, collectedInputs, formKey),
                  icon: const Icon(Icons.play_arrow),
                  label: Text(
                    l10n.startAiExecution,
                    overflow: TextOverflow.ellipsis,
                  ),
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      vertical: AppSpacing.s16,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildQuestionnaire(
    BuildContext context,
    String semanticRole,
    String title,
    List<QuestionnaireItem> definitions,
    Map<String, WorkflowInputValue> collectedInputs,
  ) {
    if (collectedInputs[semanticRole]?.questionnaireValue == null) {
      collectedInputs[semanticRole] = const WorkflowInputValue(
        questionnaireValue: <String, String>{},
      );
    }

    final locale = Localizations.localeOf(context).languageCode;
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: theme.colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.questionnaireTitle(title),
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
              overflow: TextOverflow.ellipsis,
            ),
            AppSpacing.h16,
            ...definitions.map((def) {
              final qId = def.questionId;
              final qLabel = def.question.get(locale);

              return Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.s16),
                child: HookBuilder(
                  builder: (ctx) {
                    final controller = useTextEditingController(
                      text:
                          collectedInputs[semanticRole]
                              ?.questionnaireValue?[qId] ??
                          '',
                    );

                    return TextFormField(
                      controller: controller,
                      decoration: InputDecoration(
                        labelText: qLabel,
                        border: const OutlineInputBorder(),
                      ),
                      maxLines: 3,
                      onChanged: (val) {
                        final existingAnswers =
                            collectedInputs[semanticRole]?.questionnaireValue ??
                            const <String, String>{};
                        collectedInputs[semanticRole] =
                            WorkflowInputValue.questionnaire(<String, String>{
                              ...existingAnswers,
                              qId: val,
                            });
                      },
                    );
                  },
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}
