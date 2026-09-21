import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/api/workflow_client.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/shared/widgets/omni_input_box.dart';

import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/models/workflow_ui_schema.dart';
import 'package:client_app/features/studio/models/workflow.dart';

// Riverpod Provider for UI Schema. Replaces manual `_fetchSchema()` side-effects.
final workflowUiSchemaProvider = FutureProvider.autoDispose
    .family<WorkflowUiSchema, String>((ref, workflowId) async {
      final client = ref.watch(workflowClientProvider);
      return await client.getWorkflowUiSchema(workflowId);
    });

/// **Dynamic Start Screen**
///
/// V2 Architecture: Renders required inputs using strongly typed `WorkflowUiSchema`
/// and `ExpectedInput` models matching the backend Pydantic SSOT contract.
/// Complies with Riverpod and No-String mandates.
class DynamicStartScreen extends HookConsumerWidget {
  final String workflowId;

  const DynamicStartScreen({super.key, required this.workflowId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final schemaAsync = ref.watch(workflowUiSchemaProvider(workflowId));
    final collectedInputs = useRef<Map<String, dynamic>>({});
    final formKey = useMemoized(() => GlobalKey<FormState>());

    return switch (schemaAsync) {
      AsyncData(:final value) => _buildContent(
        context,
        ref,
        value.expectedInputs,
        collectedInputs.value,
        formKey,
      ),
      AsyncError(:final error) => ErrorView(
        error: AppLocalizations.of(
          context,
        )!.failedToLoadSchema(error.toString()),
        compact: true,
      ),
      _ => const Center(child: CircularProgressIndicator()),
    };
  }

  void _onStart(
    BuildContext context,
    WidgetRef ref,
    Map<String, dynamic> collectedInputs,
    GlobalKey<FormState> formKey,
  ) {
    if (formKey.currentState?.validate() ?? false) {
      // 1. Process files into base64 for the backend deterministic input hook.
      final Map<String, dynamic> processedInputs = {};

      collectedInputs.forEach((key, value) {
        if (value is PlatformFile && value.bytes != null) {
          processedInputs[key] = {
            'filename': value.name,
            'content_base64': base64Encode(value.bytes!),
          };
        } else {
          processedInputs[key] = value;
        }
      });

      final targetLocale = Localizations.localeOf(context).languageCode;
      ref
          .read(executionControllerProvider.notifier)
          .startExecution(
            workflowId,
            processedInputs,
            targetLocale: targetLocale,
          );
    }
  }

  Widget _buildContent(
    BuildContext context,
    WidgetRef ref,
    List<ExpectedInput> expectedInputs,
    Map<String, dynamic> collectedInputs,
    GlobalKey<FormState> formKey,
  ) {
    final locale = Localizations.localeOf(context).languageCode;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 600),
          child: Form(
            key: formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  AppLocalizations.of(context)!.startWorkflowTitle(workflowId),
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 24),

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
                    padding: const EdgeInsets.only(bottom: 16.0),
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
                              final localValue = useState<dynamic>(
                                collectedInputs[semanticRole],
                              );

                              return OmniInputBox(
                                label: label + (requiredParam ? ' *' : ''),
                                keyName: semanticRole,
                                currentValue: localValue.value,
                                icon: isAssignment
                                    ? Icons.assignment_outlined
                                    : null,
                                onChanged: (val) {
                                  localValue.value = val;
                                  collectedInputs[semanticRole] = val;
                                },
                              );
                            },
                          ),
                  );
                }),

                const SizedBox(height: 32),
                FilledButton.icon(
                  onPressed: () =>
                      _onStart(context, ref, collectedInputs, formKey),
                  icon: const Icon(Icons.play_arrow),
                  label: Text(AppLocalizations.of(context)!.startAiExecution),
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
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
    Map<String, dynamic> collectedInputs,
  ) {
    if (collectedInputs[semanticRole] == null) {
      collectedInputs[semanticRole] = <String, dynamic>{};
    }

    final locale = Localizations.localeOf(context).languageCode;

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
              // Using questionnaireTitle ARB key from execution UI
              AppLocalizations.of(context)!.questionnaireTitle(title),
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ...definitions.map((def) {
              final qId = def.questionId;
              final qLabel = def.question.get(locale);

              return Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: HookBuilder(
                  builder: (ctx) {
                    final controller = useTextEditingController(
                      text:
                          (collectedInputs[semanticRole]
                                  as Map<String, dynamic>)[qId]
                              ?.toString() ??
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
                        (collectedInputs[semanticRole]
                                as Map<String, dynamic>)[qId] =
                            val;
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
