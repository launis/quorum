// ignore_for_file: deprecated_member_use
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
    final formKey = useMemoized(() => GlobalKey<FormState>());
    final idController = useTextEditingController();
    final nameController = useTextEditingController();
    final descController = useTextEditingController();
    final minScaleController = useTextEditingController(text: '1');
    final maxScaleController = useTextEditingController(text: '5');

    // Add Handler
    Future<void> addDimension() async {
      if (!formKey.currentState!.validate()) return;

      // Auto-generate ID from Name (Slugify)
      final generatedId = nameController.text.trim().toLowerCase().replaceAll(RegExp(r'\s+'), '_');

      final dim = OntologyDimension(
        id: generatedId,
        name: nameController.text.trim(),
        description: descController.text.trim(),
        scale: {
          'min': int.parse(minScaleController.text),
          'max': int.parse(maxScaleController.text),
        },
      );

      await ref.read(ontologyControllerProvider.notifier).addDimension(dim);

      // Clear
      idController.clear();
      nameController.clear();
      descController.clear();
      minScaleController.text = '1';
      maxScaleController.text = '5';
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

          // Add Form
          ExpansionTile(
            title: const Text("New Dimension"),
            children: [
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Form(
                  key: formKey,
                  child: Column(
                    children: [
                      // ID is now auto-generated from Name to enforce consistency
                      // TextFormField(controller: idController, ...),
                      const SizedBox(height: 8),
                      TextFormField(
                        controller: nameController,
                        decoration: const InputDecoration(
                          labelText: 'Name (e.g. "Reasoning")',
                          isDense: true,
                          border: OutlineInputBorder(),
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
                        decoration: const InputDecoration(
                          labelText: 'Description',
                          isDense: true,
                          border: OutlineInputBorder(),
                        ),
                        maxLines: 2,
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: TextFormField(
                              controller: minScaleController,
                              decoration: const InputDecoration(
                                labelText: 'Min',
                                isDense: true,
                                border: OutlineInputBorder(),
                              ),
                              keyboardType: TextInputType.number,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: TextFormField(
                              controller: maxScaleController,
                              decoration: const InputDecoration(
                                labelText: 'Max',
                                isDense: true,
                                border: OutlineInputBorder(),
                              ),
                              keyboardType: TextInputType.number,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: FilledButton.icon(
                          onPressed: addDimension,
                          icon: const Icon(Icons.add),
                          label: const Text("Register Dimension"),
                        ),
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
                    return ListTile(
                      title: Text(item.name),
                      subtitle: Text(
                        "${item.id} • ${item.scale['min']}-${item.scale['max']}",
                      ),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete, size: 20),
                        color: Theme.of(context).colorScheme.error,
                        onPressed: () {
                          ref
                              .read(ontologyControllerProvider.notifier)
                              .removeDimension(item.id);
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
