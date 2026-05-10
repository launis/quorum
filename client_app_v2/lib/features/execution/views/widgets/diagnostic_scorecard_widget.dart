import 'package:flutter/material.dart';

import 'package:client_app/features/execution/views/widgets/atom_matrix_table_widget.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';

/// The master entrypoint component for the Diagnostic Scorecard UI.
class DiagnosticScorecardWidget extends StatelessWidget {
  final List<MatrixScorecardRowDto> evaluativeMatrices;
  final List<MatrixScorecardRowDto> informationalMatrices;
  final List<String> visibleColumns;

  const DiagnosticScorecardWidget({
    super.key,
    required this.evaluativeMatrices,
    required this.informationalMatrices,
    required this.visibleColumns,
  });

  @override
  Widget build(BuildContext context) {
    if (visibleColumns.isEmpty) {
      return const SizedBox(); // Matrix skipped if visibleColumns is empty
    }
    if (evaluativeMatrices.isEmpty && informationalMatrices.isEmpty) {
      return const SizedBox(); // Scorecard not applicable
    }

    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          AtomMatrixTableWidget(
            matrices: [...evaluativeMatrices, ...informationalMatrices],
            visibleColumns: visibleColumns,
          ),
        ],
      ),
    );
  }
}
