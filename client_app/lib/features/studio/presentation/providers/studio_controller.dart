import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'studio_controller.g.dart';

/// **Studio Controller**
///
/// Manages the state and logic for the Cognitive Studio.
@riverpod
class StudioController extends _$StudioController {
  @override
  FutureOr<void> build() {
    // No initialization logic needed for now
  }

  /// Mocks fetching the JSON Schema for a Workflow Definition.
  Future<Map<String, dynamic>> fetchWorkflowSchema() async {
    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));

    return {
      'type': 'object',
      'title': 'Workflow Definition',
      'required': ['id', 'name', 'status'],
      'properties': {
        'id': {
          'type': 'string',
          'title': 'Workflow ID',
          'description': 'Unique identifier (slug)',
        },
        'name': {'type': 'string', 'title': 'Display Name'},
        'description': {
          'type': 'string',
          'title': 'Description',
          'format': 'textarea',
        },
        'version': {
          'type': 'integer',
          'title': 'Version',
          'description': 'Numeric version (1, 2, ...)',
        },
        'status': {
          'type': 'string',
          'title': 'Status',
          'enum': ['draft', 'active', 'deprecated', 'archived'],
        },
        'is_public': {
          'type': 'boolean',
          'title': 'Publicly Available',
          'description': 'If checked, visible to all tenants.',
        },
      },
    };
  }

  /// Saves the workflow data.
  Future<void> saveWorkflow(Map<String, dynamic> data) async {
    state = const AsyncValue.loading();
    try {
      // Simulate network delay
      await Future.delayed(const Duration(seconds: 1));

      // Log for verification (Mock persistence)
      // ignore: avoid_print
      print('Saving Workflow: $data');

      state = const AsyncValue.data(null);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }
}
