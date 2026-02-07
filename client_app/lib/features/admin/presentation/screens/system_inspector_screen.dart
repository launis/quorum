import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/features/orchestration/domain/models/workflow.dart';
import 'package:client_app/features/orchestration/presentation/providers/workflow_controller.dart';
import 'package:client_app/features/admin/domain/models/system_preview.dart';
import 'package:client_app/features/admin/presentation/providers/system_providers.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

part 'system_inspector_screen.g.dart';

/// **Step Preview Provider**
///
/// Fetches the preview for a single step.
@riverpod
Future<SystemPreview> stepPreview(Ref ref, String stepId) async {
  final repository = ref.watch(systemRepositoryProvider);
  final result = await repository.getStepPreview(stepId);
  return result.match((l) => throw l, (r) => r);
}

/// **Chain Preview Provider**
///
/// Fetches the full chain preview for a workflow.
@riverpod
Future<ChainPreview> chainPreview(Ref ref, String workflowId) async {
  final repository = ref.watch(systemRepositoryProvider);
  final result = await repository.getChainPreview(workflowId);
  return result.match((l) => throw l, (r) => r);
}

class SystemInspectorScreen extends ConsumerStatefulWidget {
  const SystemInspectorScreen({super.key});

  @override
  ConsumerState<SystemInspectorScreen> createState() =>
      _SystemInspectorScreenState();
}

class _SystemInspectorScreenState extends ConsumerState<SystemInspectorScreen> {
  Workflow? _selectedWorkflow;

  @override
  Widget build(BuildContext context) {
    final workflowsAsync = ref.watch(workflowListProvider);
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(title: Text(l10n.systemInspectorTitle)),
      body: workflowsAsync.when(
        data: (workflows) {
          return Row(
            children: [
              // Left Column: List of Workflows
              SizedBox(
                width: 300,
                child: ListView.builder(
                  itemCount: workflows.length,
                  itemBuilder: (context, index) {
                    final workflow = workflows[index];
                    final isSelected = _selectedWorkflow?.id == workflow.id;
                    return ListTile(
                      title: Text(workflow.name),
                      subtitle: Text(workflow.id),
                      selected: isSelected,
                      selectedTileColor:
                          Theme.of(context).colorScheme.surfaceContainerHighest,
                      onTap: () {
                        setState(() {
                          _selectedWorkflow = workflow;
                        });
                      },
                    );
                  },
                ),
              ),
              const VerticalDivider(width: 1),
              // Right Column: Details
              Expanded(
                child:
                    _selectedWorkflow == null
                        ? Center(child: Text(l10n.selectWorkflowRequired))
                        : _InspectorDetails(workflow: _selectedWorkflow!),
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(child: Text('Error: $err')),
      ),
    );
  }
}

class _InspectorDetails extends StatelessWidget {
  final Workflow workflow;

  const _InspectorDetails({required this.workflow});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return DefaultTabController(
      length: 4,
      child: Column(
        children: [
          TabBar(
            tabs: [
              Tab(text: l10n.workflowConfig),
              Tab(text: l10n.studioStepsTitle),
              Tab(text: l10n.stepPreview),
              Tab(text: l10n.exportTab),
            ],
          ),
          Expanded(
            child: TabBarView(
              children: [
                _ConfigTab(workflow: workflow),
                _StepsTab(workflow: workflow),
                _PreviewTab(key: ValueKey(workflow.id), workflow: workflow),
                _ExportTab(key: ValueKey(workflow.id), workflow: workflow),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ConfigTab extends StatelessWidget {
  final Workflow workflow;

  const _ConfigTab({required this.workflow});

  @override
  Widget build(BuildContext context) {
    final jsonString = const JsonEncoder.withIndent(
      '  ',
    ).convert(workflow.toJson());
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: SelectableText(
        jsonString,
        style: const TextStyle(fontFamily: 'monospace'),
      ),
    );
  }
}

class _StepsTab extends StatelessWidget {
  final Workflow workflow;

  const _StepsTab({required this.workflow});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: workflow.steps.length,
      itemBuilder: (context, index) {
        final step = workflow.steps[index];
        return ListTile(
          title: Text(step.id),
          subtitle: Text(step.taskKey),
          leading: CircleAvatar(child: Text('${index + 1}')),
        );
      },
    );
  }
}

class _PreviewTab extends ConsumerStatefulWidget {
  final Workflow workflow;

  const _PreviewTab({super.key, required this.workflow});

  @override
  ConsumerState<_PreviewTab> createState() => _PreviewTabState();
}

class _PreviewTabState extends ConsumerState<_PreviewTab> {
  String? _selectedStepId;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    // Removed unused theme variable

    // Filter steps that have an ID (should be all)
    final steps = widget.workflow.steps;

    // Safety check: deeply validate that _selectedStepId is actually present in the current steps.
    // If we switched workflows and state persisted (despite Key), this prevents a crash.
    String? effectiveSelectedStepId = _selectedStepId;
    if (effectiveSelectedStepId != null && !steps.any((s) => s.id == effectiveSelectedStepId)) {
      effectiveSelectedStepId = null;
      // Schedule a cleanup to sync state
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted && _selectedStepId != null) {
          setState(() {
            _selectedStepId = null;
          });
        }
      });
    }

    return Column(
      children: [
        // Dropdown
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: DropdownButtonFormField<String>(
            // ignore: deprecated_member_use
            value: effectiveSelectedStepId,
            decoration: InputDecoration(
              labelText: l10n.selectStepPlaceholder,
              border: const OutlineInputBorder(),
            ),
            items:
                steps.map((step) {
                  return DropdownMenuItem(
                    value: step.id,
                    child: Text('${step.id} (${step.taskKey})'),
                  );
                }).toList(),
            onChanged: (value) {
              setState(() {
                _selectedStepId = value;
              });
            },
          ),
        ),
        // Content
        Expanded(
          child:
              _selectedStepId == null
                  ? const Center(child: Text(''))
                  : _StepPreviewContent(stepId: _selectedStepId!),
        ),
      ],
    );
  }
}

class _StepPreviewContent extends ConsumerWidget {
  final String stepId;

  const _StepPreviewContent({required this.stepId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final previewAsync = ref.watch(stepPreviewProvider(stepId));
    final l10n = AppLocalizations.of(context)!;

    return previewAsync.when(
      data: (preview) {
        return SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _SectionHeader(title: l10n.systemInstruction),
              const SizedBox(height: 8),
              _CodeBlock(content: preview.systemInstruction),
              const SizedBox(height: 24),
              _SectionHeader(title: l10n.userPrompt),
              const SizedBox(height: 8),
              _CodeBlock(content: preview.userPrompt),
            ],
          ),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error:
          (err, stack) => Center(
            child: Text(
              'Error: $err',
              style: const TextStyle(color: Colors.red),
            ),
          ),
    );
  }
}

class _ExportTab extends ConsumerWidget {
  final Workflow workflow;

  const _ExportTab({super.key, required this.workflow});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // We only fetch when the user asks, or we can fetch immediately?
    // Prompt says: "Add a Button 'Generate Full Chain'. On click, trigger..."
    // So we need state to manage when to fetch.
    return _ExportTabContent(workflow: workflow);
  }
}

class _ExportTabContent extends ConsumerStatefulWidget {
  final Workflow workflow;
  const _ExportTabContent({required this.workflow});

  @override
  ConsumerState<_ExportTabContent> createState() => _ExportTabContentState();
}

class _ExportTabContentState extends ConsumerState<_ExportTabContent> {
  bool _generated = false;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    if (!_generated) {
      return Center(
        child: FilledButton.icon(
          onPressed: () {
            setState(() {
              _generated = true;
            });
          },
          icon: const Icon(Icons.download),
          label: Text(l10n.generateChain),
        ),
      );
    }

    final chainAsync = ref.watch(chainPreviewProvider(widget.workflow.id));

    return chainAsync.when(
      data: (preview) {
        return Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  OutlinedButton.icon(
                    onPressed: () {
                      Clipboard.setData(
                        ClipboardData(text: preview.markdownContent),
                      );
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(l10n.copiedToClipboard)),
                      );
                    },
                    icon: const Icon(Icons.copy),
                    label: Text(l10n.copyToClipboard),
                  ),
                ],
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16.0),
                child: _CodeBlock(content: preview.markdownContent),
              ),
            ),
          ],
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error:
          (err, stack) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text('Error: $err', style: const TextStyle(color: Colors.red)),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () {
                    ref.invalidate(chainPreviewProvider(widget.workflow.id));
                  },
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: Theme.of(context).textTheme.titleMedium?.copyWith(
        fontWeight: FontWeight.bold,
        color: Theme.of(context).colorScheme.primary,
      ),
    );
  }
}

class _CodeBlock extends StatelessWidget {
  final String content;
  const _CodeBlock({required this.content});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).colorScheme.outlineVariant),
      ),
      child: SelectableText(
        content,
        style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
      ),
    );
  }
}
