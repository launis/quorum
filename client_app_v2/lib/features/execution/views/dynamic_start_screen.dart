import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/workflow_client.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/shared/widgets/omni_input_box.dart';
import 'package:client_app/utils/safe_cast.dart';

/// **Dynamic Start Screen**
///
/// V2 Architecture: Renders required inputs blindly based on the backend's
/// `expected_inputs` schema. Does not use static model classes.
class DynamicStartScreen extends ConsumerStatefulWidget {
  final String workflowId;

  const DynamicStartScreen({super.key, required this.workflowId});

  @override
  ConsumerState<DynamicStartScreen> createState() => _DynamicStartScreenState();
}

class _DynamicStartScreenState extends ConsumerState<DynamicStartScreen> {
  bool _isLoading = true;
  String? _errorMsg;
  final List<Map<String, dynamic>> _expectedInputs = [];

  // The state map that holds the final user inputs mapped by semantic role keys
  final Map<String, dynamic> _collectedInputs = {};
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _fetchSchema();
  }

  Future<void> _fetchSchema() async {
    try {
      final client = ref.read(workflowClientProvider);
      final schema = await client.getWorkflowUiSchema(widget.workflowId);

      setState(() {
        final expected = SafeCast.safeList(schema['expected_inputs']);
        for (var item in expected) {
          _expectedInputs.add(SafeCast.safeMap(item));
        }
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMsg = e.toString();
        _isLoading = false;
      });
    }
  }

  void _onStart() {
    if (_formKey.currentState?.validate() ?? false) {
      // 1. Process files into base64 or pass to controller, etc.
      // Assuming executionController handles the conversion or the backend
      // accepts multipart if files are present.
      // For V2 MVP we just pass the _collectedInputs directly.
      ref
          .read(executionControllerProvider.notifier)
          .startExecution(widget.workflowId, _collectedInputs);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_errorMsg != null) {
      return Center(
        child: Text(
          'Failed to load schema: $_errorMsg',
          style: const TextStyle(color: Colors.red),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 600),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Start Workflow: ${widget.workflowId}',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 24),

                // Blindly iterate expected_inputs to build OmniInputBoxes
                ..._expectedInputs.map((details) {
                  final semanticRole = SafeCast.safeString(
                    details['input_key'],
                  );
                  final requiredParam = SafeCast.safeBool(
                    details['required'],
                    true,
                  );

                  // I18n fallback for label
                  final labelObj = SafeCast.safeMap(details['label']);
                  final translations = SafeCast.safeMap(
                    labelObj['translations'],
                  );
                  final defaultLocale = SafeCast.safeString(
                    labelObj['default_locale'],
                    'en',
                  );

                  String label = SafeCast.safeString(translations['fi']);
                  if (label.isEmpty)
                    label = SafeCast.safeString(translations[defaultLocale]);
                  if (label.isEmpty) label = semanticRole.toUpperCase();

                  final inputModes = SafeCast.safeList(details['input_modes']);
                  final isQuestionnaire = inputModes.contains('questionnaire');

                  return Padding(
                    padding: const EdgeInsets.only(bottom: 16.0),
                    child:
                        isQuestionnaire
                            ? _buildQuestionnaire(
                              semanticRole,
                              label,
                              SafeCast.safeList(
                                details['questionnaire_definition'],
                              ),
                            )
                            : OmniInputBox(
                              label: label + (requiredParam ? ' *' : ''),
                              keyName: semanticRole,
                              currentValue: _collectedInputs[semanticRole],
                              onChanged: (val) {
                                setState(() {
                                  _collectedInputs[semanticRole] = val;
                                });
                              },
                            ),
                  );
                }),

                const SizedBox(height: 32),
                FilledButton.icon(
                  onPressed: _onStart,
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('Start Execution'),
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
    String semanticRole,
    String title,
    List<dynamic> definitions,
  ) {
    if (_collectedInputs[semanticRole] == null) {
      _collectedInputs[semanticRole] = <String, dynamic>{};
    }

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
              title,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ...definitions.map((defInput) {
              final def = SafeCast.safeMap(defInput);
              final qId = SafeCast.safeString(def['question_id']);
              final qLabelObj = SafeCast.safeMap(def['question']);
              final qTranslations = SafeCast.safeMap(qLabelObj['translations']);
              final qDefaultLocale = SafeCast.safeString(
                qLabelObj['default_locale'],
                'en',
              );

              String qLabel = SafeCast.safeString(qTranslations['fi']);
              if (qLabel.isEmpty) {
                qLabel = SafeCast.safeString(qTranslations[qDefaultLocale]);
              }
              if (qLabel.isEmpty) qLabel = qId;

              return Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: TextFormField(
                  decoration: InputDecoration(
                    labelText: qLabel,
                    border: const OutlineInputBorder(),
                  ),
                  maxLines: 3,
                  onChanged: (val) {
                    setState(() {
                      (_collectedInputs[semanticRole]
                              as Map<String, dynamic>)[qId] =
                          val;
                    });
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
