import 'dart:io';

import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import 'package:client_app/l10n/gen/app_localizations.dart';

import 'package:client_app/features/knowledge/presentation/providers/knowledge_status_provider.dart';
import 'package:client_app/core/ui/error_view.dart';
import '../controller/ingestion_controller.dart';
import '../../../models/knowledge_base.dart';

class IngestionView extends HookConsumerWidget {
  const IngestionView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ingestionState = ref.watch(ingestionControllerProvider);
    final strategiesAsync = ref.watch(knowledgeStrategiesProvider);
    final knowledgeStatusAsync = ref.watch(knowledgeStatusProvider);
    final l10n = AppLocalizations.of(context)!;

    // State for selected strategy ID
    final selectedStrategyId = useState<String?>(null);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.knowledgeBaseIngestionTitle),
        actions: [
          // Reset Button
          IconButton(
            icon: const Icon(Icons.delete_forever),
            tooltip: 'Reset Knowledge Base',
            onPressed:
                ingestionState.isLoading
                    ? null
                    : () async {
                      final confirm = await showDialog<bool>(
                        context: context,
                        builder:
                            (context) => AlertDialog(
                              title: Text(l10n.resetKnowledgeBaseTitle),
                              content: Text(
                                l10n.resetKnowledgeBaseConfirmation,
                              ),
                              actions: [
                                TextButton(
                                  onPressed:
                                      () => Navigator.pop(context, false),
                                  child: Text(l10n.cancel),
                                ),
                                TextButton(
                                  onPressed: () => Navigator.pop(context, true),
                                  child: Text(
                                    l10n.resetButton,
                                    style: const TextStyle(color: Colors.red),
                                  ),
                                ),
                              ],
                            ),
                      );

                      if (confirm == true) {
                        ref
                            .read(ingestionControllerProvider.notifier)
                            .resetKnowledgeBase();
                      }
                    },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Knowledge Base Status Banner
            knowledgeStatusAsync.when(
              data:
                  (status) => Card(
                    color:
                        status.hasDocuments
                            ? Colors.green.shade50
                            : Colors.orange.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Row(
                        children: [
                          Icon(
                            status.hasDocuments
                                ? Icons.check_circle
                                : Icons.warning_amber_rounded,
                            color:
                                status.hasDocuments
                                    ? Colors.green
                                    : Colors.orange.shade800,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  status.hasDocuments
                                      ? l10n.knowledgeActive
                                      : l10n.errKnowledgeNotIngestedTitle,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                Text(
                                  status.hasDocuments
                                      ? l10n.knowledgeStats(
                                        status.documentCount,
                                        status.precedentCount,
                                      )
                                      : l10n.errKnowledgeNotIngested,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              loading: () => const LinearProgressIndicator(),
              error: (err, _) => const SizedBox.shrink(),
            ),
            const SizedBox(height: 20),

            // Strategy Dropdown
            strategiesAsync.when(
              data:
                  (strategies) => DropdownButtonFormField<String>(
                    decoration: InputDecoration(
                      labelText: l10n.analysisLevelLabel,
                      border: const OutlineInputBorder(),
                      helperText: l10n.analysisLevelHelper,
                    ),
                    value: selectedStrategyId.value,
                    items: [
                      DropdownMenuItem(
                        value: null,
                        child: Text(l10n.analysisLevelNone),
                      ),
                      ...strategies.map(
                        (s) => DropdownMenuItem(
                          value: s.id,
                          child: Text('${s.modelName} (${s.id})'),
                        ),
                      ),
                    ],
                    onChanged:
                        ingestionState.isLoading
                            ? null
                            : (value) => selectedStrategyId.value = value,
                  ),
              loading: () => const LinearProgressIndicator(),
              error:
                  (err, _) => Text(
                    l10n.strategiesLoadError(err),
                    style: const TextStyle(color: Colors.red),
                  ),
            ),
            const SizedBox(height: 20),

            // Upload Button
            ElevatedButton.icon(
              onPressed:
                  ingestionState.isLoading
                      ? null
                      : () async {
                        final result = await FilePicker.platform.pickFiles(
                          type: FileType.custom,
                          allowedExtensions: ['docx', 'md'],
                        );

                        if (result != null &&
                            result.files.single.path != null) {
                          final file = File(result.files.single.path!);
                          ref
                              .read(ingestionControllerProvider.notifier)
                              .startIngestion(
                                file,
                                modelStrategy: selectedStrategyId.value,
                              );
                        }
                      },
              icon: const Icon(Icons.upload_file),
              label: Text(l10n.uploadDocxMd),
            ),
            const SizedBox(height: 20),

            // Status Display
            ingestionState.when(
              data: (status) {
                if (status?.status == 'failed') {
                  return ErrorView(
                    error: _getErrorMessage(status?.error ?? l10n.errorUnknown),
                    onAction:
                        () =>
                            ref
                                .read(ingestionControllerProvider.notifier)
                                .resetState(),
                    actionLabel: l10n.retry,
                  );
                }

                if (status == null) {
                  return Center(child: Text(l10n.selectFile));
                }

                return Column(
                  children: [
                    LinearProgressIndicator(value: status.progress / 100),
                    const SizedBox(height: 10),
                    Text(
                      '${status.stage} (${status.progress}%)',
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                    if (status.status == 'completed' && status.result != null)
                      _buildResultCard(context, status.result!),
                  ],
                );
              },
              error:
                  (err, st) => ErrorView(
                    error: _getErrorMessage(err),
                    onAction:
                        () =>
                            ref
                                .read(ingestionControllerProvider.notifier)
                                .resetState(),
                    actionLabel: l10n.retry,
                  ),
              loading:
                  () => Column(
                    children: [
                      const LinearProgressIndicator(),
                      const SizedBox(height: 10),
                      Text(l10n.processingStatus),
                    ],
                  ),
            ),
          ],
        ),
      ),
    );
  }

  String _getErrorMessage(dynamic error) {
    if (error is DioException) {
      final data = error.response?.data;
      if (data is Map<String, dynamic>) {
        if (data.containsKey('message')) {
          return data['message'].toString();
        }
        if (data.containsKey('detail')) {
          if (data['detail'] is String) return data['detail'];
          // Handle if detail is a Map (standard FastAPI validation error often is array, but here exception handler uses dict)
          if (data['detail'] is Map && data['detail']['message'] != null)
            return data['detail']['message'];
        }
      }
    }
    // Cleanup "AppError.server(...)" noise if present in string
    final s = error.toString();
    if (s.contains("AppError")) {
      final match = RegExp(r'message: (.*?),').firstMatch(s);
      if (match != null) return match.group(1) ?? s;
    }
    return s;
  }

  Widget _buildResultCard(BuildContext context, dynamic result) {
    final l10n = AppLocalizations.of(context)!;
    // result is IngestionSummary (Freezed)
    return Card(
      color: Colors.green.shade50,
      margin: const EdgeInsets.only(top: 20),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.ingestionComplete,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            const Divider(),
            Text(
              '${result.filename} (${(result.fileSize / 1024).toStringAsFixed(1)} KB)',
            ),
            Text(l10n.referencesCount(result.referencesCount)),
            Text(l10n.claimsCount(result.claimsCount)),
          ],
        ),
      ),
    );
  }
}
