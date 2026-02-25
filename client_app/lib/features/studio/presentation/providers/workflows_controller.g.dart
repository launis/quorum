// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflows_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(WorkflowsController)
final workflowsControllerProvider = WorkflowsControllerProvider._();

final class WorkflowsControllerProvider
    extends $AsyncNotifierProvider<WorkflowsController, List<WorkflowDef>> {
  WorkflowsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'workflowsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$workflowsControllerHash();

  @$internal
  @override
  WorkflowsController create() => WorkflowsController();
}

String _$workflowsControllerHash() =>
    r'e0dd515dfa9a15537616d9cf40c5e85c9b1d7de6';

abstract class _$WorkflowsController extends $AsyncNotifier<List<WorkflowDef>> {
  FutureOr<List<WorkflowDef>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<List<WorkflowDef>>, List<WorkflowDef>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<WorkflowDef>>, List<WorkflowDef>>,
              AsyncValue<List<WorkflowDef>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
