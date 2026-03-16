import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';

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
    final l10n = AppLocalizations.of(context)!;
    final promptBlocksAsync = ref.watch(promptBlocksControllerProvider);
    final promptBlocks = promptBlocksAsync.value ?? [];

    final modelRegistryAsync = ref.watch(modelRegistryControllerProvider);
    final modelRegistry = modelRegistryAsync.value ?? {};
    final modelsMap = SafeCast.safeMap(modelRegistry['models']);
    final strategyKeys = modelsMap.keys.toList().cast<String>();

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
              final modelStrategy = _editableStep['model_strategy'];
              if (modelStrategy == null ||
                  modelStrategy.toString().isEmpty ||
                  modelStrategy == 'null') {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text(
                      'Fail-Fast: You must explicitly select a Model Strategy.',
                    ),
                    backgroundColor: Colors.red,
                  ),
                );
                throw Exception('Missing Strategy');
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
                      const SizedBox(height: 16),
                      DropdownButtonFormField<String>(
                        decoration: const InputDecoration(
                          labelText: 'Model Strategy',
                        ),
                        initialValue:
                            strategyKeys.contains(
                                  _editableStep['model_strategy'],
                                )
                                ? _editableStep['model_strategy'] as String?
                                : null,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Fail-Fast: Strategy must be explicitly selected.';
                          }
                          return null;
                        },
                        items:
                            strategyKeys.map((key) {
                              return DropdownMenuItem(
                                value: key,
                                child: Text(key),
                              );
                            }).toList(),
                        onChanged:
                            (val) => setState(
                              () => _editableStep['model_strategy'] = val,
                            ),
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
              ...SafeCast.safeList(
                _editableStep['pre_hooks'],
              ).asMap().entries.map((entry) {
                return _buildPreHookCard(entry.key, entry.value.toString());
              }),

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
              ...SafeCast.safeList(
                _editableStep['prompt_blocks'],
              ).asMap().entries.map((entry) {
                return _buildPromptBlockCard(
                  entry.key,
                  entry.value.toString(),
                  promptBlocks,
                );
              }),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPreHookCard(int index, String hookDef) {
    final hookController = TextEditingController(text: hookDef);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
            Expanded(
              child: Focus(
                onFocusChange: (f) {
                  if (!f) {
                    final hooks = SafeCast.safeList(_editableStep['pre_hooks']);
                    hooks[index] = hookController.text;
                    _editableStep['pre_hooks'] = hooks;
                  }
                },
                child: TextField(
                  controller: hookController,
                  decoration: const InputDecoration(
                    labelText: 'Hook Name (e.g. search_hook)',
                  ),
                ),
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
    int index,
    String blockDef,
    List<Map<String, dynamic>> promptBlocks,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
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
