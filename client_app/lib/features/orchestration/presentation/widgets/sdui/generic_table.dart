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
