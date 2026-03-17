import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/blueprint_editor_controller.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// **Blueprint Editor View**
///
/// A dedicated drag-and-drop / dynamic form editor for `render_blueprint`.
/// Enforces Zero-Codegen SDUI architecture by keeping the state as `Map<String, dynamic>`.
class BlueprintEditorView extends ConsumerStatefulWidget {
  final Map<String, dynamic> initialBlueprint;
  final ValueChanged<Map<String, dynamic>> onSave;

  const BlueprintEditorView({
    super.key,
    required this.initialBlueprint,
    required this.onSave,
  });

  @override
  ConsumerState<BlueprintEditorView> createState() =>
      _BlueprintEditorViewState();
}

class _BlueprintEditorViewState extends ConsumerState<BlueprintEditorView> {
  // We use ValueKeys bound to the map instance or a randomly assigned internal ID
  // to ensure ReorderableListView works smoothly without relying on indices.
  final Map<int, String> _assignedKeys = {};

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref
          .read(blueprintEditorControllerProvider.notifier)
          .initialize(widget.initialBlueprint);
    });
  }

  String _getKeyForComponent(int index, Map<String, dynamic> comp) {
    if (comp.containsKey('id')) return comp['id'].toString();
    if (!_assignedKeys.containsKey(index)) {
      _assignedKeys[index] =
          'comp_${Random().nextInt(100000)}_${DateTime.now().millisecondsSinceEpoch}';
    }
    return _assignedKeys[index]!;
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final blueprint = ref.watch(blueprintEditorControllerProvider);
    final controller = ref.read(blueprintEditorControllerProvider.notifier);

    final components = SafeCast.safeList(blueprint['components']);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.blueprintEditorTitle),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_sweep),
            tooltip:
                'Clear Form Cache', // Using hardcoded English fallback for now as l10n gen is failing to pick up the key
            onPressed: () {
              ref.invalidate(blueprintEditorControllerProvider);
              _assignedKeys.clear();
            },
          ),
          const SizedBox(width: 8),
          FilledButton.icon(
            onPressed: () {
              widget.onSave(blueprint);
              Navigator.of(context).pop();
            },
            icon: const Icon(Icons.check),
            label: Text(l10n.save),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.blueprintComponentsTitle,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                ElevatedButton.icon(
                  onPressed:
                      () => _showAddComponentDialog(context, controller, l10n),
                  icon: const Icon(Icons.add),
                  label: Text(l10n.blueprintAddComponentBtn),
                ),
              ],
            ),
          ),
          Expanded(
            child:
                components.isEmpty
                    ? Center(
                      child: Text(
                        l10n.blueprintEmptyStateMsg,
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: Colors.grey,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    )
                    : ReorderableListView.builder(
                      padding: const EdgeInsets.all(16.0),
                      itemCount: components.length,
                      onReorder: (oldIndex, newIndex) {
                        controller.reorderComponent(oldIndex, newIndex);
                        // Update assigned keys layout if reordered
                        _assignedKeys.remove(oldIndex);
                        // Simple fix is to just clear assigned keys and let them regenerate on render,
                        // but it's better to actually swap them to avoid rebuilding state for children.
                        _assignedKeys.clear();
                      },
                      itemBuilder: (context, index) {
                        final comp = SafeCast.safeMap(components[index]);
                        final type = SafeCast.safeString(comp['type']);
                        final uniqueKey = _getKeyForComponent(index, comp);

                        return Card(
                          key: ValueKey(uniqueKey),
                          elevation: 2,
                          margin: const EdgeInsets.only(bottom: 12),
                          child: ExpansionTile(
                            title: Text(
                              '$type',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            subtitle: Builder(
                              builder: (context) {
                                String text = '';
                                if (type == 'grid_row') {
                                  final children = SafeCast.safeList(
                                    comp['children'],
                                  );
                                  final cols = SafeCast.safeInt(
                                    comp['columns'],
                                    2,
                                  );
                                  text =
                                      'Grid Row ($cols saraketta) | Lapsikomponentteja: ${children.length}';
                                } else if (comp.containsKey('data_path')) {
                                  text =
                                      '${l10n.blueprintPropertyDataPath}: ${SafeCast.safeString(comp['data_path'])}';
                                } else if (comp.containsKey('x_data_path')) {
                                  text =
                                      'X: ${SafeCast.safeString(comp['x_data_path'])} | Y: ${SafeCast.safeString(comp['y_data_path'])}';
                                  if (comp.containsKey('z_data_path')) {
                                    text +=
                                        ' | Z: ${SafeCast.safeString(comp['z_data_path'])}';
                                  }
                                } else if (comp.containsKey('title')) {
                                  text =
                                      '${l10n.blueprintPropertyTitle}: ${SafeCast.safeString(comp['title'])}';
                                }

                                if (text.isEmpty) {
                                  return const SizedBox.shrink();
                                }
                                return Text(
                                  text,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                );
                              },
                            ),
                            leading: const Icon(Icons.drag_handle),
                            trailing: IconButton(
                              icon: const Icon(Icons.delete, color: Colors.red),
                              onPressed: () {
                                _assignedKeys.remove(index);
                                controller.removeComponent(index);
                              },
                            ),
                            children: [
                              Padding(
                                padding: const EdgeInsets.all(16.0),
                                child: _buildComponentEditor(context, comp, (
                                  updatedComp,
                                ) {
                                  controller.updateComponent(
                                    index,
                                    updatedComp,
                                  );
                                }, l10n),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
          ),
        ],
      ),
    );
  }

  void _showAddComponentDialog(
    BuildContext context,
    BlueprintEditorController controller,
    AppLocalizations l10n,
  ) {
    String selectedType = '1d_gauge';

    showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: Text(l10n.blueprintAddComponentBtn),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  DropdownButtonFormField<String>(
                    initialValue: selectedType,
                    decoration: const InputDecoration(labelText: 'Type'),
                    items: [
                      DropdownMenuItem(
                        value: '1d_gauge',
                        child: Text(l10n.blueprintComponent1dGauge),
                      ),
                      DropdownMenuItem(
                        value: '2d_matrix',
                        child: Text(l10n.blueprintComponent2dMatrix),
                      ),
                      DropdownMenuItem(
                        value: '3d_scatter',
                        child: Text(l10n.blueprintComponent3dScatter),
                      ),
                      DropdownMenuItem(
                        value: 'evaluation_notes_panel',
                        child: Text(l10n.blueprintComponentEvaluationNotes),
                      ),
                      DropdownMenuItem(
                        value: 'header',
                        child: Text(l10n.blueprintComponentHeader),
                      ),
                      DropdownMenuItem(
                        value: 'metadata_header',
                        child: Text(l10n.blueprintComponentMetadataHeader),
                      ),
                      const DropdownMenuItem(
                        value: 'grid_row',
                        child: Text('Grid Row (Rinnakkainen)'),
                      ),
                      DropdownMenuItem(
                        value: 'bibliography_footer',
                        child: Text(l10n.blueprintComponentBibliography),
                      ),
                    ],
                    onChanged: (val) {
                      if (val != null) setState(() => selectedType = val);
                    },
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(ctx).pop(),
                  child: Text(l10n.cancel),
                ),
                FilledButton(
                  onPressed: () {
                    controller.addComponent(selectedType);
                    Navigator.of(ctx).pop();
                  },
                  child: Text(l10n.save),
                ),
              ],
            );
          },
        );
      },
    );
  }

  void _showAddChildDialog(
    BuildContext context,
    Map<String, dynamic> comp,
    List<Map<String, dynamic>> children,
    ValueChanged<Map<String, dynamic>> onChanged,
    AppLocalizations l10n,
  ) {
    String selectedType = '1d_gauge';

    showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: const Text('Lisää lapsikomponentti'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  DropdownButtonFormField<String>(
                    initialValue: selectedType,
                    decoration: const InputDecoration(labelText: 'Type'),
                    items: [
                      DropdownMenuItem(
                        value: '1d_gauge',
                        child: Text(l10n.blueprintComponent1dGauge),
                      ),
                      DropdownMenuItem(
                        value: '2d_matrix',
                        child: Text(l10n.blueprintComponent2dMatrix),
                      ),
                      DropdownMenuItem(
                        value: '3d_scatter',
                        child: Text(l10n.blueprintComponent3dScatter),
                      ),
                      DropdownMenuItem(
                        value: 'evaluation_notes_panel',
                        child: Text(l10n.blueprintComponentEvaluationNotes),
                      ),
                      DropdownMenuItem(
                        value: 'header',
                        child: Text(l10n.blueprintComponentHeader),
                      ),
                      DropdownMenuItem(
                        value: 'metadata_header',
                        child: Text(l10n.blueprintComponentMetadataHeader),
                      ),
                    ],
                    onChanged: (val) {
                      if (val != null) setState(() => selectedType = val);
                    },
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(ctx).pop(),
                  child: Text(l10n.cancel),
                ),
                FilledButton(
                  onPressed: () {
                    final newChild = <String, dynamic>{'type': selectedType};
                    if (selectedType == '1d_gauge') {
                      newChild['value'] = 0.0;
                    } else if (selectedType == '2d_matrix' ||
                        selectedType == '3d_scatter') {
                      newChild['x_value'] = 0.0;
                      newChild['y_value'] = 0.0;
                      if (selectedType == '3d_scatter')
                        newChild['z_value'] = 0.0;
                    }

                    final newComp = Map<String, dynamic>.from(comp);
                    final newChildren = List<Map<String, dynamic>>.from(
                      children,
                    );
                    newChildren.add(newChild);
                    newComp['children'] = newChildren;

                    onChanged(newComp);
                    Navigator.of(ctx).pop();
                  },
                  child: Text(l10n.save),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Widget _buildComponentEditor(
    BuildContext context,
    Map<String, dynamic> comp,
    ValueChanged<Map<String, dynamic>> onChanged,
    AppLocalizations l10n,
  ) {
    final type = SafeCast.safeString(comp['type']);

    if (type == 'header') {
      return _buildTextField(
        comp,
        'title',
        l10n.blueprintPropertyTitle,
        onChanged,
      );
    } else if (type == '1d_gauge') {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildTextField(
            comp,
            'data_path',
            l10n.blueprintPropertyDataPath,
            onChanged,
            helper: 'e.g. \$steps.analyst.score',
          ),
          const SizedBox(height: 8),
          _buildTextField(
            comp,
            'title',
            l10n.blueprintPropertyTitle,
            onChanged,
          ),
        ],
      );
    } else if (type == '2d_matrix' || type == '3d_scatter') {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildTextField(
            comp,
            'x_data_path',
            l10n.blueprintPropertyXAxis,
            onChanged,
          ),
          const SizedBox(height: 8),
          _buildTextField(
            comp,
            'y_data_path',
            l10n.blueprintPropertyYAxis,
            onChanged,
          ),
          const SizedBox(height: 8),
          _buildTextField(
            comp,
            'x_axis_note',
            l10n.blueprintPropertyXAxisNote,
            onChanged,
          ),
          const SizedBox(height: 8),
          _buildTextField(
            comp,
            'y_axis_note',
            l10n.blueprintPropertyYAxisNote,
            onChanged,
          ),
          if (type == '3d_scatter') ...[
            const SizedBox(height: 8),
            _buildTextField(
              comp,
              'z_data_path',
              l10n.blueprintPropertyZAxis,
              onChanged,
            ),
          ],
        ],
      );
    } else if (type == 'evaluation_notes_panel') {
      final currentList = SafeCast.safeList(
        comp['data_paths'],
      ).map((e) => e.toString()).join(', ');
      final ctrl = TextEditingController(text: currentList);

      return Focus(
        onFocusChange: (f) {
          if (!f) {
            final newComp = Map<String, dynamic>.from(comp);
            newComp['data_paths'] =
                ctrl.text
                    .split(',')
                    .map((e) => e.trim())
                    .where((e) => e.isNotEmpty)
                    .toList();
            onChanged(newComp);
          }
        },
        child: TextField(
          controller: ctrl,
          decoration: InputDecoration(
            labelText: l10n.blueprintPropertyDataPathsInfo,
          ),
        ),
      );
    } else if (type == 'grid_row') {
      final children = SafeCast.safeList(comp['children']);
      final cols = SafeCast.safeInt(comp['columns'], 2);
      final ctrl = TextEditingController(text: cols.toString());

      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Focus(
            onFocusChange: (f) {
              if (!f) {
                final newComp = Map<String, dynamic>.from(comp);
                newComp['columns'] = int.tryParse(ctrl.text) ?? 2;
                onChanged(newComp);
              }
            },
            child: TextField(
              controller: ctrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Sarakkeiden määrä (Columns)',
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Rinnakkaiset lapsikomponentit (${children.length}):',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          ...children.asMap().entries.map((entry) {
            final childIndex = entry.key;
            final childMap = SafeCast.safeMap(entry.value);
            final childType = SafeCast.safeString(childMap['type']);

            return Card(
              margin: const EdgeInsets.only(bottom: 8.0),
              color: Colors.blueGrey.shade50,
              child: Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '[$childIndex] $childType',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        IconButton(
                          icon: const Icon(
                            Icons.close,
                            color: Colors.red,
                            size: 20,
                          ),
                          onPressed: () {
                            final newComp = Map<String, dynamic>.from(comp);
                            final currentChildrenList = SafeCast.safeList(
                              newComp['children'],
                            );
                            final newChildren = List<Map<String, dynamic>>.from(
                              currentChildrenList.map(
                                (e) => SafeCast.safeMap(e),
                              ),
                            );
                            newChildren.removeAt(childIndex);
                            newComp['children'] = newChildren;
                            onChanged(newComp);
                          },
                        ),
                      ],
                    ),
                    const Divider(),
                    _buildComponentEditor(context, childMap, (updatedChild) {
                      final newComp = Map<String, dynamic>.from(comp);
                      final currentChildrenList = SafeCast.safeList(
                        newComp['children'],
                      );
                      final newChildren = List<Map<String, dynamic>>.from(
                        currentChildrenList.map((e) => SafeCast.safeMap(e)),
                      );
                      newChildren[childIndex] = updatedChild;
                      newComp['children'] = newChildren;
                      onChanged(newComp);
                    }, l10n),
                  ],
                ),
              ),
            );
          }),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            icon: const Icon(Icons.add),
            label: const Text('Lisää lapsikomponentti'),
            onPressed: () {
              final currentChildrenList = SafeCast.safeList(comp['children']);
              final childMapList = List<Map<String, dynamic>>.from(
                currentChildrenList.map((e) => SafeCast.safeMap(e)),
              );
              _showAddChildDialog(context, comp, childMapList, onChanged, l10n);
            },
          ),
        ],
      );
    } else {
      return Center(
        child: Text(
          l10n.noInputsRequired(type),
          style: const TextStyle(fontStyle: FontStyle.italic),
        ),
      );
    }
  }

  Widget _buildTextField(
    Map<String, dynamic> comp,
    String key,
    String label,
    ValueChanged<Map<String, dynamic>> onChanged, {
    String? helper,
  }) {
    final ctrl = TextEditingController(text: SafeCast.safeString(comp[key]));
    return Focus(
      onFocusChange: (f) {
        if (!f) {
          final newComp = Map<String, dynamic>.from(comp);
          final val = ctrl.text.trim();
          if (val.isEmpty) {
            newComp.remove(key);
          } else {
            newComp[key] = val;
          }
          onChanged(newComp);
        }
      },
      child: TextField(
        controller: ctrl,
        decoration: InputDecoration(labelText: label, helperText: helper),
      ),
    );
  }
}
