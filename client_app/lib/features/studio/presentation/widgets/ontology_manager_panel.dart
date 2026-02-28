// ignore_for_file: deprecated_member_use
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/features/studio/presentation/providers/ontology_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class OntologyManagerPanel extends HookConsumerWidget {
  const OntologyManagerPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final ontologyAsync = ref.watch(ontologyControllerProvider);

    // Form State
    // Form State
    final formKey = useMemoized(() => GlobalKey<FormState>());
    final idController = useTextEditingController();
    final nameController = useTextEditingController();
    final descController = useTextEditingController();

    final editingId = useState<String?>(null);

    final expansionController = useMemoized(() => ExpansionTileController());

    // Populate helper
    void onEdit(OntologyDimension item) {
      editingId.value = item.id;
      nameController.text = item.name;
      descController.text = item.description;
      expansionController.expand();
    }

    void onCancel() {
      editingId.value = null;
      idController.clear();
      nameController.clear();
      descController.clear();
      expansionController.collapse();
    }

    // Save/Add Handler
    Future<void> onSave() async {
      if (!formKey.currentState!.validate()) return;

      final isEditing = editingId.value != null;

      String finalId;
      if (isEditing) {
        finalId = editingId.value!;
      } else {
        // Auto-generate ID from Name (Slugify)
        finalId = nameController.text.trim().toLowerCase().replaceAll(
          RegExp(r'\s+'),
          '_',
        );
      }

      final dim = OntologyDimension(
        id: finalId,
        name: nameController.text.trim(),
        description: descController.text.trim(),
      );

      if (isEditing) {
        await ref
            .read(ontologyControllerProvider.notifier)
            .updateDimension(dim);
      } else {
        await ref.read(ontologyControllerProvider.notifier).addDimension(dim);
      }

      // Clear
      onCancel();
    }

    return Card(
      margin: const EdgeInsets.all(8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              "Ontology Registry",
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          const Divider(height: 1),

          // Add/Edit Form
          ExpansionTile(
            controller: expansionController,
            title: Text(
              editingId.value != null ? l10n.editDimension : l10n.newDimension,
            ),
            children: [
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Form(
                  key: formKey,
                  child: Column(
                    children: [
                      const SizedBox(height: 8),
                      TextFormField(
                        controller: nameController,
                        decoration: InputDecoration(
                          labelText: l10n.ontologyNameLabel,
                          isDense: true,
                          border: const OutlineInputBorder(),
                        ),
                        validator:
                            (v) =>
                                (v == null || v.isEmpty)
                                    ? l10n.fieldRequired
                                    : null,
                      ),
                      const SizedBox(height: 8),
                      TextFormField(
                        controller: descController,
                        decoration: InputDecoration(
                          labelText: l10n.ontologyDescriptionLabel,
                          isDense: true,
                          border: const OutlineInputBorder(),
                        ),
                        maxLines: 2,
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          if (editingId.value != null) ...[
                            Expanded(
                              child: OutlinedButton(
                                onPressed: onCancel,
                                child: Text(l10n.cancel),
                              ),
                            ),
                            const SizedBox(width: 8),
                          ],
                          Expanded(
                            child: FilledButton.icon(
                              onPressed: onSave,
                              icon: Icon(
                                editingId.value != null
                                    ? Icons.save
                                    : Icons.add,
                              ),
                              label: Text(
                                editingId.value != null
                                    ? l10n.update
                                    : l10n.registerDimension,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),

          const Divider(height: 1),

          // List
          Expanded(
            child: ontologyAsync.when(
              data: (list) {
                if (list.isEmpty)
                  return const Center(child: Text("No dimensions defined."));
                return ListView.builder(
                  itemCount: list.length,
                  itemBuilder: (context, index) {
                    final item = list[index];
                    final isSelected = item.id == editingId.value;

                    return ListTile(
                      selected: isSelected,
                      selectedTileColor: Theme.of(
                        context,
                      ).colorScheme.primaryContainer.withOpacity(0.2),
                      title: Text(item.name),
                      subtitle:
                          item.description.isNotEmpty
                              ? Text(
                                item.description,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              )
                              : null,
                      onTap: () => onEdit(item),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete, size: 20),
                        color: Theme.of(context).colorScheme.error,
                        onPressed: () async {
                          try {
                            await ref
                                .read(ontologyControllerProvider.notifier)
                                .removeDimension(item.id);

                            // If we deleted the one we are editing, cancel edit
                            if (editingId.value == item.id) {
                              onCancel();
                            }
                          } catch (e) {
                            if (!context.mounted) return;

                            String msg = e.toString();
                            if (e is AppError) {
                              e.maybeMap(
                                api: (apiError) {
                                  if (apiError.errorCode ==
                                      'Errors.DeleteBlockedByMatrix') {
                                    msg = l10n.errorDeleteBlockedByMatrix;
                                  }
                                },
                                orElse: () {},
                              );
                            }

                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(msg),
                                backgroundColor:
                                    Theme.of(context).colorScheme.error,
                              ),
                            );
                          }
                        },
                      ),
                    );
                  },
                );
              },
              error: (err, st) => Center(child: Text('Error: $err')),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ),
        ],
      ),
    );
  }
}
