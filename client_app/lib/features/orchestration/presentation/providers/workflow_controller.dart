import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/orchestration/data/repositories/workflow_repository.dart';
import 'package:client_app/features/orchestration/domain/models/workflow.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'workflow_controller.g.dart';

/// Fetches workflows for the current user.
///
/// **IMPORTANT**: This provider depends on [authControllerProvider] to ensure
/// auth token is available before making API calls. This prevents the
/// race condition where workflows load before authentication is ready.
@riverpod
Future<List<Workflow>> workflowList(Ref ref) async {
  // Wait for auth to be ready - this ensures token is available
  final authUser = await ref.watch(authControllerProvider.future);
  if (authUser == null) {
    // User not authenticated - return empty list
    return [];
  }

  final repository = ref.watch(workflowRepositoryProvider);

  return repository
      .fetchWorkflows()
      .match(
        (error) => throw error, // Let AsyncValue handle the error
        (workflows) => workflows,
      )
      .run();
}

