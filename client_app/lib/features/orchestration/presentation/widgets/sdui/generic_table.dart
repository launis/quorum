import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:flutter/material.dart';

class GenericTable extends StatelessWidget {
  final String title;
  final Map<String, dynamic> data;

  const GenericTable({super.key, required this.title, required this.data});

  @override
  Widget build(BuildContext context) {
    final columns = data['columns'] as List<dynamic>? ?? [];
    final rows = data['rows'] as List<dynamic>? ?? [];

    if (columns.isEmpty) return const SizedBox.shrink();

    // Map column keys to DataTable Columns
    final dataColumns =
        columns.map((col) {
          return DataColumn(
            label: Text(
              col['label'] ?? '',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          );
        }).toList();

    // Map rows to DataTable Rows
    final dataRows =
        rows.map((row) {
          final cells =
              columns.map((col) {
                final key = col['key'];
                final val = row[key]?.toString() ?? '';
                return DataCell(Text(val));
              }).toList();
          return DataRow(cells: cells);
        }).toList();

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: ConstrainedBox(
                constraints: const BoxConstraints(minWidth: 400),
                child: DataTable(
                  columns: dataColumns,
                  rows: dataRows,
                  headingRowHeight: 40,
                  dataRowMinHeight: 30, // Tighter
                  columnSpacing: 24,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class ModelMappingGrid extends StatelessWidget {
  final List<WorkflowStepDef> steps;
  final Map<String, String> currentMapping;
  final ValueChanged<Map<String, String>> onChanged;

  // Hardcoded for Phase 2 Hardening as per context
  static const _availableModels = ['Fast LLM', 'Deep LLM', 'Reasoning LLM'];

  const ModelMappingGrid({
    super.key,
    required this.steps,
    required this.currentMapping,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    if (steps.isEmpty) {
      return const Center(child: Text('No steps to map.'));
    }

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Model Mapping',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
             SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: [
                  const DataColumn(label: Text('Model / Step')),
                  ...steps.map((s) => DataColumn(
                    label: Tooltip(
                      message: s.taskKey,
                      child: Text(s.name.isNotEmpty ? s.name : s.id),
                    ),
                  )),
                ],
                rows: _availableModels.map((model) {
                  return DataRow(
                    cells: [
                      DataCell(Text(model, style: const TextStyle(fontWeight: FontWeight.w600))),
                      ...steps.map((step) {
                        final currentModel = currentMapping[step.id];
                        final isSelected = currentModel == model;
                        
                        return DataCell(
                          Center(
                            child: Checkbox(
                              value: isSelected,
                              onChanged: (val) {
                                if (val == true) {
                                  _updateMapping(step.id, model);
                                } else {
                                  // Optional: Allow deselecting? Or force selection?
                                  // For now, allow deselect (remove key)
                                   _updateMapping(step.id, null);
                                }
                              },
                            ),
                          ),
                        );
                      }),
                    ],
                  );
                }).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _updateMapping(String stepId, String? model) {
    final newMapping = Map<String, String>.from(currentMapping);
    if (model == null) {
      newMapping.remove(stepId);
    } else {
      newMapping[stepId] = model;
    }
    onChanged(newMapping);
  }
}
