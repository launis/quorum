import 'package:flutter/material.dart';

import 'package:client_app/features/execution/views/widgets/atom_matrix_table_widget.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';

/// The master entrypoint component for the Diagnostic Scorecard UI.
class DiagnosticScorecardWidget extends StatelessWidget {
  final List<MatrixScorecardRowDto> axes;
  final List<String> visibleColumns;
  final String executionId;

  const DiagnosticScorecardWidget({
    super.key,
    required this.axes,
    required this.visibleColumns,
    required this.executionId,
  });

  @override
  Widget build(BuildContext context) {
    if (visibleColumns.isEmpty) {
      return const SizedBox(); // Matrix skipped if visibleColumns is empty
    }
    if (axes.isEmpty) {
      return const SizedBox(); // Scorecard not applicable
    }

    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          AtomMatrixTableWidget(
            matrices: axes,
            visibleColumns: visibleColumns,
            executionId: executionId,
          ),
        ],
      ),
    );
  }
}
