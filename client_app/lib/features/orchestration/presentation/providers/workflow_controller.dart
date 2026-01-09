import 'package:client_app/features/orchestration/data/repositories/workflow_repository.dart';
import 'package:client_app/features/orchestration/domain/models/workflow.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'workflow_controller.g.dart';

@riverpod
Future<List<Workflow>> workflowList(Ref ref) {
  final repository = ref.watch(workflowRepositoryProvider);

  return repository
      .fetchWorkflows()
      .match(
        (error) => throw error, // Let AsyncValue handle the error
        (workflows) => workflows,
      )
      .run();
}
