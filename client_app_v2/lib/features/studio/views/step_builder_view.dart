import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';

class StepBuilderView extends ConsumerStatefulWidget {
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

  void _saveBlueprint() {
    final id = _idController.text.trim();
    if (id.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('ID is required.')));
      return;
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
      return;
    }

    _editableStep['id'] = id;
    _editableStep['slug'] = _slugController.text.trim();

    ref
        .read(stepsControllerProvider.notifier)
        .saveStep(id, _editableStep)
        .then((_) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Step saved (Optimistic update applied).'),
              ),
            );
            Navigator.of(context).pop();
          }
        })
        .catchError((e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Failed to save: $e'),
                backgroundColor: Colors.red,
              ),
            );
          }
        });
  }

  void _deleteStep(BuildContext context) {
    final id = _editableStep['id']?.toString();
    if (id == null || id.isEmpty) return;

    final l10n = AppLocalizations.of(context)!;

    showDialog(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: Text(l10n.stepDeleteConfirmTitle),
            content: Text(l10n.stepDeleteConfirmMessage(id)),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: Text(l10n.cancel),
              ),
              TextButton(
                onPressed: () {
                  Navigator.pop(ctx);
                  ref
                      .read(stepsControllerProvider.notifier)
                      .deleteStep(id)
                      .then((_) {
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Deleted successfully'),
                            ),
                          );
                          Navigator.of(context).pop();
                        }
                      })
                      .catchError((e) {
                        if (mounted) {
                          String errorMsg = e.toString();
                          if (e is AppError && e is ApiAppError) {
                            if (e.errorCode == 'RESOURCE_IN_USE') {
                              errorMsg = l10n.errorResourceInUse;
                            }
                          } else if (errorMsg.contains('RESOURCE_IN_USE') ||
                              errorMsg.contains('400')) {
                            errorMsg = l10n.errorResourceInUse;
                          }

                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(errorMsg),
                              backgroundColor: Colors.red,
                            ),
                          );
                        }
                      });
                },
                child: Text(
                  l10n.delete,
                  style: const TextStyle(color: Colors.red),
                ),
              ),
            ],
          ),
    );
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

  @override
  Widget build(BuildContext context) {
    final promptBlocksAsync = ref.watch(promptBlocksControllerProvider);
    final promptBlocks = promptBlocksAsync.value ?? [];

    final modelRegistryAsync = ref.watch(modelRegistryControllerProvider);
    final modelRegistry = modelRegistryAsync.value ?? {};
    final modelsMap = SafeCast.safeMap(modelRegistry['models']);
    final strategyKeys = modelsMap.keys.toList().cast<String>();

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
              onPressed: () => _deleteStep(context),
              icon: const Icon(Icons.delete, color: Colors.red),
              tooltip: 'Delete',
            ),
          FilledButton.icon(
            onPressed: _saveBlueprint,
            icon: const Icon(Icons.save),
            label: const Text('Save'),
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
