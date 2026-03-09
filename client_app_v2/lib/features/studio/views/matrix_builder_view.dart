import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';

/// **Universal Matrix Builder**
///
/// CRUD interface for editing evaluation matrices adhering strictly to the
/// De-Generator policy (`Map<String, dynamic>`).
///
/// Integrates XAI (Explainable AI) controls directly into criteria definitions
/// and provides a global "Strictness/Kireys" calibration slider.
class MatrixBuilderView extends ConsumerStatefulWidget {
  final Map<String, dynamic> matrix;

  const MatrixBuilderView({super.key, required this.matrix});

  @override
  ConsumerState<MatrixBuilderView> createState() => _MatrixBuilderViewState();
}

class _MatrixBuilderViewState extends ConsumerState<MatrixBuilderView> {
  late Map<String, dynamic> _editableMatrix;
  late TextEditingController _idController;
  late double _strictnessLevel;

  @override
  void initState() {
    super.initState();
    // Deepish copy for isolated editing
    _editableMatrix = Map<String, dynamic>.from(widget.matrix);

    _idController = TextEditingController(
      text: SafeCast.safeString(_editableMatrix['id']),
    );

    // Parse strictness level, defaulting to 50 if missing
    _strictnessLevel =
        _editableMatrix['strictness_level'] != null
            ? SafeCast.safeDouble(_editableMatrix['strictness_level'])
            : 50.0;

    if (!_editableMatrix.containsKey('criteria')) {
      _editableMatrix['criteria'] = [];
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

    _editableMatrix['id'] = id;
    _editableMatrix['strictness_level'] = _strictnessLevel.round();

    ref
        .read(promptBlocksControllerProvider.notifier)
        .savePromptBlock(id, _editableMatrix)
        .then((_) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Matrix saved (Optimistic update applied).'),
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

  void _addCriterion() {
    setState(() {
      final criteria = SafeCast.safeList(_editableMatrix['criteria']);
      criteria.add({
        'slug': 'new_criterion_${criteria.length}',
        'name': {'default_locale': 'Uusi Kriteeri'},
        'description': {'default_locale': 'Kuvaus...'},
        'type': 'int',
        'allow_decimals': false,
        'require_justification': true,
        'theory_url': '',
        'citation_tag': '',
      });
      _editableMatrix['criteria'] = criteria;
    });
  }

  void _removeCriterion(int index) {
    setState(() {
      final criteria = SafeCast.safeList(_editableMatrix['criteria']);
      criteria.removeAt(index);
    });
  }

  @override
  Widget build(BuildContext context) {
    final criteria = SafeCast.safeList(_editableMatrix['criteria']);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Matrix'),
        actions: [
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
                        'Matrix Configuration',
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
                            widget.matrix['id'] == null ||
                            widget.matrix['id'].toString().isEmpty,
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

              // Criteria Editor
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Evaluation Criteria',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  OutlinedButton.icon(
                    onPressed: _addCriterion,
                    icon: const Icon(Icons.add),
                    label: const Text('Add Row'),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              ...criteria.asMap().entries.map((entry) {
                final int index = entry.key;
                final Map<String, dynamic> criterion = SafeCast.safeMap(
                  entry.value,
                );

                return _buildCriterionCard(index, criterion);
              }),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCriterionCard(int index, Map<String, dynamic> criterion) {
    final slugController = TextEditingController(
      text: SafeCast.safeString(criterion['slug']),
    );
    final theoryUrlController = TextEditingController(
      text: SafeCast.safeString(criterion['theory_url']),
    );
    final citationController = TextEditingController(
      text: SafeCast.safeString(criterion['citation_tag']),
    );

    return Card(
      margin: const EdgeInsets.only(bottom: 16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Row ${index + 1}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () => _removeCriterion(index),
                ),
              ],
            ),
            const Divider(),

            // Slug
            Focus(
              onFocusChange: (hasFocus) {
                if (!hasFocus) {
                  criterion['slug'] = slugController.text;
                }
              },
              child: TextField(
                controller: slugController,
                decoration: const InputDecoration(
                  labelText: 'Slug (e.g., readability_score)',
                  border: UnderlineInputBorder(),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Names (I18N)
            I18nTextField(
              label: 'Criterion Name',
              initialData: SafeCast.safeMap(criterion['name']),
              onChanged: (val) => criterion['name'] = val,
            ),
            const SizedBox(height: 16),

            // Description (I18N)
            I18nTextField(
              label: 'Detailed Instructions/Rubric',
              initialData: SafeCast.safeMap(criterion['description']),
              onChanged: (val) => criterion['description'] = val,
            ),
            const SizedBox(height: 16),

            // XAI & Data Type Config
            Container(
              padding: const EdgeInsets.all(12),
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'XAI & Constraints',
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
                            const [
                                  'int',
                                  'float',
                                  'string',
                                ].contains(criterion['type'])
                                ? criterion['type'] as String
                                : 'int',
                        items: const [
                          DropdownMenuItem(
                            value: 'int',
                            child: Text('Integer'),
                          ),
                          DropdownMenuItem(
                            value: 'float',
                            child: Text('Float'),
                          ),
                          DropdownMenuItem(
                            value: 'string',
                            child: Text('String'),
                          ),
                        ],
                        onChanged:
                            (val) => setState(() => criterion['type'] = val),
                      ),
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Checkbox(
                            value: criterion['allow_decimals'] == true,
                            onChanged:
                                (val) => setState(
                                  () => criterion['allow_decimals'] = val,
                                ),
                          ),
                          const Text('Allow Decimals'),
                        ],
                      ),
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Checkbox(
                            value: criterion['require_justification'] == true,
                            onChanged:
                                (val) => setState(
                                  () =>
                                      criterion['require_justification'] = val,
                                ),
                          ),
                          const Text('Require AI Justification'),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Theory References
                  Focus(
                    onFocusChange: (hasFocus) {
                      if (!hasFocus)
                        criterion['theory_url'] = theoryUrlController.text;
                    },
                    child: TextField(
                      controller: theoryUrlController,
                      decoration: const InputDecoration(
                        labelText: 'Theory Source URL',
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Focus(
                    onFocusChange: (hasFocus) {
                      if (!hasFocus)
                        criterion['citation_tag'] = citationController.text;
                    },
                    child: TextField(
                      controller: citationController,
                      decoration: const InputDecoration(
                        labelText: 'Citation Tag (e.g., Bloom 1956, §2)',
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
