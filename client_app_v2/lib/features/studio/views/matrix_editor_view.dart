import 'package:flutter/material.dart';
import 'package:client_app/features/studio/views/prompt_block_builder_view.dart';

/// Flat MVC wrapper specific for editing matrices.
/// Enforces the matrix category and float evaluation type for new matrices.
class MatrixEditorView extends StatelessWidget {
  final String? id;
  final Map<String, dynamic>? initialData;

  const MatrixEditorView({super.key, this.id, this.initialData});

  @override
  Widget build(BuildContext context) {
    if (id == 'new' || id == null || id!.isEmpty) {
      return const PromptBlockBuilderView(
        id: 'new',
        slug: 'create-matrix',
        initialData: {
          'category_id': 'matrix',
          'type': 'float',
          'label': {
            'default_locale': 'en',
            'translations': <String, dynamic>{'en': ''},
          },
          'description': {
            'default_locale': 'en',
            'translations': <String, dynamic>{'en': ''},
          },
        },
      );
    }
    return PromptBlockBuilderView(
      id: id,
      slug: 'edit-matrix',
      initialData: initialData,
    );
  }
}
