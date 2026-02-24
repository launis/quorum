import 'dart:convert';

import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/features/studio/presentation/providers/components_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class ComponentsManagerPanel extends HookConsumerWidget {
  const ComponentsManagerPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 1. State
    final componentsState = ref.watch(componentsControllerProvider);
    final selectedId = useState<String?>(null);
    final searchController = useTextEditingController();

    // Derived List (Filtered)
    final filteredComponents = useMemoized(() {
      final list = componentsState.value ?? [];
      final query = searchController.text.toLowerCase();
      
      if (query.isEmpty) return list;
      return list.where((c) =>
        c.id.toLowerCase().contains(query) ||
        (c.name ?? c.slug ?? '').toLowerCase().contains(query) ||
        (c.slug?.toLowerCase().contains(query) ?? false) ||
        c.type.toLowerCase().contains(query)
      ).toList();
    }, [componentsState.value, searchController.text]);

    useListenable(searchController);

    // 2. Layout
    return Row(
      children: [
        // MASTER (List)
        Expanded(
          flex: 2,
          child: Card(
            margin: const EdgeInsets.all(8),
            elevation: 0,
            shape: RoundedRectangleBorder(
              side: BorderSide(color: Theme.of(context).colorScheme.outlineVariant),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              children: [
                // Toolbar
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: searchController,
                          decoration: const InputDecoration(
                            labelText: "Search Components",
                            prefixIcon: Icon(Icons.search),
                            isDense: true,
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(Icons.add),
                         style: IconButton.styleFrom(
                          backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                          foregroundColor: Theme.of(context).colorScheme.onPrimaryContainer,
                        ),
                        onPressed: () => selectedId.value = 'new',
                        tooltip: "Create New Component",
                      ),
                    ],
                  ),
                ),
                const Divider(height: 1),
                
                // List
                Expanded(
                  child: componentsState.isLoading && !componentsState.hasValue
                  ? const Center(child: CircularProgressIndicator())
                  : componentsState.hasError
                    ? Center(child: Text('Error: ${componentsState.error}'))
                    : filteredComponents.isEmpty 
                      ? const Center(child: Text("No components found."))
                      : ListView.builder(
                        itemCount: filteredComponents.length,
                        itemBuilder: (context, index) {
                          final comp = filteredComponents[index];
                          final isSelected = comp.id == selectedId.value;
                          return ListTile(
                            title: Text(comp.name ?? comp.slug ?? comp.id, style: const TextStyle(fontWeight: FontWeight.w600)),
                            subtitle: Text(comp.type, style: const TextStyle(fontSize: 12)),
                            selected: isSelected,
                            selectedTileColor: Theme.of(context).colorScheme.primaryContainer.withOpacity(0.2),
                            onTap: () => selectedId.value = comp.id,
                            trailing: const Icon(Icons.chevron_right, size: 16),
                          );
                        },
                      ),
                ),
              ],
            ),
          ),
        ),

        // DETAIL (Editor)
        Expanded(
          flex: 5,
          child: Card(
             margin: const EdgeInsets.all(8),
             elevation: 0,
             shape: RoundedRectangleBorder(
              side: BorderSide(color: Theme.of(context).colorScheme.outlineVariant),
              borderRadius: BorderRadius.circular(8),
            ),
            child: selectedId.value == null
              ? const Center(child: Text("Select a component to edit", style: TextStyle(color: Colors.grey)))
              : _ComponentEditor(
                  key: ValueKey(selectedId.value),
                  componentId: selectedId.value!,
                  initialComponent: selectedId.value == 'new' 
                    ? null 
                    : filteredComponents.firstWhere((c) => c.id == selectedId.value, orElse: () => const StudioComponentDef(id: 'err', name: 'err', type: 'err', content: {})),
                  onSave: () => selectedId.value = null,
              ),
          ),
        ),
      ],
    );
  }
}

class _ComponentEditor extends HookConsumerWidget {
  final String componentId;
  final StudioComponentDef? initialComponent;
  final VoidCallback onSave;

  const _ComponentEditor({
    super.key,
    required this.componentId,
    required this.initialComponent,
    required this.onSave,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isNew = componentId == 'new';


    // Controllers
    final idController = useTextEditingController(text: initialComponent?.id ?? '');
    final nameController = useTextEditingController(text: initialComponent?.name ?? '');
    final descController = useTextEditingController(text: initialComponent?.description ?? '');
    final citationController = useTextEditingController(text: initialComponent?.citation ?? '');
    
    // Content handling
    // Try to prettify JSON if map, else raw string
    String initialContentStr = "";
    if (initialComponent != null) {
      if (initialComponent!.content is Map || initialComponent!.content is List) {
         try {
           initialContentStr = const JsonEncoder.withIndent('  ').convert(initialComponent!.content);
         } catch (_) {
           initialContentStr = initialComponent!.content.toString();
         }
      } else {
        initialContentStr = initialComponent!.content.toString();
      }
    }
    final contentController = useTextEditingController(text: initialContentStr);

    final selectedType = useState<String>(initialComponent?.type ?? 'prompt');

    // Types
    final types = ['prompt', 'rule', 'mandate', 'header', 'instruction', 'context', 'evaluation_matrix', 'unknown'];
    // Ensure selected type is in list
    if (!types.contains(selectedType.value)) {
      types.add(selectedType.value);
    }

    Future<void> save() async {
      if (idController.text.isEmpty || nameController.text.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("ID and Name are required.")));
        return;
      }

      // Parse content
      dynamic contentValue = contentController.text;
      // Try to parse as JSON if it looks like JSON
      final text = contentController.text.trim();
      if ((text.startsWith('{') && text.endsWith('}')) || (text.startsWith('[') && text.endsWith(']'))) {
        try {
          contentValue = jsonDecode(text);
        } catch (_) {
          // Keep as string if invalid json
        }
      }

      final newComp = StudioComponentDef(
        id: idController.text,
        name: nameController.text,
        type: selectedType.value,
        description: descController.text,
        citation: citationController.text,
        content: contentValue,
      );

      final controller = ref.read(componentsControllerProvider.notifier);
      try {
        if (isNew) {
          await controller.create(newComp);
        } else {
          await controller.updateComponent(newComp);
        }
        if (context.mounted) {
           ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Component saved!")));
        }
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e"), backgroundColor: Colors.red));
        }
      }
    }

    Future<void> delete() async {
       final confirm = await showDialog<bool>(
            context: context,
            builder: (context) => AlertDialog(
                title: const Text("Confirm Delete"),
                content: Text("Delete component '${idController.text}'?"),
                actions: [
                    TextButton(onPressed: () => Navigator.pop(context, false), child: const Text("Cancel")),
                    FilledButton(
                        style: FilledButton.styleFrom(backgroundColor: Colors.red),
                        onPressed: () => Navigator.pop(context, true), 
                        child: const Text("Delete")
                    ),
                ]
            )
        );

        if (confirm == true) {
            try {
               await ref.read(componentsControllerProvider.notifier).delete(componentId);
               if (context.mounted) {
                   onSave(); // Go back to empty selection
               }
            } catch(e) {
              if (context.mounted) {
                 ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Delete failed: $e"), backgroundColor: Colors.red));
              }
            }
        }
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
           Row(children: [
             Text(isNew ? "Create New Component" : "Edit Component", style: Theme.of(context).textTheme.headlineSmall),
             const Spacer(),
             FilledButton.icon(
               icon: const Icon(Icons.save),
               label: const Text("Save"),
               onPressed: save,
             ),
             if (!isNew) ...[
               const SizedBox(width: 8),
               OutlinedButton.icon(
                 icon: const Icon(Icons.delete, color: Colors.red),
                 label: const Text("Delete", style: TextStyle(color: Colors.red)),
                 onPressed: delete,
               )
             ]
           ]),
           const Divider(),
           const SizedBox(height: 16),

           Row(children: [
             Expanded(
               child: TextField(
                 controller: idController,
                 enabled: isNew,
                 decoration: const InputDecoration(labelText: "ID", border: OutlineInputBorder(), helperText: "Unique identifier"),
               ),
             ),
             const SizedBox(width: 16),
             Expanded(
               child: TextField(
                 controller: nameController,
                 decoration: const InputDecoration(labelText: "Name", border: OutlineInputBorder()),
               ),
             ),
           ]),
           const SizedBox(height: 16),

           Row(children: [
             Expanded(
               child: DropdownButtonFormField<String>(
                 initialValue: types.contains(selectedType.value) ? selectedType.value : types.first,
                 decoration: const InputDecoration(labelText: "Type", border: OutlineInputBorder()),
                 items: types.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                 onChanged: (v) { if(v!=null) selectedType.value = v; },
               ),
             ),
             const SizedBox(width: 16),
             Expanded(
               child: TextField(
                 controller: citationController,
                 decoration: const InputDecoration(labelText: "Citation", border: OutlineInputBorder(), helperText: "Optional reference"),
               ),
             ),
           ]),

           const SizedBox(height: 16),
           TextField(
             controller: descController,
             decoration: const InputDecoration(labelText: "Description", border: OutlineInputBorder()),
           ),

           const SizedBox(height: 16),
           TextField(
             controller: contentController,
             minLines: 5,
             maxLines: 20,
             style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
             decoration: const InputDecoration(
               labelText: "Content", 
               border: OutlineInputBorder(),
               helperText: "String or JSON object",
               alignLabelWithHint: true,
             ),
           ),
        ],
      ),
    );
  }
}
