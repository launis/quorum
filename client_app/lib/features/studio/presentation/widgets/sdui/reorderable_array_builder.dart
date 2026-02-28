import 'package:client_app/features/studio/domain/models/json_schema.dart';
import 'package:client_app/features/studio/presentation/widgets/sdui/schema_form_builder.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// **ReorderableArrayBuilder**
///
/// Specialized SDUI widget for handling reorderable lists based on JSON Schema.
/// Renders a list of items that can be reordered via drag-and-drop.
class ReorderableArrayBuilder extends ConsumerStatefulWidget {
  final JsonSchema schema;
  final List<dynamic> initialData;
  final ValueChanged<List<dynamic>> onChanged;

  const ReorderableArrayBuilder({
    super.key,
    required this.schema,
    this.initialData = const [],
    required this.onChanged,
    this.customItemBuilder,
    this.onReorder,
    this.itemFactory,
  });

  final Widget Function(BuildContext context, int index, dynamic item)?
  customItemBuilder;
  final void Function(int oldIndex, int newIndex)? onReorder;
  final dynamic Function()? itemFactory;

  @override
  ConsumerState<ReorderableArrayBuilder> createState() =>
      _ReorderableArrayBuilderState();
}

class _ReorderableArrayBuilderState
    extends ConsumerState<ReorderableArrayBuilder> {
  late List<dynamic> _items;

  @override
  void initState() {
    super.initState();
    _items = List.from(widget.initialData);
  }

  @override
  void didUpdateWidget(ReorderableArrayBuilder oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialData != oldWidget.initialData) {
      _items = List.from(widget.initialData);
    }
  }

  void _updateItems() {
    widget.onChanged(_items);
  }

  void _onReorder(int oldIndex, int newIndex) {
    setState(() {
      if (oldIndex < newIndex) {
        newIndex -= 1;
      }
      final item = _items.removeAt(oldIndex);
      _items.insert(newIndex, item);

      if (widget.onReorder != null) {
        widget.onReorder!(oldIndex, newIndex);
      } else {
        _updateItems();
      }
    });
  }

  void _onAddItem() {
    setState(() {
      final newItem =
          widget.itemFactory != null
              ? widget.itemFactory!()
              : _createDefaultValue();
      _items.add(newItem);
      _updateItems();
    });
  }

  void _onRemoveItem(int index) {
    setState(() {
      _items.removeAt(index);
      _updateItems();
    });
  }

  dynamic _createDefaultValue() {
    final itemSchema = widget.schema.items;
    if (itemSchema == null) return null;

    if (itemSchema.type == 'object') {
      return <String, dynamic>{};
    } else if (itemSchema.type == 'string') {
      return '';
    } else if (itemSchema.type == 'number' || itemSchema.type == 'integer') {
      return 0;
    } else if (itemSchema.type == 'boolean') {
      return false;
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final itemSchema = widget.schema.items;
    // If no items schema defined and no custom builder, we can't render much (maybe a warning?)
    if (itemSchema == null && widget.customItemBuilder == null) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text('Error: No "items" definition in array schema.'),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.schema.title != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8.0),
            child: Text(
              widget.schema.title!,
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),
        if (_items.isEmpty)
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text(
              'No items',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          )
        else
          ReorderableListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _items.length,
            onReorder: _onReorder,
            itemBuilder: (context, index) {
              return widget.customItemBuilder?.call(
                    context,
                    index,
                    _items[index],
                  ) ??
                  Card(
                    key: ValueKey('item_$index'), // Simple key strategy
                    margin: const EdgeInsets.only(bottom: 8.0),
                    child: ExpansionTile(
                      key: PageStorageKey('item_$index'), // Persist expansion
                      leading: const Icon(Icons.drag_handle),
                      title: Text('Item ${index + 1}'),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete, color: Colors.red),
                        onPressed: () => _onRemoveItem(index),
                      ),
                      children: [
                        Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: _buildItemContent(index, itemSchema!),
                        ),
                      ],
                    ),
                  );
            },
          ),
        OutlinedButton.icon(
          onPressed: _onAddItem,
          icon: const Icon(Icons.add),
          label: const Text('Add Item'),
        ),
      ],
    );
  }

  Widget _buildItemContent(int index, JsonSchema itemSchema) {
    // 1. Recursive Object
    if (itemSchema.type == 'object') {
      final currentData = _items[index] as Map<String, dynamic>? ?? {};
      return SchemaFormBuilder(
        schema: itemSchema,
        initialData: currentData,
        onChanged: (val) {
          // Verify we aren't rebuilding the whole list on every keystroke in a way that kills focus
          // setState here might be aggressive, but for MVP it works.
          // Ideally we'd update the backing list without full rebuild if possible.
          _items[index] = val;
          _updateItems();
        },
      );
    }

    // 2. Primitives (String, Number, etc)
    // We reuse SchemaFormBuilder logic? No, SchemaFormBuilder renders a whole form (properties).
    // Primitive items are just a single field.
    // We can implement a micro "SchemaFieldBuilder" or just inline logic here.
    return TextFormField(
      initialValue: _items[index].toString(),
      decoration: InputDecoration(
        labelText: itemSchema.title ?? 'Value',
        border: const OutlineInputBorder(),
      ),
      onChanged: (val) {
        if (itemSchema.type == 'number') {
          _items[index] = num.tryParse(val) ?? 0;
        } else {
          _items[index] = val;
        }
        _updateItems();
      },
    );
  }
}
