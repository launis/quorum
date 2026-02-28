import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import '../../domain/models/model_registry.dart';

class AdHocTestPanel extends HookConsumerWidget {
  final AsyncValue<AdHocTestResult?> testResult;
  final Function(AdHocTestRequest) onRunTest;
  final String providerType;

  const AdHocTestPanel({
    super.key,
    required this.testResult,
    required this.onRunTest,
    required this.providerType,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ignore: unnecessary_non_null_assertion
    final l10n = AppLocalizations.of(context)!;

    // Hooks
    final systemCtrl = useTextEditingController(
      text: 'You are a helpful assistant.',
    );
    final userCtrl = useTextEditingController();

    // Clean layout
    return Row(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Input Column
        Expanded(
          flex: 1,
          child: DefaultTabController(
            length: 1, // Maybe expandable later? Just headers for now
            child: Card(
              margin: const EdgeInsets.all(8.0),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      l10n.testLab,
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const Divider(),

                    // Connection Info (Removed API Key override as per user request to rely on Registry)
                    // The backend will resolve keys based on the selected configuration ID.
                    Expanded(
                      child: ListView(
                        children: [
                          TextField(
                            controller: systemCtrl,
                            decoration: InputDecoration(
                              labelText: l10n.systemInstruction,
                              border: const OutlineInputBorder(),
                              alignLabelWithHint: true,
                            ),
                            maxLines: 4,
                          ),
                          const SizedBox(height: 16),
                          TextField(
                            controller: userCtrl,
                            decoration: InputDecoration(
                              labelText: l10n.userPrompt,
                              border: const OutlineInputBorder(),
                              alignLabelWithHint: true,
                            ),
                            maxLines: 8,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed:
                          testResult.isLoading
                              ? null
                              : () {
                                // Build Request
                                onRunTest(
                                  AdHocTestRequest(
                                    provider: providerType,
                                    systemInstruction: systemCtrl.text,
                                    userPrompt: userCtrl.text,
                                    modelParams: {}, // Defaults
                                    apiKey:
                                        null, // Always use backend/env resolution
                                  ),
                                );
                              },
                      icon:
                          testResult.isLoading
                              ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                              : const Icon(Icons.play_arrow),
                      label: Text(l10n.runTest),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),

        // Output Column
        Expanded(
          flex: 1,
          child: Card(
            margin: const EdgeInsets.all(8.0),
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        l10n.responseOutput,
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      if (testResult.value?.latencyMs != null)
                        Chip(
                          label: Text(
                            '${l10n.latency}: ${testResult.value!.latencyMs!.toStringAsFixed(0)}ms',
                          ),
                          backgroundColor:
                              Theme.of(context).colorScheme.primaryContainer,
                        ),
                    ],
                  ),
                  const Divider(),
                  Expanded(
                    child: testResult.when(
                      data: (data) {
                        if (data == null)
                          return Center(
                            child: Text(
                              l10n.analysisResults,
                              style: TextStyle(
                                color: Theme.of(context).disabledColor,
                              ),
                            ),
                          );

                        if (data.status == 'error') {
                          return SingleChildScrollView(
                            child: SelectableText(
                              'Error: ${data.content}',
                              style: TextStyle(
                                color: Theme.of(context).colorScheme.error,
                                fontFamily: 'monospace',
                              ),
                            ),
                          );
                        }
                        return Markdown(data: data.content, selectable: true);
                      },
                      error:
                          (e, st) => SingleChildScrollView(
                            child: SelectableText('Error: $e'),
                          ),
                      loading:
                          () =>
                              const Center(child: CircularProgressIndicator()),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}
