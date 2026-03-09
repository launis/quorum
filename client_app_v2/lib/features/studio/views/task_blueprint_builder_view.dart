import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';

class TaskBlueprintBuilderView extends ConsumerStatefulWidget {
  final Map<String, dynamic> blueprint;

  const TaskBlueprintBuilderView({super.key, required this.blueprint});

  @override
  ConsumerState<TaskBlueprintBuilderView> createState() =>
      _TaskBlueprintBuilderViewState();
}

class _TaskBlueprintBuilderViewState
    extends ConsumerState<TaskBlueprintBuilderView> {
  late Map<String, dynamic> _editableBlueprint;
  late TextEditingController _idController;
  late TextEditingController _slugController;

  @override
  void initState() {
    super.initState();
    _editableBlueprint = Map<String, dynamic>.from(widget.blueprint);
    _idController = TextEditingController(
      text: SafeCast.safeString(_editableBlueprint['id']),
    );
    _slugController = TextEditingController(
      text: SafeCast.safeString(_editableBlueprint['slug']),
    );

    if (!_editableBlueprint.containsKey('prompt_blocks')) {
      _editableBlueprint['prompt_blocks'] = [];
    }
    if (!_editableBlueprint.containsKey('pre_hooks')) {
      _editableBlueprint['pre_hooks'] = [];
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

    _editableBlueprint['id'] = id;
    _editableBlueprint['slug'] = _slugController.text.trim();

    ref
        .read(taskBlueprintsControllerProvider.notifier)
        .saveTaskBlueprint(id, _editableBlueprint)
        .then((_) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text(
                  'Task Blueprint saved (Optimistic update applied).',
                ),
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

  void _addPromptBlock() {
    setState(() {
      final blocks = SafeCast.safeList(_editableBlueprint['prompt_blocks']);
      blocks.add('');
      _editableBlueprint['prompt_blocks'] = blocks;
    });
  }

  void _addPreHook() {
    setState(() {
      final hooks = SafeCast.safeList(_editableBlueprint['pre_hooks']);
      hooks.add('');
      _editableBlueprint['pre_hooks'] = hooks;
    });
  }

  @override
  Widget build(BuildContext context) {
    final matricesAsync = ref.watch(promptBlocksControllerProvider);
    final matrices = matricesAsync.value ?? [];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Task Blueprint'),
        actions: [
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
                          labelText: 'Blueprint ID (UUID or Unique String)',
                          border: OutlineInputBorder(),
                        ),
                        enabled:
                            widget.blueprint['id'] == null ||
                            widget.blueprint['id'].toString().isEmpty,
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
                        initialData: SafeCast.safeMap(
                          _editableBlueprint['name'],
                        ),
                        onChanged: (val) => _editableBlueprint['name'] = val,
                      ),
                      const SizedBox(height: 16),
                      I18nTextField(
                        label: 'Description',
                        initialData: SafeCast.safeMap(
                          _editableBlueprint['description'],
                        ),
                        onChanged:
                            (val) => _editableBlueprint['description'] = val,
                      ),
                      const SizedBox(height: 16),
                      DropdownButtonFormField<String>(
                        decoration: const InputDecoration(
                          labelText: 'Model Strategy',
                        ),
                        initialValue:
                            const [
                                  'fast',
                                  'deep',
                                  'none',
                                ].contains(_editableBlueprint['model_strategy'])
                                ? _editableBlueprint['model_strategy']
                                    as String?
                                : null,
                        items: const [
                          DropdownMenuItem(
                            value: null,
                            child: Text("System Default"),
                          ),
                          DropdownMenuItem(
                            value: 'fast',
                            child: Text("Fast Strategy"),
                          ),
                          DropdownMenuItem(
                            value: 'deep',
                            child: Text("Deep Strategy"),
                          ),
                        ],
                        onChanged:
                            (val) => setState(
                              () => _editableBlueprint['model_strategy'] = val,
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
                _editableBlueprint['pre_hooks'],
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
                _editableBlueprint['prompt_blocks'],
              ).asMap().entries.map((entry) {
                return _buildPromptBlockCard(
                  entry.key,
                  entry.value.toString(),
                  matrices,
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
                    final hooks = SafeCast.safeList(
                      _editableBlueprint['pre_hooks'],
                    );
                    hooks[index] = hookController.text;
                    _editableBlueprint['pre_hooks'] = hooks;
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
                  SafeCast.safeList(
                    _editableBlueprint['pre_hooks'],
                  ).removeAt(index);
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
    List<Map<String, dynamic>> matrices,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
            Expanded(
              child: DropdownButtonFormField<String>(
                decoration: const InputDecoration(
                  labelText: 'Prompt Block (Matrix)',
                ),
                initialValue:
                    matrices.any((m) => m['id'] == blockDef) ? blockDef : null,
                items:
                    matrices.map((m) {
                      return DropdownMenuItem(
                        value: m['id'] as String,
                        child: Text(SafeCast.safeString(m['id'])),
                      );
                    }).toList(),
                onChanged: (val) {
                  setState(() {
                    final blocks = SafeCast.safeList(
                      _editableBlueprint['prompt_blocks'],
                    );
                    blocks[index] = val;
                    _editableBlueprint['prompt_blocks'] = blocks;
                  });
                },
              ),
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Colors.red),
              onPressed: () {
                setState(() {
                  SafeCast.safeList(
                    _editableBlueprint['prompt_blocks'],
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
