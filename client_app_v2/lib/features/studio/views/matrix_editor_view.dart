import 'package:flutter/material.dart';
import 'package:client_app/features/studio/views/prompt_block_builder_view.dart';

/// Flat MVC wrapper specific for editing matrices.
/// Enforces the matrix category and float evaluation type for new matrices.
class MatrixEditorView extends StatelessWidget {
  final String? id;

  const MatrixEditorView({super.key, this.id});

  @override
  Widget build(BuildContext context) {
    final normalizedId = id?.trim();
    if (normalizedId == null || normalizedId.isEmpty || normalizedId == 'new') {
      return const PromptBlockBuilderView(id: 'new', slug: 'create-matrix');
    }
    return PromptBlockBuilderView(id: normalizedId, slug: 'edit-matrix');
  }
}
