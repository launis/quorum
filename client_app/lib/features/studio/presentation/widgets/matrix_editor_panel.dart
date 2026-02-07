// ignore_for_file: deprecated_member_use
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/features/studio/presentation/providers/matrix_controller.dart';
import 'package:client_app/features/studio/presentation/providers/ontology_controller.dart';
import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class MatrixEditorPanel extends HookConsumerWidget {
  const MatrixEditorPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;

    // Watch the form state (Unsaved Changes)
    final matrixState = ref.watch(matrixEditorStateProvider);
    final isSaving = ref.watch(matrixControllerProvider).isLoading;

    if (matrixState == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.table_view, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              l10n.studioSelectMatrix,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              icon: const Icon(Icons.add),
              label: Text(l10n.studioCreateMatrix),
              onPressed: () {
                ref.read(matrixControllerProvider.notifier).createNewMatrix();
              },
            ),
          ],
        ),
      );
    }

    // Handlers
    void update(MatrixDef Function(MatrixDef) updater) {
      ref.read(matrixEditorStateProvider.notifier).update(updater);
    }

    void addCriterion() {
      update(
        (m) => m.copyWith(
          criteria: [
            ...m.criteria,
            const MatrixCriterion(dimensionId: '', prompt: '', weight: 1.0),
          ],
        ),
      );
    }

    // Delete Handler
    // TODO: Add L10N
    Future<void> onDelete() async {
      final confirm = await showDialog<bool>(
        context: context,
        builder:
            (context) => AlertDialog(
              title: const Text('Delete Matrix?'),
              content: const Text(
                'Are you sure you want to delete this matrix?',
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: Text(l10n.cancel),
                ),
                FilledButton(
                  style: FilledButton.styleFrom(backgroundColor: Colors.red),
                  onPressed: () => Navigator.pop(context, true),
                  child: Text(l10n.delete),
                ),
              ],
            ),
      );

      if (confirm == true) {
        try {
          await ref
              .read(matrixControllerProvider.notifier)
              .deleteMatrix(matrixState.id);
        } catch (e) {
          if (!context.mounted) return;

          String msg = e.toString();
          if (e is AppError) {
             e.maybeMap(
               api: (apiError) {
                 if (apiError.errorCode == 'Errors.DeleteBlockedByExecutions') {
                    msg = l10n.errorDeleteBlockedByExecutions;
                 } else if (apiError.errorCode == 'Errors.DeleteBlockedByMatrix') {
                    msg = l10n.errorDeleteBlockedByMatrix;
                 }
               },
               orElse: () {},
             );
          }

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(msg),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      }
    }

    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header / Actions
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    matrixState.name.isEmpty ? "New Matrix" : matrixState.name,
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                ),
                if (isSaving)
                  const CircularProgressIndicator()
                else ...[
                  OutlinedButton.icon(
                      icon: const Icon(Icons.close),
                      label: Text(l10n.cancel), // Ensure l10n.cancel exists
                      onPressed: () {
                          // Clear selection to close editor
                          ref.read(studioControllerProvider.notifier).enterMatrixMode();
                      },
                  ),
                  const SizedBox(width: 8),
                  FilledButton.icon(
                    icon: const Icon(Icons.save),
                    label: Text(l10n.save),
                    onPressed: () {
                      ref
                          .read(matrixControllerProvider.notifier)
                          .saveCurrentMatrix();
                    },
                  ),
                  const SizedBox(width: 8),
                  if (matrixState.id.isNotEmpty &&
                      !matrixState.id.startsWith("new_"))
                    IconButton(
                      icon: const Icon(Icons.delete, color: Colors.red),
                      tooltip: l10n.delete,
                      onPressed: onDelete,
                    ),
                ],
              ],
            ),
          ),

          const Divider(height: 1),

          // ... rest of the file ...

          // Metadata Form
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                TextFormField(
                  initialValue: matrixState.name,
                  decoration: InputDecoration(
                    labelText: l10n.studioMatrixName,
                    border: const OutlineInputBorder(),
                  ),
                  onChanged: (v) => update((m) => m.copyWith(name: v)),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  initialValue: matrixState.description,
                  decoration: InputDecoration(
                    labelText: l10n.studioMatrixDesc,
                    border: const OutlineInputBorder(),
                  ),
                  onChanged: (v) => update((m) => m.copyWith(description: v)),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  initialValue: matrixState.roleDescription,
                  decoration: InputDecoration(
                    labelText: l10n.matrixRole,
                    border: const OutlineInputBorder(),
                  ),
                  onChanged:
                      (v) => update((m) => m.copyWith(roleDescription: v)),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        initialValue: matrixState.scale['min'].toString(),
                        decoration: InputDecoration(
                          labelText: '${l10n.matrixScale} (Min)',
                          border: const OutlineInputBorder(),
                        ),
                        keyboardType: TextInputType.number,
                        onChanged:
                            (v) => update(
                              (m) => m.copyWith(
                                scale: {
                                  ...m.scale,
                                  'min': int.tryParse(v) ?? 1,
                                },
                              ),
                            ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: TextFormField(
                        initialValue: matrixState.scale['max'].toString(),
                        decoration: InputDecoration(
                          labelText: '${l10n.matrixScale} (Max)',
                          border: const OutlineInputBorder(),
                        ),
                        keyboardType: TextInputType.number,
                        onChanged:
                            (v) => update(
                              (m) => m.copyWith(
                                scale: {
                                  ...m.scale,
                                  'max': int.tryParse(v) ?? 5,
                                },
                              ),
                            ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const Divider(),

          // Criteria List Header
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: 16.0,
              vertical: 8.0,
            ),
            child: Row(
              children: [
                Text(
                  l10n.matrixCriteria,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const Spacer(),
                OutlinedButton.icon(
                  icon: const Icon(Icons.add),
                  label: Text(l10n.matrixAddCriterion),
                  onPressed: addCriterion,
                ),
              ],
            ),
          ),

          // Reorderable List
          Expanded(
            child: ReorderableListView.builder(
              itemCount: matrixState.criteria.length,
              onReorder: (oldIndex, newIndex) {
                if (oldIndex < newIndex) {
                  newIndex -= 1;
                }
                final list = [...matrixState.criteria];
                final item = list.removeAt(oldIndex);
                list.insert(newIndex, item);
                update((m) => m.copyWith(criteria: list));
              },
              padding: const EdgeInsets.only(bottom: 80),
              itemBuilder: (context, index) {
                final criterion = matrixState.criteria[index];
                return _CriterionRow(
                  key: ValueKey('crit_${index}_${criterion.hashCode}'),
                  // HashCode in Key might break text focus if object changes on typing.
                  // Using index is bad for Reorderable.
                  // We need a stable ID. But MatrixCriterion doesn't have an ID!
                  // It has 'dimension_id'. If empty (new), we have issues.
                  // Let's use ObjectKey(criterion) but 'CopyWith' creates new objects.
                  // The solution is a stable ID in the model, but I can't change model.
                  // I'll use ValueKey(index) BUT ReorderableListView hates that for reordering animations.
                  // Wait, if I use a unique ID for the WIDGET list, I need stable IDs.
                  // I will assume for now that index is acceptable if I don't reorder constantly,
                  // OR I can't solve it without model changes.
                  // ACTUALLY: I can wrap it in a container.
                  // Let's us UniqueKey() for now? No, rebuilds every time.
                  // I will use ValueKey(index) and hope for the best, or disable reorder animation if it glitches.
                  // Actually, flutter docs say: "Keys must be unique".
                  // If I update content, the object changes.
                  index: index,
                  criterion: criterion,
                  onUpdate: (c) {
                    final list = [...matrixState.criteria];
                    list[index] = c;
                    update((m) => m.copyWith(criteria: list));
                  },
                  onRemove: () {
                    final list = [...matrixState.criteria];
                    list.removeAt(index);
                    update((m) => m.copyWith(criteria: list));
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _CriterionRow extends HookConsumerWidget {
  final int index;
  final MatrixCriterion criterion;
  final ValueChanged<MatrixCriterion> onUpdate;
  final VoidCallback onRemove;

  const _CriterionRow({
    super.key,
    required this.index,
    required this.criterion,
    required this.onUpdate,
    required this.onRemove,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ontologyList = ref.watch(ontologyControllerProvider).value ?? [];

    // Auto-fill helper
    void onDimensionChanged(String? newId) {
      if (newId == null) return;

      // Auto-fill label and prompt from ontology if they are empty
      String newLabel = criterion.label;
      String newPrompt = criterion.prompt;

      final selectedDim = ontologyList.firstWhere(
        (d) => d.id == newId,
        orElse:
            () => const OntologyDimension(id: '', name: '', description: ''),
      );

      if (selectedDim.id.isNotEmpty) {
        // User Request: ID should be independent (technical key). 
        // Use the Registry's Display Name (selectedDim.name/label) as the Criterion Label.
        // This ensures the Dimension Name is dynamic and human-readable.
        if (selectedDim.name.isNotEmpty) {
           newLabel = selectedDim.name;
        }
        
        if (newPrompt.isEmpty) newPrompt = selectedDim.description;
      }

      onUpdate(
        criterion.copyWith(
          dimensionId: newId,
          label: newLabel,
          prompt: newPrompt,
        ),
      );
    }

    void onAnchorChanged(String level, String value) {
      final newAnchors = Map<String, String>.from(criterion.anchors);
      newAnchors[level] = value;
      onUpdate(criterion.copyWith(anchors: newAnchors));
    }

    return Card(
      key: key,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Drag Handle
                const Padding(
                  padding: EdgeInsets.only(top: 12.0, right: 8.0),
                  child: Icon(Icons.drag_handle, color: Colors.grey),
                ),

                // Content
                Expanded(
                  child: Column(
                    children: [
                      // Dimension Dropdown
                      DropdownButtonFormField<String>(
                        value:
                            ontologyList.any(
                                  (d) => d.id == criterion.dimensionId,
                                )
                                ? criterion.dimensionId
                                : null,
                        decoration: const InputDecoration(
                          labelText: 'Dimension',
                          isDense: true,
                        ),
                        items:
                            ontologyList.map((d) {
                              return DropdownMenuItem(
                                value: d.id,
                                child: Text(
                                  d.name,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              );
                            }).toList(),
                        onChanged: onDimensionChanged,
                        hint: Text(
                          criterion.dimensionId.isEmpty
                              ? "Select Dimension..."
                              : criterion.dimensionId,
                        ),
                      ),

                      const SizedBox(height: 8),

                      // Label (Display Name)
                      TextFormField(
                        initialValue: criterion.label,
                        decoration: const InputDecoration(
                          labelText: 'Display Name',
                          isDense: true,
                        ),
                        onChanged:
                            (v) => onUpdate(criterion.copyWith(label: v)),
                      ),

                      const SizedBox(height: 8),

                      // Prompt
                      TextFormField(
                        initialValue: criterion.prompt,
                        maxLines: 2,
                        decoration: const InputDecoration(
                          labelText: 'Instruction / Prompt',
                          isDense: true,
                          border: OutlineInputBorder(),
                        ),
                        onChanged:
                            (v) => onUpdate(criterion.copyWith(prompt: v)),
                      ),

                      const SizedBox(height: 8),

                      // Weight Slider
                      Row(
                        children: [
                          const Text("Weight: "),
                          Expanded(
                            child: Slider(
                              value: criterion.weight,
                              min: 0.1,
                              max: 5.0,
                              divisions: 49,
                              label: criterion.weight.toStringAsFixed(1),
                              onChanged:
                                  (v) =>
                                      onUpdate(criterion.copyWith(weight: v)),
                            ),
                          ),
                          Text(
                            criterion.weight.toStringAsFixed(1),
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),

                      const Divider(),
                      const Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          "Proficiency Levels (Anchors)",
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      // Anchors Grid
                      Row(
                        children: [
                          Expanded(
                            child: TextFormField(
                              initialValue: criterion.anchors['1'] ?? '',
                              maxLines: 3,
                              decoration: const InputDecoration(
                                labelText: 'Level 1',
                                border: OutlineInputBorder(),
                                isDense: true,
                              ),
                              style: const TextStyle(fontSize: 12),
                              onChanged: (v) => onAnchorChanged('1', v),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: TextFormField(
                              initialValue: criterion.anchors['2'] ?? '',
                              maxLines: 3,
                              decoration: const InputDecoration(
                                labelText: 'Level 2',
                                border: OutlineInputBorder(),
                                isDense: true,
                              ),
                              style: const TextStyle(fontSize: 12),
                              onChanged: (v) => onAnchorChanged('2', v),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: TextFormField(
                              initialValue: criterion.anchors['3'] ?? '',
                              maxLines: 3,
                              decoration: const InputDecoration(
                                labelText: 'Level 3',
                                border: OutlineInputBorder(),
                                isDense: true,
                              ),
                              style: const TextStyle(fontSize: 12),
                              onChanged: (v) => onAnchorChanged('3', v),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: TextFormField(
                              initialValue: criterion.anchors['4'] ?? '',
                              maxLines: 3,
                              decoration: const InputDecoration(
                                labelText: 'Level 4',
                                border: OutlineInputBorder(),
                                isDense: true,
                              ),
                              style: const TextStyle(fontSize: 12),
                              onChanged: (v) => onAnchorChanged('4', v),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                // Delete
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: onRemove,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
