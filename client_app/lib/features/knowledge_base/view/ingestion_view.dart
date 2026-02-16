import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import 'package:client_app/l10n/gen/app_localizations.dart';

import '../controller/ingestion_controller.dart';
import '../../../models/knowledge_base.dart';

class IngestionView extends HookConsumerWidget {
  const IngestionView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ingestionState = ref.watch(ingestionControllerProvider);
    final strategiesAsync = ref.watch(knowledgeStrategiesProvider);
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
            onPressed: ingestionState.isLoading
                ? null
                : () async {
                    final confirm = await showDialog<bool>(
                      context: context,
                      builder: (context) => AlertDialog(
            title: Text(l10n.resetKnowledgeBaseTitle),
            content: Text(l10n.resetKnowledgeBaseConfirmation),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: Text(l10n.cancel),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context, true),
                child: Text(l10n.resetButton,
                    style: const TextStyle(color: Colors.red)),
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
      // Strategy Dropdown
      strategiesAsync.when(
        data: (strategies) => DropdownButtonFormField<String>(
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
            ...strategies.map((s) => DropdownMenuItem(
                  value: s.id,
                  child: Text('${s.modelName} (${s.id})'),
                )),
          ],
          onChanged: ingestionState.isLoading
              ? null
              : (value) => selectedStrategyId.value = value,
        ),
        loading: () => const LinearProgressIndicator(),
        error: (err, _) => Text(l10n.strategiesLoadError(err),
            style: const TextStyle(color: Colors.red)),
      ),
      const SizedBox(height: 20),
      
      // Upload Button
      ElevatedButton.icon(
        onPressed: ingestionState.isLoading
            ? null
            : () async {
                final result = await FilePicker.platform.pickFiles(
                  type: FileType.custom,
                  allowedExtensions: ['docx', 'md'],
                );

                if (result != null && result.files.single.path != null) {
                  final file = File(result.files.single.path!);
                  ref
                      .read(ingestionControllerProvider.notifier)
                      .startIngestion(
                        file, 
                        modelStrategy: selectedStrategyId.value
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
              if (status.status == 'failed')
                Text(
                  l10n.submissionFailed(status.error ?? l10n.errorUnknown),
                  style: const TextStyle(color: Colors.red),
                ),
            ],
          );
        },
        error: (err, st) => Text(
          l10n.submissionFailed(err),
          style: const TextStyle(color: Colors.red),
        ),
        loading: () => Column(
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
            Text('${result.filename} (${(result.fileSize / 1024).toStringAsFixed(1)} KB)'),
            Text(l10n.referencesCount(result.referencesCount)),
            Text(l10n.claimsCount(result.claimsCount)),
          ],
        ),

      ),
    );
  }
}
