// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'active_workflow_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(ActiveWorkflowController)
final activeWorkflowControllerProvider = ActiveWorkflowControllerProvider._();

final class ActiveWorkflowControllerProvider
    extends $AsyncNotifierProvider<ActiveWorkflowController, WorkflowDef?> {
  ActiveWorkflowControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'activeWorkflowControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$activeWorkflowControllerHash();

  @$internal
  @override
  ActiveWorkflowController create() => ActiveWorkflowController();
}

String _$activeWorkflowControllerHash() =>
    r'0890f88f3684f59955646156fe78222bf8bab05e';

abstract class _$ActiveWorkflowController extends $AsyncNotifier<WorkflowDef?> {
  FutureOr<WorkflowDef?> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<WorkflowDef?>, WorkflowDef?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<WorkflowDef?>, WorkflowDef?>,
              AsyncValue<WorkflowDef?>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
