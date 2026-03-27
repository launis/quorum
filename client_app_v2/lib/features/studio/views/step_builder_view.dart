import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/error/app_exception.dart';

class StepBuilderView extends StatefulHookConsumerWidget {
  final Map<String, dynamic> step;

  const StepBuilderView({super.key, required this.step});

  @override
  ConsumerState<StepBuilderView> createState() => _StepBuilderViewState();
}

class _StepBuilderViewState extends ConsumerState<StepBuilderView> {
  late Map<String, dynamic> _editableStep;
  late TextEditingController _idController;
  late TextEditingController _slugController;

  @override
  void initState() {
    super.initState();
    _editableStep = Map<String, dynamic>.from(widget.step);
    _idController = TextEditingController(
      text: SafeCast.safeString(_editableStep['id']),
    );
    _slugController = TextEditingController(
      text: SafeCast.safeString(_editableStep['slug']),
    );

    if (!_editableStep.containsKey('prompt_blocks')) {
      _editableStep['prompt_blocks'] = [];
    }
    if (!_editableStep.containsKey('pre_hooks')) {
      _editableStep['pre_hooks'] = [];
    }
  }

  @override
  void dispose() {
    _idController.dispose();
    _slugController.dispose();
    super.dispose();
  }

  void _addPromptBlock() {
    setState(() {
      final blocks = SafeCast.safeList(_editableStep['prompt_blocks']);
      blocks.add('');
      _editableStep['prompt_blocks'] = blocks;
    });
  }

  void _addPreHook() {
    setState(() {
      final hooks = SafeCast.safeList(_editableStep['pre_hooks']);
      hooks.add('');
      _editableStep['pre_hooks'] = hooks;
    });
  }

  void _deleteStep(BuildContext context, MutationState<void> deleteMutation) {
    final id = _idController.text.trim();
    if (id.isEmpty) return;

    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('Delete Step'),
            content: Text('Are you sure you want to delete step "$id"?'),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Cancel'),
              ),
              MutationButton<void>(
                mutation: deleteMutation,
                label: 'Delete',
                action: () async {
                  await ref
                      .read(stepsControllerProvider.notifier)
                      .deleteStep(id);
                },
              ),
            ],
          ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final promptBlocksAsync = ref.watch(promptBlocksControllerProvider);

    // Absolute Fail-Fast: Do not use `?? []` to mask data loading or corruption.
    if (promptBlocksAsync.hasError) throw promptBlocksAsync.error!;
    if (!promptBlocksAsync.hasValue) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final promptBlocks = promptBlocksAsync.value!;

    final saveMutation = useMutation<void>(
      onSuccess: (_) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Step saved (Optimistic).')),
          );
          Navigator.of(context).pop();
        }
      },
      onError: (e) {
        if (mounted) {
          final l10n = AppLocalizations.of(context)!;
          final errorMsg = AppExceptionX.extractLocalizedHint(e, l10n);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('${l10n.errorUnknown}: $errorMsg'),
              backgroundColor: Colors.red,
            ),
          );
        }
      },
    );

    final deleteMutation = useMutation<void>(
      onSuccess: (_) {
        if (mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text('Deleted successfully')));
          Navigator.of(context).pop();
        }
      },
      onError: (e) {
        if (mounted) {
          final l10n = AppLocalizations.of(context)!;
          final errorMsg = AppExceptionX.extractLocalizedHint(e, l10n);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(errorMsg), backgroundColor: Colors.red),
          );
        }
      },
    );

    final validateMutation = useMutation<Map<String, dynamic>>(
      onSuccess: (data) {
        if (mounted) {
          final rendered = data['rendered_prompt']?.toString();
          if (rendered == null) {
            throw AppException.validation(
              'Simulator did not return rendered_prompt. Data corruption detected.',
            );
          }
          showDialog(
            context: context,
            builder:
                (ctx) => AlertDialog(
                  title: const Text('Simulator Output'),
                  content: SizedBox(
                    width: double.maxFinite,
                    child: SingleChildScrollView(
                      child: Text(
                        rendered,
                        style: const TextStyle(fontFamily: 'monospace'),
                      ),
                    ),
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(ctx),
                      child: const Text('Close'),
                    ),
                  ],
                ),
          );
        }
      },
      onError: (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Simulation Error: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      },
    );

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: 'Back to Studio',
          onPressed: () => context.go('/admin'),
        ),
        title: const Text('Edit Step'),
        actions: [
          if (widget.step['id']?.toString().isNotEmpty == true)
            IconButton(
              onPressed: () => _deleteStep(context, deleteMutation),
              icon: const Icon(Icons.delete, color: Colors.red),
              tooltip: 'Delete',
            ),
          IconButton(
            onPressed:
                validateMutation.isLoading
                    ? null
                    : () {
                      validateMutation.mutate(() async {
                        final payload = {
                          'step': _editableStep,
                          'mock_inputs': <String, dynamic>{},
                        };
                        return await ref
                            .read(stepsControllerProvider.notifier)
                            .simulateStep(payload);
                      });
                    },
            icon:
                validateMutation.isLoading
                    ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                    : const Icon(Icons.bug_report, color: Colors.green),
            tooltip: 'Simulate Step',
          ),
          MutationButton<void>(
            mutation: saveMutation,
            label: 'Save',
            icon: Icons.save,
            action: () async {
              final id = _idController.text.trim();
              if (id.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('ID is required.')),
                );
                throw Exception('ID is required');
              }

              _editableStep['id'] = id;
              _editableStep['slug'] = _slugController.text.trim();
              await ref
                  .read(stepsControllerProvider.notifier)
                  .saveStep(id, _editableStep);
            },
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Metadata
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Configuration',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _idController,
                        decoration: const InputDecoration(
                          labelText: 'Step ID (UUID or Unique String)',
                          border: OutlineInputBorder(),
                        ),
                        enabled:
                            widget.step['id'] == null ||
                            widget.step['id'].toString().isEmpty,
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _slugController,
                        decoration: const InputDecoration(
                          labelText: 'Slug (e.g., task_guard)',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 16),
                      I18nTextField(
                        label: 'Name',
                        initialData: SafeCast.safeMap(_editableStep['name']),
                        onChanged: (val) => _editableStep['name'] = val,
                      ),
                      const SizedBox(height: 16),
                      I18nTextField(
                        label: 'Description',
                        initialData: SafeCast.safeMap(
                          _editableStep['description'],
                        ),
                        onChanged: (val) => _editableStep['description'] = val,
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // pre_hooks
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Pre Hooks',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  OutlinedButton.icon(
                    onPressed: _addPreHook,
                    icon: const Icon(Icons.add),
                    label: const Text('Add Hook'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              ReorderableListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: SafeCast.safeList(_editableStep['pre_hooks']).length,
                onReorder: (oldIndex, newIndex) {
                  setState(() {
                    if (oldIndex < newIndex) newIndex -= 1;
                    final hooks = SafeCast.safeList(_editableStep['pre_hooks']);
                    final item = hooks.removeAt(oldIndex);
                    hooks.insert(newIndex, item);
                    _editableStep['pre_hooks'] = hooks;
                  });
                },
                itemBuilder: (context, index) {
                  final hooks = SafeCast.safeList(_editableStep['pre_hooks']);
                  return _buildPreHookCard(
                    ValueKey('hook_$index\_${hooks[index]}'),
                    index,
                    hooks[index].toString(),
                  );
                },
              ),

              const SizedBox(height: 24),

              // prompt_blocks
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Prompt Blocks',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  OutlinedButton.icon(
                    onPressed: _addPromptBlock,
                    icon: const Icon(Icons.add),
                    label: const Text('Add Prompt Block'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              ReorderableListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount:
                    SafeCast.safeList(_editableStep['prompt_blocks']).length,
                onReorder: (oldIndex, newIndex) {
                  setState(() {
                    if (oldIndex < newIndex) newIndex -= 1;
                    final blocks = SafeCast.safeList(
                      _editableStep['prompt_blocks'],
                    );
                    final item = blocks.removeAt(oldIndex);
                    blocks.insert(newIndex, item);
                    _editableStep['prompt_blocks'] = blocks;
                  });
                },
                itemBuilder: (context, index) {
                  final blocks = SafeCast.safeList(
                    _editableStep['prompt_blocks'],
                  );
                  return _buildPromptBlockCard(
                    ValueKey('block_$index\_${blocks[index]}'),
                    index,
                    blocks[index].toString(),
                    promptBlocks,
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPreHookCard(Key key, int index, String hookDef) {
    final knownHooks = [
      'search_hook',
      'memory_hook',
      'validation_hook',
      'score_hook',
    ];
    final bool isCustom = hookDef.isNotEmpty && !knownHooks.contains(hookDef);

    return Card(
      key: key,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
            const Padding(
              padding: EdgeInsets.only(right: 8.0),
              child: Icon(Icons.drag_indicator, color: Colors.grey),
            ),
            Expanded(
              child: DropdownButtonFormField<String>(
                decoration: const InputDecoration(
                  labelText: 'Pre-Execution Hook Engine',
                ),
                initialValue: hookDef.isEmpty ? null : hookDef,
                items: [
                  const DropdownMenuItem(
                    value: 'search_hook',
                    child: Text('Tavily Web Search (search_hook)'),
                  ),
                  const DropdownMenuItem(
                    value: 'memory_hook',
                    child: Text('Contextual Memory (memory_hook)'),
                  ),
                  const DropdownMenuItem(
                    value: 'validation_hook',
                    child: Text('Strict Validation (validation_hook)'),
                  ),
                  const DropdownMenuItem(
                    value: 'score_hook',
                    child: Text('Grading Matrix (score_hook)'),
                  ),
                  if (isCustom)
                    DropdownMenuItem(
                      value: hookDef,
                      child: Text('Legacy: $hookDef'),
                    ),
                ],
                onChanged: (val) {
                  if (val != null) {
                    setState(() {
                      final hooks = SafeCast.safeList(
                        _editableStep['pre_hooks'],
                      );
                      hooks[index] = val;
                      _editableStep['pre_hooks'] = hooks;
                    });
                  }
                },
              ),
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Colors.red),
              onPressed: () {
                setState(() {
                  SafeCast.safeList(_editableStep['pre_hooks']).removeAt(index);
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPromptBlockCard(
    Key key,
    int index,
    String blockDef,
    List<Map<String, dynamic>> promptBlocks,
  ) {
    return Card(
      key: key,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
            const Padding(
              padding: EdgeInsets.only(right: 8.0),
              child: Icon(Icons.drag_indicator, color: Colors.grey),
            ),
            Expanded(
              child: DropdownButtonFormField<String>(
                decoration: const InputDecoration(labelText: 'Prompt Block'),
                initialValue:
                    promptBlocks.any((m) => m['id'] == blockDef)
                        ? blockDef
                        : null,
                items:
                    promptBlocks.map((m) {
                      return DropdownMenuItem(
                        value: m['id'] as String,
                        child: Text(SafeCast.safeString(m['id'])),
                      );
                    }).toList(),
                onChanged: (val) {
                  setState(() {
                    final blocks = SafeCast.safeList(
                      _editableStep['prompt_blocks'],
                    );
                    blocks[index] = val;
                    _editableStep['prompt_blocks'] = blocks;
                  });
                },
              ),
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Colors.red),
              onPressed: () {
                setState(() {
                  SafeCast.safeList(
                    _editableStep['prompt_blocks'],
                  ).removeAt(index);
                });
              },
            ),
          ],
        ),
      ),
    );
  }
}
