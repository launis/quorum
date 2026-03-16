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
  ConsumerState<BlueprintEditorView> createState() => _BlueprintEditorViewState();
}

class _BlueprintEditorViewState extends ConsumerState<BlueprintEditorView> {
  // We use ValueKeys bound to the map instance or a randomly assigned internal ID 
  // to ensure ReorderableListView works smoothly without relying on indices.
  final Map<int, String> _assignedKeys = {};

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(blueprintEditorControllerProvider.notifier).initialize(widget.initialBlueprint);
    });
  }

  String _getKeyForComponent(int index, Map<String, dynamic> comp) {
    if (comp.containsKey('id')) return comp['id'].toString();
    if (!_assignedKeys.containsKey(index)) {
      _assignedKeys[index] = 'comp_${Random().nextInt(100000)}_${DateTime.now().millisecondsSinceEpoch}';
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
            tooltip: 'Clear Form Cache', // Using hardcoded English fallback for now as l10n gen is failing to pick up the key
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
                  onPressed: () => _showAddComponentDialog(context, controller, l10n),
                  icon: const Icon(Icons.add),
                  label: Text(l10n.blueprintAddComponentBtn),
                ),
              ],
            ),
          ),
          Expanded(
            child: components.isEmpty
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
                          title: Text('$type', style: const TextStyle(fontWeight: FontWeight.bold)),
                          subtitle: Text('${l10n.blueprintPropertyDataPath}: ${SafeCast.safeString(comp['data_path'])}'),
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
                              child: _buildComponentEditor(context, comp, (updatedComp) {
                                controller.updateComponent(index, updatedComp);
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

  void _showAddComponentDialog(BuildContext context, BlueprintEditorController controller, AppLocalizations l10n) {
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
                    items: const [
                      DropdownMenuItem(value: '1d_gauge', child: Text('1D Gauge / Metric')),
                      DropdownMenuItem(value: '2d_matrix', child: Text('2D Matrix (Scatter)')),
                      DropdownMenuItem(value: '3d_matrix', child: Text('3D Matrix (XYZ)')),
                      DropdownMenuItem(value: 'evaluation_notes', child: Text('Evaluation Notes')),
                      DropdownMenuItem(value: 'metadata_panel', child: Text('Metadata Panel')),
                      DropdownMenuItem(value: 'bibliography', child: Text('Bibliography')),
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
          }
        );
      }
    );
  }

  Widget _buildComponentEditor(
    BuildContext context, 
    Map<String, dynamic> comp, 
    ValueChanged<Map<String, dynamic>> onChanged,
    AppLocalizations l10n,
  ) {
    final pathCtrl = TextEditingController(text: SafeCast.safeString(comp['data_path']));
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Focus(
          onFocusChange: (f) {
            if (!f) {
              final newComp = Map<String, dynamic>.from(comp);
              newComp['data_path'] = pathCtrl.text;
              onChanged(newComp);
            }
          },
          child: TextField(
            controller: pathCtrl,
            decoration: InputDecoration(
              labelText: l10n.blueprintPropertyDataPath,
              helperText: 'e.g. \$steps.analyst.score',
            ),
          ),
        ),
      ],
    );
  }
}
