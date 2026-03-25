import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/features/studio/views/widgets/scale_editor_modal.dart';
import 'package:client_app/features/studio/views/widgets/row_editor_modal.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/models/prompt_block_category.dart';

/// **Universal Matrix Builder**
///
/// CRUD interface for editing evaluation matrices adhering strictly to the
/// De-Generator policy (`Map<String, dynamic>`).
///
/// Integrates XAI (Explainable AI) controls directly into criteria definitions
/// and provides a global "Strictness/Kireys" calibration slider.
class PromptBlockBuilderView extends ConsumerWidget {
  final String? id;
  final String? slug;
  final Map<String, dynamic>? initialData;

  const PromptBlockBuilderView({super.key, this.id, this.slug, this.initialData});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (initialData != null && initialData!.isNotEmpty) {
      return _PromptBlockBuilderForm(promptBlock: initialData!);
    }
    if (id == null || id!.isEmpty || id == 'new') {
      return const _PromptBlockBuilderForm(promptBlock: {});
    }

    final asyncData = ref.watch(promptBlockByIdProvider(id!));
    return asyncData.when(
      data: (matrix) => _PromptBlockBuilderForm(promptBlock: matrix),
      loading:
          () =>
              const Scaffold(body: Center(child: CircularProgressIndicator())),
      error:
          (e, st) => ErrorView(
            error: e,
            stackTrace: st,
            onRetry: () => ref.invalidate(promptBlockByIdProvider(id!)),
          ),
    );
  }
}

class _PromptBlockBuilderForm extends StatefulHookConsumerWidget {
  final Map<String, dynamic> promptBlock;

  const _PromptBlockBuilderForm({required this.promptBlock});

  @override
  ConsumerState<_PromptBlockBuilderForm> createState() =>
      _PromptBlockBuilderFormState();
}

class _PromptBlockBuilderFormState
    extends ConsumerState<_PromptBlockBuilderForm> {
  late Map<String, dynamic> _editablePromptBlock;
  late TextEditingController _idController;

  @override
  void initState() {
    super.initState();
    // Deepish copy for isolated editing
    _editablePromptBlock = Map<String, dynamic>.from(widget.promptBlock);

    _idController = TextEditingController(
      text: SafeCast.safeString(_editablePromptBlock['id']),
    );

    // Deprecated 'criteria' array has been removed from V2 architecture

    // "The English-Only Mandate": Ensure new blocks have required 'en' structure
    if (!_editablePromptBlock.containsKey('label')) {
      _editablePromptBlock['label'] = {
        'default_locale': 'en',
        'translations': <String, dynamic>{'en': ''},
      };
    }
    if (!_editablePromptBlock.containsKey('description')) {
      _editablePromptBlock['description'] = {
        'default_locale': 'en',
        'translations': <String, dynamic>{'en': ''},
      };
    }
  }

  @override
  void dispose() {
    _idController.dispose();
    super.dispose();
  }

  void _deletePromptBlock(BuildContext context, MutationState<void> deleteMut) {
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
                  deleteMut.mutate(
                    () => ref
                        .read(promptBlocksControllerProvider.notifier)
                        .deletePromptBlock(id),
                  );
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
    final l10n = AppLocalizations.of(context)!;

    final saveMutation = useMutation<void>(
      onSuccess: (_) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Prompt Block saved (Optimistic).')),
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
        title: const Text('Edit Prompt Block'),
        actions: [
          if (widget.promptBlock['id']?.toString().isNotEmpty == true)
            IconButton(
              onPressed: () => _deletePromptBlock(context, deleteMutation),
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
              _editablePromptBlock['id'] = id;

              _editablePromptBlock.remove('criteria');

              if (_editablePromptBlock['theory_grounding'] == null) {
                _editablePromptBlock.remove('theory_grounding');
              }
              await ref
                  .read(promptBlocksControllerProvider.notifier)
                  .savePromptBlock(id, _editablePromptBlock);
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
                      DropdownButtonFormField<PromptBlockCategory>(
                        decoration: const InputDecoration(
                          labelText: 'Category',
                        ),
                        initialValue: PromptBlockCategory.fromId(
                          _editablePromptBlock['category_id'] as String? ??
                              'system_rule',
                        ),
                        items:
                            PromptBlockCategory.values.map((category) {
                              return DropdownMenuItem(
                                value: category,
                                child: Text(category.displayName),
                              );
                            }).toList(),
                        onChanged: (val) {
                          if (val != null) {
                            setState(
                              () =>
                                  _editablePromptBlock['category_id'] = val.id,
                            );
                          }
                        },
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

                      // Description (I18N) - Short UI Hint
                      I18nTextField(
                        label: 'Short Description (UI Hint)',
                        initialData: SafeCast.safeMap(
                          _editablePromptBlock['description'],
                        ),
                        onChanged:
                            (val) => _editablePromptBlock['description'] = val,
                      ),
                      const SizedBox(height: 16),

                      // AI Description - Core LLM Prompt (English Only)
                      TextFormField(
                        initialValue:
                            _editablePromptBlock['ai_description']?.toString(),
                        decoration: const InputDecoration(
                          labelText:
                              'System Prompt / Cognitive Blueprint (MANDATORY ENGLISH)',
                          border: OutlineInputBorder(),
                        ),
                        maxLines: 8,
                        onChanged: (val) {
                          _editablePromptBlock['ai_description'] = val;
                        },
                      ),
                      Padding(
                        padding: const EdgeInsets.only(top: 8.0),
                        child: Text(
                          l10n.adminAiDescriptionHint,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.only(top: 4.0),
                        child: Text(
                          l10n.adminPromptBestPracticesHint,
                          style: const TextStyle(
                            color: Colors.blueGrey,
                            fontSize: 13,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
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
                                            'number',
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
                                      value: 'number',
                                      child: Text('Number (Numeric)'),
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
                              ],
                            ),
                            const SizedBox(height: 16),
                            const Text(
                              'XAI Output Extensions (Proaktiivinen Valmentaja & Report Fields)',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 8),
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children:
                                  {
                                    "justification": "Justification",
                                    "coaching": "Coaching Tip",
                                    "falsification": "Devil's Advocate",
                                    "missing_context": "Missing Context",
                                    "risk_flag": "Risk Flag",
                                    "remediation_steps": "Remediation",
                                    "emotional_sentiment": "Sentiment",
                                    "theory_link": "Theory Link",
                                    "confidence": "AI Confidence",
                                    "citation": "Source Citation",
                                  }.entries.map((entry) {
                                    final extList =
                                        SafeCast.safeList(
                                          _editablePromptBlock['output_extensions'],
                                        ).map((e) => e.toString()).toList();
                                    final isSelected = extList.contains(
                                      entry.key,
                                    );
                                    return FilterChip(
                                      label: Text(entry.value),
                                      selected: isSelected,
                                      onSelected: (bool selected) {
                                        setState(() {
                                          if (selected) {
                                            extList.add(entry.key);
                                          } else {
                                            extList.remove(entry.key);
                                          }
                                          _editablePromptBlock['output_extensions'] =
                                              extList;
                                          // Cleanup deprecated field just in case
                                          _editablePromptBlock.remove(
                                            'require_justification',
                                          );
                                        });
                                      },
                                      selectedColor:
                                          Theme.of(
                                            context,
                                          ).colorScheme.primaryContainer,
                                      checkmarkColor:
                                          Theme.of(
                                            context,
                                          ).colorScheme.onPrimaryContainer,
                                    );
                                  }).toList(),
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
                          final bool isRow = key == 'rows';
                          final initialMap =
                              isRow
                                  ? {
                                    'label': {
                                      'default_locale': 'en',
                                      'translations': <String, dynamic>{
                                        'en': '',
                                      },
                                    },
                                    'ai_description': 'CRITICAL MANDATE: ',
                                  }
                                  : {
                                    'default_locale': 'en',
                                    'translations': <String, dynamic>{'en': ''},
                                  };

                          final result = await showDialog<Map<String, dynamic>>(
                            context: context,
                            builder:
                                (ctx) => RowEditorModal(
                                  initialRow: initialMap,
                                  title: 'Add $title Item',
                                  isMatrixRow: isRow,
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
                final bool isRow = key == 'rows';

                // If it's a MatrixRow, the text to display in the ListTile is under item['label']
                final displayItem =
                    isRow ? SafeCast.safeMap(item['label']) : item;

                return Card(
                  margin: const EdgeInsets.only(bottom: 8.0),
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  child: ListTile(
                    title: Text(
                      displayItem['translations']?[displayItem['default_locale']] ??
                          displayItem['default_locale'] ??
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
                              isMatrixRow: isRow,
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
                                    'name': {
                                      'default_locale': 'en',
                                      'translations': <String, dynamic>{
                                        'en': '',
                                      },
                                    },
                                    'claims': [
                                      {
                                        'default_locale': 'en',
                                        'translations': <String, dynamic>{
                                          'en': '',
                                        },
                                      },
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
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      initialValue:
                          _editablePromptBlock['scale_min']?.toString() ?? '4',
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                        signed: true,
                      ),
                      decoration: const InputDecoration(
                        labelText: 'Scale Min (e.g. 4)',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (val) {
                        final parsed = num.tryParse(val);
                        if (parsed != null) {
                          setState(() {
                            _editablePromptBlock['scale_min'] = parsed;
                          });
                        }
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: TextFormField(
                      initialValue:
                          _editablePromptBlock['scale_max']?.toString() ?? '10',
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                        signed: true,
                      ),
                      decoration: const InputDecoration(
                        labelText: 'Scale Max (e.g. 10)',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (val) {
                        final parsed = num.tryParse(val);
                        if (parsed != null) {
                          setState(() {
                            _editablePromptBlock['scale_max'] = parsed;
                          });
                        }
                      },
                    ),
                  ),
                ],
              ),
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
