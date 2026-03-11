import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/studio/views/widgets/scale_editor_modal.dart';
import 'package:client_app/features/studio/views/widgets/row_editor_modal.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// **Universal Matrix Builder**
///
/// CRUD interface for editing evaluation matrices adhering strictly to the
/// De-Generator policy (`Map<String, dynamic>`).
///
/// Integrates XAI (Explainable AI) controls directly into criteria definitions
/// and provides a global "Strictness/Kireys" calibration slider.
class PromptBlockBuilderView extends ConsumerStatefulWidget {
  final Map<String, dynamic> promptBlock;

  const PromptBlockBuilderView({super.key, required this.promptBlock});

  @override
  ConsumerState<PromptBlockBuilderView> createState() =>
      _PromptBlockBuilderViewState();
}

class _PromptBlockBuilderViewState
    extends ConsumerState<PromptBlockBuilderView> {
  late Map<String, dynamic> _editablePromptBlock;
  late TextEditingController _idController;
  late double _strictnessLevel;

  @override
  void initState() {
    super.initState();
    // Deepish copy for isolated editing
    _editablePromptBlock = Map<String, dynamic>.from(widget.promptBlock);

    _idController = TextEditingController(
      text: SafeCast.safeString(_editablePromptBlock['id']),
    );

    // Parse strictness level, defaulting to 50 if missing
    _strictnessLevel =
        _editablePromptBlock['strictness_level'] != null
            ? SafeCast.safeDouble(_editablePromptBlock['strictness_level'])
            : 50.0;

    if (!_editablePromptBlock.containsKey('criteria')) {
      _editablePromptBlock['criteria'] = [];
    }
  }

  @override
  void dispose() {
    _idController.dispose();
    super.dispose();
  }

  void _savePromptBlock() {
    final id = _idController.text.trim();
    if (id.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('ID is required.')));
      return;
    }

    _editablePromptBlock['id'] = id;
    _editablePromptBlock['strictness_level'] = _strictnessLevel.round();

    // Ensure nested structures are initialized securely
    if (_editablePromptBlock['theory_grounding'] == null) {
      _editablePromptBlock.remove('theory_grounding');
    }

    ref
        .read(promptBlocksControllerProvider.notifier)
        .savePromptBlock(id, _editablePromptBlock)
        .then((_) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text(
                  'Prompt Block saved (Optimistic update applied).',
                ),
              ),
            );
            Navigator.of(context).pop();
          }
        })
        .catchError((e) {
          if (mounted) {
            String errorMsg = e.toString();
            if (e is AppError && e is ApiAppError) {
              errorMsg = e.detail;
            }
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Failed to save: $errorMsg'),
                backgroundColor: Colors.red,
              ),
            );
          }
        });
  }

  void _deletePromptBlock(BuildContext context) {
    final id = _editablePromptBlock['id']?.toString();
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
                      .read(promptBlocksControllerProvider.notifier)
                      .deletePromptBlock(id)
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

  void _addListItem(String key, Map<String, dynamic> initialValue) {
    setState(() {
      final list = SafeCast.safeList(_editablePromptBlock[key]);
      list.add(initialValue);
      _editablePromptBlock[key] = list;
    });
  }

  void _removeListItem(String key, int index) {
    setState(() {
      final list = SafeCast.safeList(_editablePromptBlock[key]);
      list.removeAt(index);
      _editablePromptBlock[key] = list;
    });
  }

  @override
  Widget build(BuildContext context) {
    final criteria = SafeCast.safeList(_editablePromptBlock['criteria']);

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: 'Back to Studio',
          onPressed: () => context.go('/admin'),
        ),
        title: const Text('Edit Prompt Block'),
        actions: [
          if (widget.promptBlock['id']?.toString().isNotEmpty == true)
            IconButton(
              onPressed: () => _deletePromptBlock(context),
              icon: const Icon(Icons.delete, color: Colors.red),
              tooltip: 'Delete',
            ),
          FilledButton.icon(
            onPressed: _savePromptBlock,
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
              // Matrix Metadata
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Prompt Block Configuration',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _idController,
                        decoration: const InputDecoration(
                          labelText: 'Unique ID (e.g. bloom_rubric_v1)',
                          border: OutlineInputBorder(),
                        ),
                        enabled:
                            widget.promptBlock['id'] == null ||
                            widget.promptBlock['id'].toString().isEmpty,
                      ),
                      const SizedBox(height: 24),
                      const Text(
                        'Strictness Level (KIREYS) [0 = Merciful, 100 = Strict]',
                      ),
                      Row(
                        children: [
                          const Text('0'),
                          Expanded(
                            child: Slider(
                              value: _strictnessLevel,
                              min: 0,
                              max: 100,
                              divisions: 100,
                              label: _strictnessLevel.round().toString(),
                              onChanged:
                                  (val) =>
                                      setState(() => _strictnessLevel = val),
                            ),
                          ),
                          const Text('100'),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // --- ROOT CONFIGURATION (NO MORE CRITERIA ARRAY) ---
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        'Prompt Block Properties',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Categories
                      DropdownButtonFormField<String>(
                        decoration: const InputDecoration(
                          labelText: 'Category',
                        ),
                        value:
                            _editablePromptBlock['category_id'] as String? ??
                            'system_rule',
                        items: const [
                          DropdownMenuItem(
                            value: 'scientific_theory',
                            child: Text('Scientific Theory'),
                          ),
                          DropdownMenuItem(
                            value: 'agent_role',
                            child: Text('Agent Role'),
                          ),
                          DropdownMenuItem(
                            value: 'system_rule',
                            child: Text('System Rule'),
                          ),
                        ],
                        onChanged:
                            (val) => setState(
                              () => _editablePromptBlock['category_id'] = val,
                            ),
                      ),
                      const SizedBox(height: 16),

                      // Label (I18N)
                      I18nTextField(
                        label: 'Block Label (Name)',
                        initialData: SafeCast.safeMap(
                          _editablePromptBlock['label'],
                        ),
                        onChanged: (val) => _editablePromptBlock['label'] = val,
                      ),
                      const SizedBox(height: 16),

                      // Description (I18N)
                      I18nTextField(
                        label: 'Detailed Prompts / Markdown Instructions',
                        initialData: SafeCast.safeMap(
                          _editablePromptBlock['description'],
                        ),
                        onChanged:
                            (val) => _editablePromptBlock['description'] = val,
                      ),
                      const SizedBox(height: 16),

                      // XAI & Constraints Container
                      Container(
                        padding: const EdgeInsets.all(12),
                        color:
                            Theme.of(
                              context,
                            ).colorScheme.surfaceContainerHighest,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            const Text(
                              'Data Type & Execution Constraints',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 12),
                            Wrap(
                              spacing: 16,
                              runSpacing: 8,
                              crossAxisAlignment: WrapCrossAlignment.center,
                              children: [
                                DropdownButton<String>(
                                  value:
                                      [
                                            'int',
                                            'float',
                                            'string',
                                            'instruction',
                                            'bool',
                                          ].contains(
                                            _editablePromptBlock['type'],
                                          )
                                          ? _editablePromptBlock['type']
                                              as String
                                          : 'instruction',
                                  items: const [
                                    DropdownMenuItem(
                                      value: 'instruction',
                                      child: Text(
                                        'Text Instruction (No JSON Output)',
                                      ),
                                    ),
                                    DropdownMenuItem(
                                      value: 'string',
                                      child: Text('String'),
                                    ),
                                    DropdownMenuItem(
                                      value: 'int',
                                      child: Text('Integer'),
                                    ),
                                    DropdownMenuItem(
                                      value: 'float',
                                      child: Text('Float'),
                                    ),
                                    DropdownMenuItem(
                                      value: 'bool',
                                      child: Text('Boolean'),
                                    ),
                                  ],
                                  onChanged:
                                      (val) => setState(
                                        () =>
                                            _editablePromptBlock['type'] = val,
                                      ),
                                ),
                                Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Checkbox(
                                      value:
                                          _editablePromptBlock['allow_decimals'] ==
                                          true,
                                      onChanged:
                                          (val) => setState(
                                            () =>
                                                _editablePromptBlock['allow_decimals'] =
                                                    val,
                                          ),
                                      // Disable checkbox if type is instruction
                                    ),
                                    const Text('Allow Decimals'),
                                  ],
                                ),
                                Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Checkbox(
                                      value:
                                          _editablePromptBlock['require_justification'] ==
                                          true,
                                      onChanged:
                                          (val) => setState(
                                            () =>
                                                _editablePromptBlock['require_justification'] =
                                                    val,
                                          ),
                                    ),
                                    const Text(
                                      'Require AI Justification (XAI)',
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 16),
                      // Theory Grounding Wrapper
                      Container(
                        padding: const EdgeInsets.all(12),
                        color:
                            Theme.of(context).colorScheme.surfaceContainerHigh,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text(
                                  'Theory Grounding (RAG)',
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                Switch(
                                  value:
                                      _editablePromptBlock['theory_grounding'] !=
                                      null,
                                  onChanged: (val) {
                                    setState(() {
                                      if (val) {
                                        _editablePromptBlock['theory_grounding'] =
                                            {
                                              'source_url': '',
                                              'citation_reference': '',
                                            };
                                      } else {
                                        _editablePromptBlock['theory_grounding'] =
                                            null;
                                        _editablePromptBlock.remove(
                                          'theory_grounding',
                                        );
                                      }
                                    });
                                  },
                                ),
                              ],
                            ),
                            if (_editablePromptBlock['theory_grounding'] !=
                                null) ...[
                              const SizedBox(height: 8),
                              // Source URL
                              TextFormField(
                                initialValue:
                                    SafeCast.safeMap(
                                      _editablePromptBlock['theory_grounding'],
                                    )['source_url']?.toString(),
                                decoration: const InputDecoration(
                                  labelText: 'Source URL (e.g. jstor.org/...)',
                                  border: UnderlineInputBorder(),
                                ),
                                onChanged: (val) {
                                  final grounding = SafeCast.safeMap(
                                    _editablePromptBlock['theory_grounding'],
                                  );
                                  grounding['source_url'] = val;
                                },
                              ),
                              const SizedBox(height: 8),
                              TextFormField(
                                initialValue:
                                    SafeCast.safeMap(
                                      _editablePromptBlock['theory_grounding'],
                                    )['citation_reference']?.toString(),
                                decoration: const InputDecoration(
                                  labelText:
                                      'Citation Reference (e.g. Kahnamen, 2011)',
                                  border: UnderlineInputBorder(),
                                ),
                                onChanged: (val) {
                                  final grounding = SafeCast.safeMap(
                                    _editablePromptBlock['theory_grounding'],
                                  );
                                  grounding['citation_reference'] = val;
                                },
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              if (_editablePromptBlock['type'] != 'instruction') ...[
                const SizedBox(height: 16),
                _buildI18nListCard('rows', 'Grid Rows (Optional)'),
                const SizedBox(height: 16),
                _buildI18nListCard('columns', 'Grid Columns (Optional)'),
                const SizedBox(height: 16),
                _buildScalesCard(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildI18nListCard(String key, String title) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: [
                    Switch(
                      value: _editablePromptBlock[key] != null,
                      onChanged: (val) {
                        setState(() {
                          if (val) {
                            _editablePromptBlock[key] = [];
                          } else {
                            _editablePromptBlock[key] = null;
                            _editablePromptBlock.remove(key);
                          }
                        });
                      },
                    ),
                    if (_editablePromptBlock[key] != null) ...[
                      const SizedBox(width: 8),
                      OutlinedButton.icon(
                        onPressed: () async {
                          final result = await showDialog<Map<String, dynamic>>(
                            context: context,
                            builder:
                                (ctx) => RowEditorModal(
                                  initialRow: const {'default_locale': ''},
                                  title: 'Add $title Item',
                                ),
                          );
                          if (result != null) {
                            _addListItem(key, result);
                          }
                        },
                        icon: const Icon(Icons.add),
                        label: const Text('Add'),
                      ),
                    ],
                  ],
                ),
              ],
            ),
            if (_editablePromptBlock[key] != null) ...[
              const SizedBox(height: 16),
              ...SafeCast.safeList(
                _editablePromptBlock[key],
              ).asMap().entries.map((entry) {
                final index = entry.key;
                final item = SafeCast.safeMap(entry.value);
                return Card(
                  margin: const EdgeInsets.only(bottom: 8.0),
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  child: ListTile(
                    title: Text(
                      item['translations']?[item['default_locale']] ??
                          item['default_locale'] ??
                          'No text',
                    ),
                    subtitle: Text('Item ${index + 1}'),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete, color: Colors.red),
                      onPressed: () => _removeListItem(key, index),
                    ),
                    onTap: () async {
                      final result = await showDialog<Map<String, dynamic>>(
                        context: context,
                        builder:
                            (ctx) => RowEditorModal(
                              initialRow: item,
                              title: 'Edit $title Item',
                            ),
                      );
                      if (result != null) {
                        setState(() {
                          final list = SafeCast.safeList(
                            _editablePromptBlock[key],
                          );
                          list[index] = result;
                          _editablePromptBlock[key] = list;
                        });
                      }
                    },
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildScalesCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'BARS Scales / Score Grades',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Row(
                  children: [
                    Switch(
                      value: _editablePromptBlock['scales'] != null,
                      onChanged: (val) {
                        setState(() {
                          if (val) {
                            _editablePromptBlock['scales'] = [];
                          } else {
                            _editablePromptBlock['scales'] = null;
                            _editablePromptBlock.remove('scales');
                          }
                        });
                      },
                    ),
                    if (_editablePromptBlock['scales'] != null) ...[
                      const SizedBox(width: 8),
                      OutlinedButton.icon(
                        onPressed: () async {
                          final result = await showDialog<Map<String, dynamic>>(
                            context: context,
                            builder:
                                (ctx) => ScaleEditorModal(
                                  initialScale: {
                                    'score': 1,
                                    'name': {'default_locale': ''},
                                    'claims': [
                                      {'default_locale': ''},
                                    ],
                                  },
                                ),
                          );
                          if (result != null) {
                            _addListItem('scales', result);
                          }
                        },
                        icon: const Icon(Icons.add),
                        label: const Text('Add Grade'),
                      ),
                    ],
                  ],
                ),
              ],
            ),
            if (_editablePromptBlock['scales'] != null) ...[
              const SizedBox(height: 16),
              ...SafeCast.safeList(
                _editablePromptBlock['scales'],
              ).asMap().entries.map((scaleEntry) {
                final sIndex = scaleEntry.key;
                final scale = SafeCast.safeMap(scaleEntry.value);
                final claimsLength = SafeCast.safeList(scale['claims']).length;
                final gradeName =
                    SafeCast.safeMap(
                      scale['name'],
                    )['translations']?[SafeCast.safeMap(
                      scale['name'],
                    )['default_locale']] ??
                    SafeCast.safeMap(scale['name'])['default_locale'] ??
                    '';

                return Card(
                  margin: const EdgeInsets.only(bottom: 8.0),
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  child: ListTile(
                    title: Text(
                      'Grade/Score: ${scale['score']} ${gradeName.isNotEmpty ? "- $gradeName" : ""}',
                    ),
                    subtitle: Text('$claimsLength Claims'),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete, color: Colors.red),
                      onPressed: () => _removeListItem('scales', sIndex),
                    ),
                    onTap: () async {
                      final result = await showDialog<Map<String, dynamic>>(
                        context: context,
                        builder: (ctx) => ScaleEditorModal(initialScale: scale),
                      );
                      if (result != null) {
                        setState(() {
                          final list = SafeCast.safeList(
                            _editablePromptBlock['scales'],
                          );
                          list[sIndex] = result;
                          _editablePromptBlock['scales'] = list;
                        });
                      }
                    },
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }
}
